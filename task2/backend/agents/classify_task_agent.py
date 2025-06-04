from dotenv import load_dotenv
import os 
import json, re
from pydantic import BaseModel
from langchain.output_parsers import PydanticOutputParser
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_tool_calling_agent, AgentExecutor

# loading the env variables
load_dotenv()

# response that we need from the model
class Response(BaseModel):
    category: str 
    code: int
    reason: str 

# our parser
parser = PydanticOutputParser(pydantic_object=Response)

# out llm model that we will use in this app
anthropic_llm = ChatAnthropic(api_key=os.getenv("ANTROPIC_API_KEY"), model_name="claude-3-5-sonnet-20241022") #type:ignore

# template that is sent to claude
our_prompt = ChatPromptTemplate.from_messages(
    [("system", 
        """
             You are an agent that determines whether a task can be performed by an AI system.

            Return one of the following:
            - doable_by_ai: The task is 100 percent digital and can be completed entirely by an AI agent (e.g., writing an email, researching, summarizing text, scheduling).
            - not_doable_by_ai: The task requires physical action or human presence (e.g., changing oil, cleaning a room, cooking), and thus cannot be completed by an AI alone.

            Task that are doable by ai needs to be completely digital. 
            
            Code is an int
            For doable put it as 0 
            For notdoable put it as 1
            Also include a short reason.
            
            Please provide the response in this format\n{format_instructions}
        """
    ),
    ("placeholder", "{chat_history}"),
    ("human", "{query}"),
    ("placeholder", "{agent_scratchpad}")
    ]
).partial(format_instructions=parser.get_format_instructions())


# out agent that will be our taskmanager 
classifying_agent = create_tool_calling_agent(
    llm=anthropic_llm,
    prompt=our_prompt,
    tools=[]
)

# we are going to execute the agent
agent_executor = AgentExecutor(
    agent=classifying_agent,
    tools=[],
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

async def run_doable_agent(query: str) -> object:
    # now getting the response from the agent using users query
    raw_response = agent_executor.invoke(
            {
                "query": query
            }
        )


    # getting the output that we need
    response = raw_response["output"][0]["text"]

    match = re.search(r"\{[\s\S]*\}", response)
    if match:
        return json.loads(match.group())
    return {"error": "Invalid format"}
