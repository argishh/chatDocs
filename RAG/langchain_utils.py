from langchain.chains import (create_history_aware_retriever,
                              create_retrieval_chain)
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from RAG.chroma_utils import vectorstore

retriever = vectorstore.as_retriever(search_kwargs={"k":2})
outputParser = StrOutputParser()

contextualizeQSystemPrompt = (
    """Given the following conversation history and the latest user question
    which might referenmce the previous conversation context in chat history, 
    fromulate a standalone question which can be understood without the chat history.
    Do NOT answer the question, just formulate it if needed, otherwise write it as it is."""
    )

contextualizeQPrompt = ChatPromptTemplate.from_messages([
    ("system", contextualizeQSystemPrompt),
    MessagesPlaceholder("chatHistory"),
    ("human", "{input}")
])

QAPrompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful, professional AI assistant. Use the following context to answer the user's question precisely. Do NOT write a summary at the end of the answer. Answer like you are chatting with the human."),
    ("system", "context: {context}"),
    MessagesPlaceholder(variable_name="chatHistory"),
    ("human", "{input}"),
])


# --- Creating RAG Chain ------------------------------------------------
def getRagChain(model="gpt-4o-mini"):
    llm = ChatOpenAI(model=model)
    historyAwareRetriever = create_history_aware_retriever(llm, retriever, contextualizeQPrompt)
    questionAnswerChain = create_stuff_documents_chain(llm, QAPrompt)
    ragChain = create_retrieval_chain(historyAwareRetriever, questionAnswerChain)    
    return ragChain
