import os
import time
import requests
import faiss
from fastapi import FastAPI, Request
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import uvicorn
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

API_URL = "https://november7-730026606190.europe-west1.run.app/messages"

# Get API key from environment variable
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is not set. Please set it in your .env file.")

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.1-8b-instant"
GROQ_TIMEOUT = 60
MAX_NEW_TOKENS = 500
TOP_K = 10

def fetch_all_messages(limit=3500, max_retries=10, retry_delay=10):
    skip = 0
    all_messages = []
    while True:
        retries = 0
        while retries < max_retries:
            try:
                response = requests.get(
                    API_URL,
                    params={"skip": skip, "limit": limit},
                    timeout=10
                )
                response.raise_for_status()
                data = response.json()
                if 'items' not in data or not isinstance(data['items'], list):
                    raise ValueError(f"Invalid response: {data}")
                items = data['items']
                break
            except Exception:
                retries += 1
                time.sleep(retry_delay)
        else:
            break
        
        if not items:
            break
        
        all_messages.extend(items)
        skip += len(items)
    
    return all_messages


def query_groq(prompt):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": MAX_NEW_TOKENS,
        "temperature": 0
    }
    
    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=GROQ_TIMEOUT)
        response.raise_for_status()
        result = response.json()
        if 'choices' in result and len(result['choices']) > 0:
            return result['choices'][0]['message']['content']
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"


print("Loading embedding model")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

print("Fetching messages")
messages = fetch_all_messages()

message_data = []
for msg in messages:
    message_data.append({
        "text": msg['message'],
        "user_name": msg['user_name'],
        "user_id": msg['user_id'],
        "timestamp": msg['timestamp'],
        "id": msg['id']
    })

texts = [m['text'] + m['user_name'] + m["timestamp"] for m in message_data]

print("Creating embeddings")
embeddings = embedding_model.encode(texts, convert_to_numpy=True, show_progress_bar=True)

if embeddings.ndim == 1:
    embeddings = embeddings.reshape(1, -1)

print("Building FAISS index")
dim = embeddings.shape[1]
index = faiss.IndexFlatL2(dim)
index.add(embeddings)

print(f"FAISS index is loaded: {index.ntotal} items")


def answer_question(question, top_k=TOP_K):
    q_embedding = embedding_model.encode([question], convert_to_numpy=True)
    distances, indices = index.search(q_embedding, top_k)
    retrieved_messages = [message_data[i] for i in indices[0]]
    
    context = "\n".join(
        [f"[Timestamp: {m['timestamp']}], User: {m['user_name']}, Message: {m['text']}"
         for m in retrieved_messages]
    )
    
    prompt = f"""You are Chat Analyzer. Use the following timestamped messages as context. Convert any relative dates using the provided timestamps. Provide a direct and concise answer.

Context:
{context}

Question:
{question}

Answer:
"""
    
    return query_groq(prompt)


app = FastAPI(title="Question Answering API")

class QueryRequest(BaseModel):
    question: str
    top_k: int = TOP_K


@app.post("/ask")
def ask_question(req: QueryRequest):
    try:
        response = answer_question(req.question, req.top_k)
        return {"answer": response}
    except Exception as e:
        return {"error": str(e)}


# Frontend integration
# Only mount static files if the directory exists
if os.path.exists("static") and os.path.isdir("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def ui(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
