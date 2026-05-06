import os
import json
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    context_precision,
    context_recall,
    faithfulness,
    answer_relevancy,
)
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings

def get_ragas_llm_and_embeddings():
    # Ragas needs specific wrapper objects in some versions, but passing standard LangChain objects usually works in the evaluate() function directly.
    llm = ChatGoogleGenerativeAI(model="gemini-3.1-pro-preview", temperature=0)
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return llm, embeddings

def evaluate_single_query(question: str, answer: str, contexts: list, ground_truth: str = None) -> dict:
    """
    Evaluates a single query.
    """
    data = {
        "question": [question],
        "answer": [answer],
        "contexts": [contexts],
    }
    
    metrics = [faithfulness, answer_relevancy]
    
    if ground_truth:
        data["ground_truth"] = [ground_truth]
        metrics.extend([context_precision, context_recall])
        
    dataset = Dataset.from_dict(data)
    llm, embeddings = get_ragas_llm_and_embeddings()
    
    try:
        # Some ragas versions return a Result object that can be converted to dict
        result = evaluate(
            dataset=dataset,
            metrics=metrics,
            llm=llm,
            embeddings=embeddings,
            raise_exceptions=False
        )
        return dict(result) if hasattr(result, 'items') else result
    except Exception as e:
        print(f"Evaluation failed: {e}")
        return {"error": str(e)}

def batch_evaluate(dataset_path: str = "evaluation/dataset.json") -> dict:
    """
    Evaluates a batch of queries from a JSON dataset.
    """
    with open(dataset_path, "r") as f:
        data = json.load(f)
        
    questions = []
    answers = []
    contexts = []
    ground_truths = []
    
    from app.services.analyzer import process_query
    
    for item in data:
        questions.append(item["question"])
        ground_truths.append(item["ground_truth"])
        
        # Run through the RAG pipeline dynamically
        result = process_query(item["question"])
        answers.append(result["final_output"])
        
        context_str = result.get("context", "")
        context_list = [c.strip() for c in context_str.split("\n\n") if c.strip()]
        if not context_list:
            context_list = ["No context retrieved"]
        contexts.append(context_list)
        
    eval_dataset = Dataset.from_dict({
        "question": questions,
        "answer": answers,
        "contexts": contexts,
        "ground_truth": ground_truths
    })
    
    llm, embeddings = get_ragas_llm_and_embeddings()
    
    try:
        result = evaluate(
            dataset=eval_dataset,
            metrics=[context_precision, context_recall, faithfulness, answer_relevancy],
            llm=llm,
            embeddings=embeddings,
            raise_exceptions=False
        )
        
        res_dict = dict(result) if hasattr(result, 'items') else result
        
        os.makedirs("evaluation/logs", exist_ok=True)
        with open("evaluation/logs/batch_eval_results.json", "w") as f:
            json.dump(res_dict, f, indent=2)
            
        return res_dict
    except Exception as e:
        print(f"Batch evaluation failed: {e}")
        return {"error": str(e)}

def log_evaluation(query: str, contexts: list, answer: str, eval_results: dict):
    """
    Logs online evaluation results to a file.
    """
    os.makedirs("evaluation/logs", exist_ok=True)
    log_file = "evaluation/logs/online_eval_log.jsonl"
    
    log_entry = {
        "question": query,
        "contexts": contexts,
        "answer": answer,
        "metrics": eval_results
    }
    
    try:
        json_str = json.dumps(log_entry)
    except TypeError:
        log_entry["metrics"] = {k: str(v) for k, v in eval_results.items()} if isinstance(eval_results, dict) else str(eval_results)
        json_str = json.dumps(log_entry)
    
    with open(log_file, "a") as f:
        f.write(json_str + "\n")
