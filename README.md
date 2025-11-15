# Aurora Q&A System

A question-answering system that analyzes chat messages and provides intelligent answers using semantic search and large language models. The system retrieves relevant messages from a dataset, creates embeddings, and uses a RAG (Retrieval-Augmented Generation) approach to answer questions.

## 🚀 Features

- **Semantic Search**: Uses sentence transformers and FAISS for fast similarity search
- **RAG Architecture**: Combines retrieval with LLM generation for accurate answers
- **Web Interface**: User-friendly HTML interface for asking questions
- **RESTful API**: FastAPI-based API for programmatic access
- **Deployed**: Publicly accessible on Render

## 📋 Prerequisites

- Python 3.8+
- Groq API key 




## 🏗️ Architecture

The system follows a RAG (Retrieval-Augmented Generation) architecture:

1. **Data Ingestion**: Fetches messages from the API endpoint
2. **Embedding Generation**: Creates vector embeddings using `all-MiniLM-L6-v2` model
3. **Index Building**: Builds a FAISS index for fast similarity search
4. **Query Processing**: 
   - Converts user question to embedding
   - Retrieves top-k most similar messages
   - Constructs context from retrieved messages
   - Sends context + question to Groq LLM
5. **Answer Generation**: LLM generates answer based on retrieved context

## 📊 System Components

- **FastAPI**: Web framework for API and UI
- **Sentence Transformers**: For generating embeddings
- **FAISS**: Vector database for similarity search
- **Groq API**: LLM provider (using Llama 3.1 8B Instant)
- **Uvicorn**: ASGI server

## 🌐 Deployment

The service is deployed on Render and publicly accessible. The deployment configuration is in `render.yaml`.

**Live URL**: https://aurora-qa-3ddz.onrender.com

## 📝 Design Notes 

### Alternative Approaches Considered

#### 1. **Embedding Models**
- **Current Choice**: `all-MiniLM-L6-v2` (384 dimensions)
- **Alternatives Considered**:
  - `all-mpnet-base-v2`: Better accuracy but slower (768 dimensions)
  - `sentence-transformers/all-MiniLM-L12-v2`: Larger model with better performance
  - `Hugging Face Inference API (google/flan-t5-large)`: I tried this as an alternative, but the model produced incomplete        answers (ending in ellipses) because:
     -Default generation parameters were too restrictive.
     -HF Inference API limits max output tokens unless configured manually.
- **Rationale**: Chose `all-MiniLM-L6-v2` for balance between speed and accuracy, especially important for real-time queries

#### 2. **Vector Database Options**
- **Current Choice**: FAISS (in-memory)
- **Alternatives Considered**:
  - **Pinecone**: Managed vector database, easier scaling but requires external service
  - **Weaviate**: Open-source, supports hybrid search, but more complex setup
  - **ChromaDB**: Lightweight, easy to use, but less performant for large datasets
  - **Qdrant**: High performance, but requires separate service
  - **Rationale**: FAISS chosen for simplicity, speed, and no external dependencies. In-memory is sufficient for the current dataset size (~3500 messages)

#### 3. **LLM Providers**
- **Current Choice**: Groq (Llama 3.1 8B Instant)
- **Alternatives Considered**:
  - **OpenAI GPT-4/GPT-3.5**: Better quality but more expensive and slower
  - **Anthropic Claude**: Excellent reasoning, but higher cost
  - **Local LLMs** (Ollama, LM Studio): No API costs but requires local GPU
  - **Rationale**: Groq chosen for speed (very fast inference) and cost-effectiveness while maintaining good quality

#### 4. **Retrieval Strategies**
- **Current Choice**: Semantic similarity search (cosine similarity on embeddings)
- **Alternatives Considered**:
  - **BM25/Keyword Search**: Fast but misses semantic relationships
  - **Hybrid Search**: Combines keyword + semantic, better recall but more complex
  - **Rationale**: Pure semantic search chosen for simplicity and good performance on conversational queries

#### 5. **Architecture Patterns**
- **Current Choice**: RAG (Retrieval-Augmented Generation)
- **Alternatives Considered**:
  - **Fine-tuning**: Train a model on the dataset, but requires labeled data and compute

## 🔍 Data Insights 

### Anomalies and Inconsistencies Identified

After analyzing the dataset, several anomalies and inconsistencies were identified:

#### 1. **Missing or Invalid Timestamps**
- Some messages have missing or malformed timestamp fields
- Inconsistent timestamp formats across different messages
- **Impact**: Makes temporal analysis and date-based queries less reliable

#### 2. **Duplicate Messages**
- Identical messages appear multiple times with different IDs
- Same user posting the same content at different times
- **Impact**: Can skew similarity search results and provide redundant context

#### 3. **Inconsistent User Names**
- Variations in user name formatting (e.g., "John", "john", "John Doe")
- Some messages have empty or null user_name fields
- **Impact**: Makes user-specific queries less accurate

#### 4. **Empty or Very Short Messages**
- Messages with only whitespace or single characters
- Messages with just emojis or special characters
- **Impact**: These provide little semantic value and can pollute the embedding space

#### 5. **Encoding Issues**
- Some messages contain special characters that may not be properly encoded
- Unicode characters that might cause issues in embedding generation
- **Impact**: Could lead to incorrect embeddings or parsing errors

#### 6. **User ID Inconsistencies**
- Some messages have user_id that doesn't match user_name
- Missing user_id for some messages
- **Impact**: Makes user tracking and filtering difficult

### Recommendations for Data Quality Improvement

1. **Data Cleaning Pipeline**: Implement preprocessing to handle empty messages, duplicates, and encoding issues
2. **Timestamp Normalization**: Standardize timestamp formats and validate timestamps
3. **Deduplication**: Remove or flag duplicate messages before indexing
4. **User Name Normalization**: Standardize user name formats (lowercase, trim whitespace)
5. **Message Filtering**: Filter out messages below a minimum length threshold

## 🔒 Security Notes

- API keys are stored in `.env` file (not committed to git)
- The `.env` file is in `.gitignore` to prevent accidental commits

## 📦 Project Structure

```
aurora/
├── app.py                 # Main FastAPI application
├── requirements.txt       # Python dependencies
├── render.yaml           # Render deployment configuration
├── .env                  # Environment variables (not in git)
├── .gitignore           # Git ignore rules
├── templates/
│   └── index.html       # Web UI template
└── static/              # Static files (optional)
    └── placeholder.txt
```


## 👤 Author
Pallavi Lakkoju



