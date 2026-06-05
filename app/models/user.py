from app.database import cursor, conn

def create_user(email, password):
    cursor.execute(
        "INSERT INTO users (email, password) VALUES (?, ?)",
        (email, password)
    )
    conn.commit()

def get_user(email):

    cursor.execute(
        "SELECT * FROM users WHERE email=?",
        (email,)
    )

    return cursor.fetchone()

def email_exists(email):

    cursor.execute(
        "SELECT id FROM users WHERE email=?",
        (email,)
    )

    return cursor.fetchone() is not None

def get_user_by_email(email):

    cursor.execute(
        "SELECT * FROM users WHERE email=?",
        (email,)
    )

    return cursor.fetchone()

def update_user_profile(
    current_email,
    username,
    new_email
):

    cursor.execute(
        """
        UPDATE users
        SET username=?,
            email=?
        WHERE email=?
        """,
        (
            username,
            new_email,
            current_email
        )
    )

    conn.commit()