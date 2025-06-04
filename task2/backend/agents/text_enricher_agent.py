from dotenv import load_dotenv
import os 
import json, re
from pydantic import BaseModel
from langchain.output_parsers import PydanticOutputParser
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_tool_calling_agent, AgentExecutor
from .tools import search_tool, get_time_tool, you_search_tool

# loading the env variables
load_dotenv()

# response that we need from the model
class Response(BaseModel):
    taskName: str
    deadline: str
    estimation: str 
    description: str
    status: str  
    importance: str 

# our parser
parser = PydanticOutputParser(pydantic_object=Response)

# out llm model that we will use in this app
anthropic_llm = ChatAnthropic(api_key=os.getenv("ANTROPIC_API_KEY"), model_name="claude-3-5-sonnet-20241022") #type:ignore

# template that is sent to claude
our_prompt = ChatPromptTemplate.from_messages(
    [("system", 
        """
        You are a text fillup agent that will provide missing data that user provided. You must fill up every data. Data are:
        TaskName will be given to you and you will use the search tool to see what other people have encountered doing this task.
        You will also be given a tool to get the current time so that you can estimate the deadline and just add it yourself.
        Use the current_time tool to get the current time and make sure that the deadline that you provide is accurate.
        When searching the internet just see what other people have encountered in similar situations and then make decision based on the output.
        Data you need to fill up if not given or partially given:
        Note: If things were given before dont fill them up just leave them as it is and based on those knowledge fill the missing data.
        Leave Importance empty.
        1) deadline: Deadline should be in this format: YYYY-MM-DDTHH:MM (24-hour format). Example: 2025-05-29T14:30
        2) Estimation: You can say it in hour or mins. Whatever is easy for a human to read. If it is 1 and half hour say 1 hour 30 mins. Dont do 1.5 hours. or dont say 120 mins for 2 hours. 
        3) Description: A nice description for the task dont overdo it. Just concise and to the point.
        4) status: Should be Not Started if the user only provided taskName.
        5) Impotance: Should be left out. Other agent will fill this up. 
        Please provide the response in this format\n{format_instructions}
        """
    ),
    ("placeholder", "{chat_history}"),
    ("human", "{query}"),
    ("placeholder", "{agent_scratchpad}")
    ]
).partial(format_instructions=parser.get_format_instructions())

tools = [get_time_tool, you_search_tool]
# out agent that will be our taskmanager 
text_enricher_agent = create_tool_calling_agent(
    llm=anthropic_llm,
    prompt=our_prompt,
    tools=tools
)

# we are going to execute the agent
agent_executor = AgentExecutor(
    agent=text_enricher_agent,
    tools=tools,
    verbose=True
)

'''
Test
raw_response = agent_executor.invoke
        {
            "query": "TaskName: Change oil in my car"
        }
    )
'''

async def run_text_enricher_agent(task_name: str) -> dict:
    # now getting the response from the agent using users query
    raw_response = agent_executor.invoke(
        {
            "query": task_name
        }
    )
    # getting the output that we need
    string = raw_response["output"][0]["text"]

    match = re.search(r"\{[\s\S]*\}", string)
    if match:
        structured_response = json.loads(match.group())
       
    return structured_response
