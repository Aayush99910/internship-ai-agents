# custom tools that we can write ourselves
from langchain_community.tools import WikipediaQueryRun, DuckDuckGoSearchRun
from langchain_community.tools.you import YouSearchTool
from langchain_community.utilities.you import YouSearchAPIWrapper
from langchain_community.utilities import WikipediaAPIWrapper
from langchain.tools import Tool 
from dotenv import load_dotenv

# loading api keys
load_dotenv()

# searching on duckduckgo
search = DuckDuckGoSearchRun()
search_tool = Tool(
    name="searching_internet",
    func=search.invoke,
    description="Use this tool to search the internet."
)

# searching with you.com
api_wrapper = YouSearchAPIWrapper(num_web_results=1)
you_search_tool = YouSearchTool(api_wrapper=api_wrapper)

# custom tools 
# just write the function
# and inside the Tool func just replace that inside 
def get_current_time(_: str = "") -> str:
    from datetime import datetime 
    current_time = datetime.now()
    readable_now = current_time.strftime("%B %d, %Y at %I:%M %p")
    return readable_now

get_time_tool = Tool(
    name="get_current_time_tool",
    func=get_current_time,
    description="Use this tool to get the current time."
)
