from app.database import conn

def create_chat_table():

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        conversation_id TEXT,
        conversation_title TEXT,
        user_email TEXT,
        user_message TEXT,
        ai_response TEXT,
        time TEXT
    )
    """)

    conn.commit()


def save_chat(
    conversation_id,
    conversation_title,
    user_email,
    user_message,
    ai_response,
    time
):

    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO chats (
        conversation_id,
        conversation_title,
        user_email,
        user_message,
        ai_response,
        time
    )
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        conversation_id,
        conversation_title,
        user_email,
        user_message,
        ai_response,
        time
    ))

    conn.commit()

def delete_user_chats(user_email):

    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM chats WHERE user_email = ?",
        (user_email,)
    )

    conn.commit()


def get_user_chats(user_email):

    cursor = conn.cursor()

    cursor.execute("""
    SELECT user_message, ai_response, time
    FROM chats
    WHERE user_email = ?
    """, (user_email,))

    return cursor.fetchall()

def get_user_conversations(user_email):

    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        conversation_id,
        conversation_title
    FROM chats
    WHERE user_email = ?
    GROUP BY conversation_id
    ORDER BY MAX(id) DESC
    """, (user_email,))

    return cursor.fetchall()

def get_conversation_chats_for_user(
    conversation_id,
    user_email
):

    cursor = conn.cursor()

    cursor.execute("""
    SELECT user_message, ai_response, time
    FROM chats
    WHERE conversation_id = ?
    AND user_email = ?
    """, (
        conversation_id,
        user_email
    ))

    return cursor.fetchall()


def delete_conversation_for_user(
    conversation_id,
    user_email
):

    cursor = conn.cursor()

    cursor.execute("""
    DELETE FROM chats
    WHERE conversation_id = ?
    AND user_email = ?
    """, (
        conversation_id,
        user_email
    ))

    conn.commit()