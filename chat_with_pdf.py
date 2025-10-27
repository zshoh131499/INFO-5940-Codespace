import os
import streamlit as st
from pypdf import PdfReader

from openai import OpenAI
from os import environ

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.documents import Document

from langchain_openai import OpenAIEmbeddings, ChatOpenAI


client = OpenAI(
	api_key=os.environ["API_KEY"],
    
	base_url="https://api.ai.it.cornell.edu",
)

st.title("📝 Toby's File Q&A with OpenAI")


uploaded_file = st.file_uploader(
    "Upload an article file",
    type=("txt","md","pdf"),
    accept_multiple_files = True
    )

question = st.chat_input(
    "Ask something about the article",
    disabled = not uploaded_file,
)

file_content = st.session_state.get("txt", "")


# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Ask something about the article"}]

if "file_contents" not in st.session_state:
    st.session_state["file_contents"] = []

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if question and uploaded_file:
    # Read all uploaded files
    st.session_state["file_contents"] = []
    for f in uploaded_file:
        name = getattr(f, "name", "")
        
        is_pdf = (getattr(f, "type", "") == "application/pdf") or name.lower().endswith(".pdf")

        if is_pdf:
            # use pypdf to get text 
            reader = PdfReader(f)
            txt = "\n".join((page.extract_text() or "") for page in reader.pages)
            if not txt.strip():
                st.warning(f"'{name}' can not get text from this PDF")
        else:
            # other txt file
            txt = f.getvalue().decode("utf-8", errors="ignore")
        st.session_state["file_contents"].append(txt)

            # Combine for chunking / context
    file_content = "\n\n---\n\n".join(st.session_state["file_contents"]) 

    # Append the user's question to the messages
    st.session_state.messages.append({"role": "user", "content": question})
    st.chat_message("user").write(question)

    # Split documents into chunks
    chunk_size = 900  # Size of each chunk in characters
    chunk_overlap = 150  # Overlap between chunks to maintain context
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, 
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""]
    )

    chunks = text_splitter.split_text(file_content) 
    # 1)  chunk convert to LangChain  Document
    documents = [Document(page_content=c) for c in chunks]

    # 2) embedding
    embeddings = OpenAIEmbeddings(
        api_key=os.environ["API_KEY"],
        base_url="https://api.ai.it.cornell.edu",
        model="openai.text-embedding-3-small",  
    )

    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=".chroma",
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

    st.session_state["retriever"] = retriever

prompt = PromptTemplate.from_template(
""" You are a knowledgeable assistant analyzing documents. Your task is to provide accurate, helpful answers based on the provided context.
    
    Instructions:
    - Answer questions based on the document chunks provided in the context
    - If there are previous conversations, use them to understand the current question better
    - Format any lists or structured information clearly if necessary

Question: {question}

Context: {context}

Answer:
"""
)

def format_docs(docs):
    return "\n\n---\n\n".join(d.page_content for d in docs)

# LLM
llm = ChatOpenAI(
    api_key=os.environ["API_KEY"],
    base_url="https://api.ai.it.cornell.edu",
    model="openai.gpt-4o",
    temperature=0,
)

# ---------- when the user asks a question, use the saved retriever ----------
if question:
    if "retriever" not in st.session_state:
        st.warning("Please upload files first so I can build the index.")
    else:
        rag_chain = (
            {"context": st.session_state["retriever"] | format_docs,
             "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )
        with st.chat_message("assistant"):
            try:
                response = rag_chain.invoke(question)
                st.write(response)
            except Exception as e:
                response = f"Error: {e}"
                st.error(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

    

