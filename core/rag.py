import os
import tempfile

from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

CHUNK_SIZE = 500
CHUNK_OVERLAP = 100


def get_embedding_model():
    return GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=GOOGLE_API_KEY,
    )


def load_pdf(uploaded_file):
    """
    Saves the uploaded PDF temporarily and loads it as LangChain Documents.
    """

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        for chunk in uploaded_file.chunks():
            temp_pdf.write(chunk)

        temp_path = temp_pdf.name

    loader = PyPDFLoader(temp_path)
    documents = loader.load()

    os.remove(temp_path)

    return documents


def create_vectorstore(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )

    chunks = splitter.split_documents(documents)

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=get_embedding_model(),
    )

    return vectorstore


def retrieve_context(uploaded_file, query, k=3):
    """
    Returns the most relevant context from the uploaded PDF.
    """

    documents = load_pdf(uploaded_file)

    vectorstore = create_vectorstore(documents)

    retriever = vectorstore.as_retriever(
        search_kwargs={"k": k}
    )

    docs = retriever.invoke(query)

    context = "\n\n".join(doc.page_content for doc in docs)

    return context