import os
import markdown

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import FastEmbedEmbeddings
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

embedding_model = FastEmbedEmbeddings(
    model_name="BAAI/bge-small-en-v1.5"
)


def create_vector_store(pdf_path, user):

    loader = PyPDFLoader(pdf_path)

    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    chunks = text_splitter.split_documents(documents)

    for chunk in chunks:
        chunk.metadata["source"] = pdf_path

    vector_store = FAISS.from_documents(
        chunks,
        embedding_model
    )

    faiss_path = f"faiss_index/{user}"

    os.makedirs(
        "faiss_index",
        exist_ok=True
    )

    vector_store.save_local(faiss_path)


def ask_pdf(query, user):

    try:

        faiss_path = f"faiss_index/{user}"

        vector_store = FAISS.load_local(
            faiss_path,
            embedding_model,
            allow_dangerous_deserialization=True
        )

        docs = vector_store.similarity_search(
            query,
            k=8
        )

        source_counts = {}

        for doc in docs:

            source = doc.metadata.get(
                "source",
                "Unknown"
            )

            source_counts[source] = (
                source_counts.get(source, 0) + 1
            )

        context = "\n".join(
            [doc.page_content for doc in docs]
        )

        prompt = f"""
        You are an intelligent AI assistant.

        Use PDF context ONLY if relevant to the user's query.

        If the user asks a general question unrelated to PDFs,
        answer normally using your own knowledge.

        Answer clearly and cleanly.

        Context:
        {context}

        Question:
        {query}
        """

        completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.3
        )

        answer = markdown.markdown(
            completion.choices[0].message.content
        )

        source_text = "\n\n---\n\n## 📄 Sources Used\n"

        sorted_sources = sorted(
            source_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )

        shown_sources = 0

        for source, count in sorted_sources:

            if count >= 2:

                source_text += (
                    f"\n- {os.path.basename(source)}"
                )

                shown_sources += 1

        if shown_sources == 0 and sorted_sources:

            source_text += (
                f"\n- {os.path.basename(sorted_sources[0][0])}"
            )

        return answer + source_text

    except Exception:

        return """
        AI service is temporarily unavailable.

        Please try again in a few moments.
        """


def search_pdf(query):

    if not os.path.exists("faiss_index"):
        return ""

    vector_store = FAISS.load_local(
        "faiss_index",
        embedding_model,
        allow_dangerous_deserialization=True
    )

    docs = vector_store.similarity_search(
        query,
        k=3
    )

    context = ""

    for doc in docs:
        context += doc.page_content + "\n"

    return context