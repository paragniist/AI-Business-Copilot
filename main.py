from agents.router_agent import router_agent
from agents.research_agent import research_agent
from agents.analyst_agent import analyst_agent
from agents.response_agent import response_agent

query = input("Ask business question: ")

route = router_agent(query)

context = research_agent(query)

solution = analyst_agent(context, query)

sources = """
• Annual Report 2025
• Sales Report Q4
• Internal Business Data
"""

final_output = response_agent(query, sources, solution)

print(final_output)