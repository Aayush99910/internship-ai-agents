from dotenv import load_dotenv
import os 
import json, re
from pydantic import BaseModel
from langchain.output_parsers import PydanticOutputParser
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_tool_calling_agent, AgentExecutor
from .tools import get_time_tool

# loading the env variables
load_dotenv()

# response that we need from the model
class Response(BaseModel):
    priority: str 
    reason: str 

# our parser
parser = PydanticOutputParser(pydantic_object=Response)

# out llm model that we will use in this app
anthropic_llm = ChatAnthropic(api_key=os.getenv("ANTROPIC_API_KEY"), model_name="claude-3-5-sonnet-20241022") #type:ignore

# template that is sent to claude
our_prompt = ChatPromptTemplate.from_messages(
    [("system", 
        """
        You are a todo manager. 
        You will give priority to various tasks that will be given to you.
        You will be given deadline, task time, taskname, description and progress. 
        Pay attention to deadline you will be given exact hour, minute, day, month and year. You need to check the current time and see how much time is left until that deadline.
        Use the tools provided to get the current time and see how far is the deadline from current time.
        You will judge the task based on these factors. You should return either Low, High or Medium. 
        Input will be in json format or any other format but response should be one priority and then a reason on why that priority.    
        Please provide the response in this format\n{format_instructions}
        """
    ),
    ("placeholder", "{chat_history}"),
    ("human", "{query}"),
    ("placeholder", "{agent_scratchpad}")
    ]
).partial(format_instructions=parser.get_format_instructions())

tools = [get_time_tool]
# out agent that will be our taskmanager 
task_manager_agent = create_tool_calling_agent(
    llm=anthropic_llm,
    prompt=our_prompt,
    tools=tools
)

# we are going to execute the agent
agent_executor = AgentExecutor(
    agent=task_manager_agent,
    tools=tools,
    verbose=True
)

'''
Test
raw_response = agent_executor.invoke(
        {
            "query": 
                TaskName: Change oil in my car
                Deadline: 2025-05-29 05:38 PM
                Estimated_time: 160 mins
                Description: I need to change my oil in my car. 
                Status: not started
        }
    )
'''

async def run_priority_agent(query: str) -> dict:
    # now getting the response from the agent using users query
    raw_response = agent_executor.invoke(
        {
            "query": query
        }
    )

    # getting the output that we need
    string = raw_response["output"][0]["text"]

    match = re.search(r"\{[\s\S]*\}", string)
    if match:
        structured_response = json.loads(match.group())
        return structured_response

    return {"error": "Something went wrong"}