# ChatDocs - RAG based Chat Assistant

ChatDocs is an intelligent document chat system that allows users to upload documents and interact with them through natural language queries. The system uses RAG (Retrieval Augmented Generation) to provide accurate, context-aware responses based on the uploaded documents.

<details>
    <summary>📸<b> Screenshots</b></summary><br>

![Home Page](img/landing_page.png)
<p align="center"><em>Landing Page</em></p><br>

![Document Upload](img/uploading_doc.png)
<p align="center"><em>Document Upload</em></p><br>

![Thinking](img/thinking.png)
<p align="center"><em>Generating Response | Thining...</em></p><br>

![Response Stream](img/response_stream.png)
<p align="center"><em>Streaming Response</em></p><br>

![Overview](img/overview.png)

</details>

<details>
    <summary><b>🌟 Features</b></summary>
<br>

- **Document Management**
  - Support for multiple file formats (PDF, DOCX, TXT)
  - Easy document upload and deletion
  - Automatic document indexing and embedding

- **Intelligent Chat**
  - Context-aware responses using RAG
  - Chat history tracking
  - Support for multiple GPT models *(more coming soon)*
  - Session management for continuous conversations *(experimental)*

- **Modern Architecture**
  - `FastAPI` backend for high performance
  - `Streamlit` frontend for user-friendly interface
  - `ChromaDB` vectorstore for efficient document retrieval
  - `SQLite` database for persistent storage

- **Easy Integration**
  - Simple API endpoints for document management and chat
  - Streamlit UI for intuitive user interaction
  - OpenAI GPT models for powerful conversational AI

- **Simple to Setup**
  - Minimal dependencies
  - Quick installation and configuration
  - Detailed documentation and usage examples

</details>

<details>
    <summary><b>❔ FAQs</b><br></summary>

###  **How does ChatDocs work?** 
*ChatDocs uses RAG to generate responses based on the uploaded documents. It first indexes and embeds the documents using ChromaDB and then uses the LangChain pipeline to process the queries and generate responses.*

### **What file formats are supported?**
*ChatDocs currently supports PDF, DOCX, and TXT file formats. You can upload documents in any of these formats and interact with them using natural language queries.*

### **Can I use my own GPT model?**
*Yes, you can use your own GPT model by setting the `OPENAI_API_KEY` environment variable to your API key. ChatDocs currently supports OpenAI's GPT-3 model, but you can easily switch to other models by changing the API key.*

### **Is my data secure?**
*Yes, your data is secure with ChatDocs. The documents are stored securely in the ChromaDB vectorstore, and the API endpoints are protected against common vulnerabilities. The system uses session-based authentication to ensure that only authorized users can access the data.*

### **What is RAG?**
*RAG (Retrieval Augmented Generation) is a transformer-based model that combines the power of retrieval-based and generative models. It uses a retriever to find relevant documents and a generator to produce responses based on the retrieved context.*

</details>

## 🔧 Toolkit

### Backend Components

- **FastAPI Server**: Handles API endpoints and business logic
- **Chroma Vector Store**: Manages document embeddings and similarity search
- **SQLite Database**: Stores document metadata and chat history
- **LangChain**: Orchestrates the RAG pipeline and document processing
- **Pydantic Models**: Defines data models for API requests and responses
- **OpenAI API**: Provides access to GPT models

### Frontend Components

- **Streamlit UI**: Provides an intuitive interface for:
  - Document upload and management
  - Chat interface
  - Model selection


## 💻 Installation

### Prerequisites

```bash
# Python 3.8 or higher is required
python --version

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows
```

### Running Locally

1. Clone the repository:
```bash
git clone https://github.com/yourusername/chatDocs.git
cd chatDocs
```

2. Install backend dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file:
```bash
echo "OPENAI_API_KEY=your_api_key_here" > .env
```

4. Initialize the database:
```bash
python init_db.py
```

## 🚀 Booting the Application

*Start the application using the provided script:*
```bash
source run.sh
```

### Alternatively,

*Start the Streamlit app:*
```bash
streamlit run app.py
```

3. Access the application: *(locally)*
- ChatDocs App: http://localhost:8501
- API Documentation: http://localhost:8000/docs

## 📁 Project Structure

```
chatDocs/
├── README.md                   # About the Project
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables
├── api.py                      # FastAPI server
├── app.py                      # Streamlit frontend
├── RAG/                        # RAG pipeline
│   ├── chroma_utils.py         # ChromaDB utilities
│   ├── db_utils.py             # SQLite database utilities
│   ├── langchain_utils.py      # LangChain utilities
│   └── pydantic_models.py      # Pydantic data models
└── chroma_db/                  # ChromaDB vectorstore
    └── ...
```

## 🔍 API Endpoints

- `POST /setApiKey`: Set OpenAI API key
- `POST /chat`: Send queries and receive responses
- `POST /uploadDoc`: Upload new documents
- `GET /listDocs`: List all uploaded documents
- `POST /deleteDoc`: Delete a document
- `POST /clearAllDocs`: Delete all documents
- `POST /clearSession`: Delete all chat history

## 🛠 Configuration

### Environment Variables  *(Optional)*

Create a `.env` file with the following configurations:

```env
OPENAI_API_KEY=your_api_key_here
```

### Supported File Types

- PDF (`.pdf`)
- Microsoft Word (`.docx`)
- Text (`.txt`)


## 🤝 Contributing

Contributions are always welcome! Here's how you can help:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔐 Security

- The application uses session-based authentication
- Documents are stored securely in the Chroma vector store
- API endpoints are protected against common vulnerabilities

## ⚠️ Known Issues and Limitations

1. Large PDF files might take longer to process.
2. File size `>200 MB` is not supported.
2. Memory usage increases with the number of documents
3. Currently supports only text-based documents

## 🗺 Future Tasks

- [ ] Add Docker Container
- [x] Implement batch document upload
- [ ] Add support for other LLMs (Groq, Gemma, Claude, Llama3.3, etc.)
- [ ] Add support for more file types
- [ ] Add SOTA document chunking configurations
- [ ] Improve response quality with better system prompts
- [ ] Implement user authentication

## ⛑️ Support

For support, please:
1. Check the [documentation](http://localhost:8000/docs)
2. Open an issue on GitHub
3. Contact the maintainer at [argish.official@gmail.com](mailto:argish.official@gmail.com)