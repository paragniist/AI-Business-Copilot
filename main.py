from agents.router_agent import router_agent
from agents.research_agent import research_agent
from agents.analyst_agent import analyst_agent
from agents.strategy_agent import strategy_agent
from agents.response_agent import response_agent

query = input("Ask business question: ")

route = router_agent(query)

context = research_agent(query)

analysis = analyst_agent(context, query)

strategy = strategy_agent(analysis)

final_output = response_agent(analysis, strategy)

print(final_output)