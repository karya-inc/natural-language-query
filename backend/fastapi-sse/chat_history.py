import sqlite3
from typing import Generator
from fastapi import HTTPException
import json
from logger import setup_logging, disable_logging
import os
from dotenv import load_dotenv

load_dotenv()

# Path to the SQLite database
DB_PATH = os.getenv("DB_PATH")  # e.g., "chat_history.db"

# disable_logging()

# Set up logging configuration
logger = setup_logging('chat_history', 'chat_history_success.log', 'chat_history_error.log')


def create_chat_history_table():
    """
    Creates the chat history table in SQLite if it doesn't exist.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS chat_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        query TEXT NOT NULL,
        response TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    conn.commit()
    conn.close()


def store_chat_history(session_id: str, query: str, response: str) -> None:
    """
    Stores chat history in the SQLite database.
    
    Args:
        session_id: The session identifier.
        query: The user's query.
        response: The generated response.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO chat_history (session_id, query, response)
    VALUES (?, ?, ?)
    ''', (session_id, query, response))
    conn.commit()
    conn.close()


def get_chat_history(session_id: str) -> list[dict]:
    """
    Function to fetch chat history for a given session.

    Args:
        session_id: The session identifier to fetch history.

    Returns:
        List of dictionaries containing chat history entries.
    """
    try:
        conn = sqlite3.connect('chat_history.db')
        cursor = conn.cursor()

        cursor.execute('''
        SELECT query, response, timestamp
        FROM chat_history
        WHERE session_id = ?
        ORDER BY timestamp
        ''', (session_id,))

        history = cursor.fetchall()
        conn.close()

        # Create a list to store the chat history entries
        history_list = []
        for entry in history:
            query, response, timestamp = entry
            history_list.append({
                "session_id": session_id,
                "query": query,
                "response": response,
                "timestamp": timestamp
            })

        return history_list

    except Exception as e:
        logger.error(f"Error while retrieving chat history for session: {session_id}. Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve chat history.")