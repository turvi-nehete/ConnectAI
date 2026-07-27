from langchain_tavily import TavilySearch


def get_tools():
    search_tool = TavilySearch(
        max_results=5,
        topic="general",
    )

    return [search_tool]