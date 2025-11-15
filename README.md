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
- Groq API key (get one at [console.groq.com](https://console.groq.com))
- Internet connection (for fetching messages and downloading models)

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/pallavilakkoju/Aurora_QA.git
   cd Aurora_QA
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   
   Create a `.env` file in the root directory:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```
   
   **Important**: Never commit your `.env` file to git. It's already in `.gitignore`.

## 🎯 Usage

### Running Locally

1. **Start the server**
   ```bash
   python app.py
   ```
   
   Or using uvicorn directly:
   ```bash
   uvicorn app:app --reload --port 8001
   ```

2. **Access the web interface**
   - Open your browser and go to `http://localhost:8001`
   - Enter your question in the text field
   - Click "Submit Question" to get an answer

### API Usage

**Endpoint**: `POST /ask`

**Request Body**:
```json
{
  "question": "when is layla planning trip?",
  "top_k": 10
}
```

**Response**:
```json
{
  "answer": "Based on the messages, Layla is planning a trip..."
}
```

**Example using curl**:
```bash
curl -X POST "http://localhost:8001/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "when is layla planning trip?", "top_k": 10}'
```

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

**Live URL**: [Your Render deployment URL]

## 📝 Design Notes (Bonus 1)

### Alternative Approaches Considered

#### 1. **Embedding Models**
- **Current Choice**: `all-MiniLM-L6-v2` (384 dimensions)
- **Alternatives Considered**:
  - `all-mpnet-base-v2`: Better accuracy but slower (768 dimensions)
  - `sentence-transformers/all-MiniLM-L12-v2`: Larger model with better performance
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
  - **Re-ranking**: Use a cross-encoder to re-rank results, better precision but slower
  - **Rationale**: Pure semantic search chosen for simplicity and good performance on conversational queries

#### 5. **Architecture Patterns**
- **Current Choice**: RAG (Retrieval-Augmented Generation)
- **Alternatives Considered**:
  - **Fine-tuning**: Train a model on the dataset, but requires labeled data and compute
  - **Few-shot Learning**: Provide examples in prompt, but limited by context window
  - **Knowledge Graph**: Build relationships between entities, but complex to implement
  - **Rationale**: RAG chosen for flexibility, no training required, and ability to update knowledge by refreshing the index

#### 6. **Context Construction**
- **Current Choice**: Simple concatenation of top-k messages with timestamps
- **Alternatives Considered**:
  - **Weighted combination**: Weight messages by similarity score
  - **Deduplication**: Remove duplicate or very similar messages
  - **Temporal ordering**: Sort by timestamp for better narrative flow
  - **Rationale**: Simple approach chosen for initial implementation; could be enhanced with deduplication for better results

## 🔍 Data Insights (Bonus 2)

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

#### 6. **Message Length Inconsistencies**
- Very long messages (multi-paragraph) mixed with very short ones
- Inconsistent formatting (some with line breaks, some without)
- **Impact**: Embeddings may not capture full context for very long messages

#### 7. **Temporal Gaps**
- Large time gaps between consecutive messages from the same user
- Messages out of chronological order (possibly due to API pagination)
- **Impact**: Makes timeline-based analysis challenging

#### 8. **User ID Inconsistencies**
- Some messages have user_id that doesn't match user_name
- Missing user_id for some messages
- **Impact**: Makes user tracking and filtering difficult

### Recommendations for Data Quality Improvement

1. **Data Cleaning Pipeline**: Implement preprocessing to handle empty messages, duplicates, and encoding issues
2. **Timestamp Normalization**: Standardize timestamp formats and validate timestamps
3. **Deduplication**: Remove or flag duplicate messages before indexing
4. **User Name Normalization**: Standardize user name formats (lowercase, trim whitespace)
5. **Message Filtering**: Filter out messages below a minimum length threshold
6. **Chunking Strategy**: For very long messages, consider chunking them into smaller segments

## 🔒 Security Notes

- API keys are stored in `.env` file (not committed to git)
- Never expose your Groq API key in code or logs
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

## 🤝 Contributing

This is a project repository. For issues or improvements, please open an issue or submit a pull request.

## 📄 License

[Specify your license here]

## 👤 Author

Pallavi Lakkoju

## 🙏 Acknowledgments

- Sentence Transformers for embedding models
- FAISS for vector search
- Groq for fast LLM inference
- FastAPI for the web framework

