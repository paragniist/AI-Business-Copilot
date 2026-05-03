from workflows.business_graph import app

query = input("Ask business question: ")

result = app.invoke({
    "query": query,
    "route": {},
    "context": "",
    "analysis": "",
    "strategy": "",
    "final_output": ""
})

print(result["final_output"])