import json
import os
import sqlite3

import bcrypt
import mysql.connector


class Database:
    def __init__(self, host='localhost', user='root', password='', database='nlp_app', sqlite_path=None):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.backend = 'mysql'
        self.sqlite_path = sqlite_path or os.path.join(os.path.dirname(__file__), f'{self.database}.db')
        self.mysql_error = None
        self._initialize_backend()

    def _initialize_backend(self):
        try:
            self.create_database() # Ensure MySQL database exists
        except mysql.connector.Error as exc:
            self.backend = 'sqlite'
            self.mysql_error = exc
            print(
                f"MySQL is unavailable ({exc}). "
                f"Falling back to SQLite at '{self.sqlite_path}'."
            )

    def create_database(self):
        if self.backend == 'sqlite':
            return

        conn = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password)
        cursor = conn.cursor() # initialize cursor/connection
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
        cursor.close()
        conn.close()

    def connect(self):
        if self.backend == 'sqlite':
            conn = sqlite3.connect(self.sqlite_path)
            conn.row_factory = sqlite3.Row
            return conn

        return mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )

    @staticmethod
    def _normalize_password_hash(hashed_password):
        if isinstance(hashed_password, memoryview):
            return hashed_password.tobytes()
        if isinstance(hashed_password, str):
            return hashed_password.encode()
        return hashed_password

    def create_user_table(self):
        conn = self.connect()
        cursor = conn.cursor()
        if self.backend == 'sqlite':
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    first_name TEXT NOT NULL,
                    last_name TEXT,
                    email TEXT NOT NULL UNIQUE,
                    password BLOB NOT NULL
                )
            """)
        else:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    first_name VARCHAR(100) NOT NULL,
                    last_name VARCHAR(100),
                    email VARCHAR(100) NOT NULL UNIQUE,
                    password VARCHAR(100) NOT NULL
                )
            """)
        conn.commit()
        cursor.close()
        conn.close()

    def create_analysis_history_table(self):
        conn = self.connect()
        cursor = conn.cursor()
        if self.backend == 'sqlite':
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analysis_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    analysis_type TEXT NOT NULL,
                    input_text TEXT NOT NULL,
                    result_json TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
        else:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analysis_history (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    analysis_type VARCHAR(100) NOT NULL,
                    input_text LONGTEXT NOT NULL,
                    result_json LONGTEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def _make_preview(text, limit=180):
        if not text:
            return ""
        compact = " ".join(str(text).split())
        return compact if len(compact) <= limit else f"{compact[:limit].rstrip()}..."

    def save_analysis_history(self, user_id, analysis_type, input_text, result_payload):
        serialized_result = json.dumps(result_payload, ensure_ascii=True)
        conn = self.connect()
        cursor = conn.cursor()
        if self.backend == 'sqlite':
            cursor.execute(
                """
                INSERT INTO analysis_history (user_id, analysis_type, input_text, result_json)
                VALUES (?, ?, ?, ?)
                """,
                (user_id, analysis_type, input_text, serialized_result)
            )
        else:
            cursor.execute(
                """
                INSERT INTO analysis_history (user_id, analysis_type, input_text, result_json)
                VALUES (%s, %s, %s, %s)
                """,
                (user_id, analysis_type, input_text, serialized_result)
            )
        conn.commit()
        cursor.close()
        conn.close()

    def get_user_analysis_history(self, user_id, limit=10):
        conn = self.connect()
        if self.backend == 'sqlite':
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, user_id, analysis_type, input_text, result_json, created_at
                FROM analysis_history
                WHERE user_id = ?
                ORDER BY created_at DESC, id DESC
                LIMIT ?
                """,
                (user_id, limit)
            )
        else:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT id, user_id, analysis_type, input_text, result_json, created_at
                FROM analysis_history
                WHERE user_id = %s
                ORDER BY created_at DESC, id DESC
                LIMIT %s
                """,
                (user_id, limit)
            )

        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        history_items = []
        for row in rows:
            item = dict(row) if self.backend == 'sqlite' else row
            result_preview = self._make_preview(item.get('result_json', ''))
            created_at = item.get('created_at')
            history_items.append({
                'id': item['id'],
                'user_id': item['user_id'],
                'analysis_type': item['analysis_type'],
                'analysis_label': item['analysis_type'].replace('-', ' ').title(),
                'input_preview': self._make_preview(item.get('input_text', '')),
                'result_preview': result_preview,
                'created_at': str(created_at) if created_at is not None else ''
            })

        return history_items


    def add_user(self, first_name, last_name, email, password):
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        conn = self.connect()
        cursor = conn.cursor()
        if self.backend == 'sqlite':
            cursor.execute(
                "INSERT INTO users (first_name, last_name, email, password) VALUES (?, ?, ?, ?)",
                (first_name, last_name, email, hashed)
            )
        else:
            cursor.execute(
                "INSERT INTO users (first_name, last_name, email, password) VALUES (%s, %s, %s, %s)",
                (first_name, last_name, email, hashed)
            )
        conn.commit()
        cursor.close()
        conn.close()

    def get_user_by_email(self, email):
        conn = self.connect()
        if self.backend == 'sqlite':
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM users WHERE email = ?",
                (email,)
            )
        else:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM users WHERE email = %s",
                (email,)
            )
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        return dict(user) if user and self.backend == 'sqlite' else user

        

    def validate_user(self, email, password):
         conn = self.connect()
         if self.backend == 'sqlite':
             cursor = conn.cursor()
             cursor.execute(
                 "SELECT * FROM users WHERE email = ?",
                 (email,)
             )
         else:
             cursor = conn.cursor(dictionary=True)
             cursor.execute(
                 "SELECT * FROM users WHERE email = %s",
                 (email,)
             )
         user = cursor.fetchone()
         cursor.close()
         conn.close()

         if not user:
            return None

         user_data = dict(user) if self.backend == 'sqlite' else user
         stored_password = self._normalize_password_hash(user_data['password'])
         if bcrypt.checkpw(password.encode(), stored_password):
            return user_data
         return None
