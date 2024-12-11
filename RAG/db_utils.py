import sqlite3

DB_NAME = 'chatDocs.db'

# --- Establish Connection ----------------------------------------------

def getDbConnection():
    """
    Establishes connection with the SQLite database
    """
    conn = sqlite3.connect(DB_NAME)
    # conn.row_factory = sqlite3.Row
    return conn


# --- Create Tables ------------------------------------------------------

def createApplicationLogs():
    """
    Stores chat history and model responses
    """
    conn = getDbConnection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS application_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sessionId TEXT,
            userQuery TEXT,
            response TEXT,
            model TEXT,
            createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )'''
    )
    conn.close()

def createDocumentStore():
    """
    Keeps track of the uploaded documents
    """
    conn = getDbConnection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS document_store (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            uploadTimestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )'''
    )
    conn.close()


# --- Managing Chat Logs -------------------------------------------------

def insertApplicationLogs(sessionId, userQuery, response, model):
    """
    Insert a record of the chat history
    """
    conn = getDbConnection()
    conn.execute('INSERT INTO application_logs (sessionId, userQuery, response, model) VALUES (?, ?, ?, ?)', 
                 (sessionId, userQuery, response, model))
    conn.commit()
    conn.close()

def getChatHistory(sessionId):
    """
    Get the chat history of a session
    """
    conn = getDbConnection()
    cursor = conn.cursor()
    cursor.execute('SELECT userQuery, response FROM application_logs WHERE sessionId = ? ORDER BY createdAt', 
                   (sessionId,))
    
    messages = []
    for row in cursor.fetchall():
        # Convert row tuple to proper message format
        messages.extend([
            {"type": "human", "content": row[0]},
            {"type": "ai", "content": row[1]}
        ])
    
    conn.close()
    return messages


# --- Manage Document Records -------------------------------------------

def insertDocumentRecord(filename):
    """
    Insert a record of the uploaded document
    """
    conn = getDbConnection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO document_store (filename) VALUES (?)', (filename,))
    fileId = cursor.lastrowid
    conn.commit()
    conn.close()
    return fileId

def deleteDocumentRecord(fileId):
    """
    Delete the record of a uploaded document
    """
    try:
        conn = getDbConnection()
        conn.execute('DELETE FROM document_store WHERE id = ?', (fileId,))
        conn.commit()
        conn.close()
        return True
    
    except:
        return False

def getAllDocuments():
    """
    Get all unique documents
    """
    conn = getDbConnection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT DISTINCT id, filename, uploadTimestamp 
        FROM document_store 
        ORDER BY uploadTimestamp DESC
    ''')
    documents = cursor.fetchall()
    conn.close()
    
    # Convert tuples to dictionaries, ensuring uniqueness by id
    seen_ids = set()
    unique_docs = []
    for doc in documents:
        if doc[0] not in seen_ids:  # doc[0] is the id
            seen_ids.add(doc[0])
            unique_docs.append({
                "id": doc[0],
                "filename": doc[1], 
                "uploadTimestamp": doc[2]
            })
    
    return unique_docs

def clearDocumentStore():
    """
    Clear all records from the document store
    """
    try:
        conn = getDbConnection()
        conn.execute('DELETE FROM document_store')
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error clearing document store: {str(e)}")
        return False

def clearSessionLogs(sessionId):
    """
    Clear all chat logs for a specific session
    """
    try:
        conn = getDbConnection()
        conn.execute('DELETE FROM application_logs WHERE sessionId = ?', (sessionId,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error clearing session logs: {str(e)}")
        return False

# Ensuring that our tables are created when the application starts, if they don't already exist.
createApplicationLogs()
createDocumentStore()
