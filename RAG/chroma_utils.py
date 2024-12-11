from typing import List

from langchain_chroma import Chroma
from langchain_community.document_loaders import (Docx2txtLoader, PyPDFLoader,
                                                  UnstructuredHTMLLoader)
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings

# Initialize text splitter and embedding function
textSplitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, length_function=len)
embeddingFunction = OpenAIEmbeddings()

# Initialize Chroma vector store
vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embeddingFunction)


# --- Loading & Splitting Documents -------------------------------------

def loadAndSplitDocument(filepath: str) -> List[Document]:
    if filepath.endswith('.pdf'):
        loader = PyPDFLoader(filepath)
    elif filepath.endswith('.docx'):
        loader = Docx2txtLoader(filepath)
    elif filepath.endswith('.html'):
        loader = UnstructuredHTMLLoader(filepath)
    elif filepath.endswith('.txt'):
        loader = UnstructuredHTMLLoader(filepath)
    else:
        raise ValueError(f"Unsupported file type: {filepath}")

    documents = loader.load()
    return textSplitter.split_documents(documents)


# --- Indexing Documents to Chroma --------------------------------------

def indexDocumentToChroma(filepath: str, fileId: int) -> bool:
    try:
        splits = loadAndSplitDocument(filepath)
        
        # Add metadata to each split
        for split in splits:
            split.metadata.update({
                'fileId': fileId,
                'source': filepath
            })

        vectorstore.add_documents(documents=splits)
        return True
    
    except Exception as e:
        print(f"Error Indexing the document: {str(e)}")
        return False
    

# --- Deleting Documents from Chroma ------------------------------------

def deleteDocumentFromChroma(fileId: int):
    try:
        # Fix: Use correct metadata field name
        vectorstore._collection.delete(where={'fileId': fileId})
        print(f'Deleted all documents with fileId {fileId}')
        return True

    except Exception as e:
        print(f"Error deleting document with fileId {fileId} from Chroma: {str(e)}")
        return False


def clearChromaStore():
    """
    Clear all documents from Chroma
    """
    try:
        vectorstore._collection.delete(where={})
        print('Cleared all documents from Chroma')
        return True
    except Exception as e:
        print(f"Error clearing Chroma store: {str(e)}")
        return False




