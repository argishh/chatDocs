import asyncio
import logging
import os
import shutil
import uuid

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from RAG.chroma_utils import deleteDocumentFromChroma, indexDocumentToChroma
from RAG.db_utils import (deleteDocumentRecord, getAllDocuments,
                          getChatHistory, insertApplicationLogs,
                          insertDocumentRecord)
from RAG.langchain_utils import getRagChain
from RAG.pydantic_models import (DeleteFileRequest, DocumentInfo, QueryInput)

load_dotenv()

OPENAI_API_KEY = None

# Initialize logging
logging.basicConfig(filename='logs/app.log', level=logging.DEBUG)

# Initialize FastAPI app
app = FastAPI()

# Add new endpoint to set API key
@app.post("/setApiKey")
async def set_api_key(api_key: str):
    global OPENAI_API_KEY
    OPENAI_API_KEY = api_key
    os.environ['OPENAI_API_KEY'] = api_key
    return {"message": "API key set successfully"}

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Chat Endpoint
@app.post("/chat")
async def chat(queryInput: QueryInput):
    try:
        # Remove the session ID generation here and just use the one from queryInput
        sessionId = queryInput.sessionId
        model = queryInput.model
        
        logging.info(f'Session ID: {sessionId}, User Query: {queryInput.question}, Model: {model}')
        
        chatHistory = getChatHistory(sessionId)
        ragChain = getRagChain(model)
        
        async def generate():
            response = ragChain.invoke({
                "input": queryInput.question,
                "chatHistory": chatHistory
            })
            
            answer = response.get('answer', '')
            if not answer:
                raise ValueError("No answer received from the model")
            
            # Stream the response character by character
            for char in answer:
                yield char
                await asyncio.sleep(0.005)  # Small delay for natural feel
            
            # Save the complete response to database after streaming
            insertApplicationLogs(sessionId, queryInput.question, answer, model)
            logging.info(f"Session ID: {sessionId}, Response: {answer}")
        
        return StreamingResponse(generate(), media_type='text/event-stream')
    
    except Exception as e:
        logging.error(f"Chat error for session {sessionId}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Upload Document Endpoint
@app.post("/uploadDoc")
def uploadAndIndexDocument(file: UploadFile = File(...)):
    allowedExtensions = ['.pdf', '֫.docx', '.txt', '.html']
    fileExtention = os.path.splitext(file.filename)[1].lower()
    
    if fileExtention not in allowedExtensions:
        raise HTTPException(status_code=400, detail="Unsupported file type. Allowed types are: {', '.join(allowedExtensions)}")
    
    tempFilePath = f'temp_{file.filename}'
    
    try:
        # Save the uploaded file to a temp file
        with open(tempFilePath, 'wb') as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        fileId = insertDocumentRecord(file.filename)
        success = indexDocumentToChroma(tempFilePath, fileId)
        
        if success:
            return {"message": f"File {file.filename} successfully uploaded and indexed.", "fileId": fileId}
        else:
            deleteDocumentRecord(fileId)
            raise HTTPException(status_code=500, detail=f"Failed to index {file.filename}.")
        
    finally:
        if os.path.exists(tempFilePath):
            os.remove(tempFilePath)        
        
# List Documents Endpoint
@app.get('/listDocs', response_model=list[DocumentInfo])
def listDocuments():
    return getAllDocuments()

# Delete Document Endpoint
@app.post('/deleteDoc')
def deleteDocument(request: DeleteFileRequest):
    chromaDeleteSuccess = deleteDocumentFromChroma(request.fileId)
    
    if chromaDeleteSuccess:
        dbDeleteSuccess = deleteDocumentRecord(request.fileId)
        if dbDeleteSuccess:
            return {"message": f"Successfully deleted file with fileId{request.fileId} from the system."}
        else:
            return {"error": f"Deleted from Chroma but failed to delete document with file_id {request.file_id} from the database."}
    else:
        return {"error": f"Failed to delete file with fileId {request.fileId} from Chroma."}

# Clear All Documents Endpoint
@app.post('/clearAllDocs')
def clearAllDocuments():
    try:
        from RAG.chroma_utils import clearChromaStore
        from RAG.db_utils import clearDocumentStore
        
        chroma_success = clearChromaStore()
        db_success = clearDocumentStore()
        
        if chroma_success and db_success:
            return {"message": "Successfully cleared all documents"}
        else:
            raise HTTPException(status_code=500, detail="Failed to clear all documents")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Clear Session Endpoint
@app.post('/clearSession/{session_id}')
def clearSession(session_id: str):
    try:
        from RAG.db_utils import clearSessionLogs
        success = clearSessionLogs(session_id)
        if success:
            return {"message": f"Successfully cleared session {session_id}"}
        else:
            raise HTTPException(status_code=500, detail="Failed to clear session")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

