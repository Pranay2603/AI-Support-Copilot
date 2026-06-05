import os

from groq import Groq
from dotenv import load_dotenv
from app.services.rag_service import search_pdf

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

def get_ai_response(user_query, previous_chats=[]):

    messages = [
        {
            "role": "system",
            "content": """
            You are an AI customer support assistant
            for a SaaS company.

            Be professional, concise, and helpful.

            Remember previous conversation context
            while answering.
            """
        }
    ]

    for chat in previous_chats:

        pdf_context = search_pdf(user_query)

        enhanced_query = f"""
        Use the following PDF context
        to answer the user.

        PDF Context:
        {pdf_context}

        User Question:
        {user_query}
        """

        messages.append({
            "role": "user",
            "content": enhanced_query
        })

        messages.append({
            "role": "assistant",
            "content": chat[1]
        })

    messages.append({
        "role": "user",
        "content": user_query
    })

    try:

        completion = client.chat.completions.create(
            messages=messages,
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            stream=True
        )

        full_response = ""

        for chunk in completion:

            content = chunk.choices[0].delta.content

            if content:
                full_response += content

        return full_response

    except Exception:

        return """
        AI service is temporarily unavailable.

        Please try again in a few moments.
        """

def generate_conversation_title(user_query):

    completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": """
                Generate a short professional
                conversation title.

                Maximum 4 words.

                No quotes.
                """
            },
            {
                "role": "user",
                "content": user_query
            }
        ],

        model="llama-3.3-70b-versatile",
        temperature=0.3,
        stream=False
    )

    return completion.choices[0].message.content.strip()