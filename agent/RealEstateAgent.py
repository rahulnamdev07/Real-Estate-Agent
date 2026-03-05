import os
from langchain_google_genai import ChatGoogleGenerativeAI
#from langchain_community.tools.tavily_search import TavilySearchResults   
from langchain_tavily import TavilySearch
from langchain_classic.agents import  create_react_agent, AgentExecutor 
from langchain_classic import hub

os.environ["GOOGLE_API_KEY"] = "AIzaSyA90bAktAuEk37am9sRe_gYHxu3_7tjb3Y"
os.environ["Tavily_API_KEY"] = "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"
os.environ["GOOGLE_MAPS_API_KEY"] = "AIzaSyDl1Nku1pe_-mnxtEkf78KkjVWAO4wIQmA"

if __name__ == "__main__":
    prompt = hub.pull("hwchase17/react")
    #print("Prompt template: {}".format(prompt))

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.9)
    search_tool = TavilySearch(max_results = 5)

    agent = create_react_agent(llm, [search_tool], prompt = prompt )
    agent_executor = AgentExecutor(agent=agent, tools=[search_tool], verbose=True,handle_parsing_errors=True)

    #query = "Evaluate the current real estate market around nishant pura bhopal and provide insights."
    #response = agent_executor.invoke({"input": query})

    #print("Agent response: {}".format(response))

    query = "Act as a Real Estate Agent who has expertise in the Bhopal Real Estate Market.:" \
    "Provide a summary in 50 words. To build the summary break down the problem into sub problem and collect data indivually for each sub-questions. " \
    "Now search for Nishant Pura Area in Bhopal and provide insights about Area. " \
    "# Include Demographics of Area" \
    "# Which the category types of Area (Residential, Commercial, Industrial). Provide statistics on Total Resident Apartment, Famous Apartments, in case commercial include numbers of shop or restaurant in 5 KM of area" \
    "# Provide avergae selling price of 1 BHK, 2 BHK, 3 BHK in the area. " \
    "# Provide insights about the future development of the area. " \
    "# Include Ammenties within 5 KM Range Ex: Number of Hospital, Number of Schools etc." \

    response = agent_executor.invoke({"input": query})

    query = "Role: Act as a senior Real Estate Analyst specializing in the Bhopal property market." \
    " Objective: Provide a concise 50-word executive summary of Nishant Pura, Bhopal." \
    " Method (reason internally, do not show chain-of-thought):" \
    " 1. Break the task into sub-questions." \
    " 2. Gather relevant market insights for each." \
    " 3. Synthesize into a fact-based summary." \
    " Required Analysis Inputs:" \
    " - Demographics overview" \
    " - Area classification (Residential / Commercial / Industrial)" \
    " - Estimated number of residential apartments and notable housing societies" \
    " - If commercial: approximate number of shops/restaurants within 5 km" \
    " - Average selling price for 1 BHK, 2 BHK, 3 BHK (latest available range)" \
    " - Future development outlook" \
    " - Amenities within 5 km (counts of hospitals, schools, malls)" \
    " Output Format:" \
    " Section 1: Key Data Points (bullet form)" \
    " Section 2: 50-word Executive Summary"
    " Use latest reasonable market estimates and note if data is approximate."

    response = agent_executor.invoke({"input": query})
