import sqlite3
import json
from datetime import datetime

DB_PATH="DB.db"

def get_connection():
    conn=sqlite3.connect(DB_PATH)
    conn.row_factory=sqlite3.Row
    return conn

def init_db():
    conn=get_connection()
    cursor=conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sections TEXT,
            created_at TEXT,
            total_questions INTEGER,
            correct_count INTEGER
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            section_id INTEGER,
            question TEXT,
            choices TEXT,
            correct_answer TEXT,
            explanation TEXT,
            user_answer TEXT,
            is_correct INTEGER
        )
    """)
    conn.commit()
    conn.close()

def save_session(section_ids,questions_data):
    conn=get_connection()
    cursor=conn.cursor()
    correct_count=sum(1 for q in questions_data if q["is_correct"])
    total=len(questions_data)
    sections_str=json.dumps(section_ids)
    created_at=datetime.now().isoformat()
    cursor.execute("""
        INSERT INTO sessions (sections,created_at,total_questions,correct_count)
        VALUES (?,?,?,?)
    """,(sections_str,created_at,total,correct_count))
    session_id=cursor.lastrowid
    for q in questions_data:
        choices_str=json.dumps(q["choices"])
        cursor.execute("""
            INSERT INTO questions 
            (session_id,section_id,question,choices,correct_answer,explanation,user_answer,is_correct)
            VALUES (?,?,?,?,?,?,?,?)
        """,(session_id,q["section_id"],q["question"],choices_str,q["correct_answer"],q["explanation"],q["user_answer"],q["is_correct"]))
    conn.commit()
    conn.close()
    return session_id

def get_weak_topics(section_ids):
    conn=get_connection()
    cursor=conn.cursor()
    cursor.execute("""
        SELECT question,correct_answer,COUNT(*) as wrong_count
        FROM questions
        WHERE is_correct=0
        GROUP BY question
        HAVING wrong_count>=1
        ORDER BY wrong_count DESC
        LIMIT 5
    """)
    rows=cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_kb_snapshot():
    conn=get_connection()
    cursor=conn.cursor()
    cursor.execute("""
        SELECT s.id,s.sections,s.created_at,s.total_questions,s.correct_count
        FROM sessions s
        ORDER BY s.id DESC
        LIMIT 5
    """)
    rows=cursor.fetchall()
    conn.close()
    snapshot=[]
    for row in rows:
        snapshot.append({
            "session_id":row["id"],
            "sections":json.loads(row["sections"]),
            "created_at":row["created_at"],
            "total_questions":row["total_questions"],
            "correct_count":row["correct_count"]
        })
    return snapshot

def get_session_questions(session_id):
    conn=get_connection()
    cursor=conn.cursor()
    cursor.execute("SELECT * FROM questions WHERE session_id=?",(session_id,))
    rows=cursor.fetchall()
    conn.close()
    result=[]
    for row in rows:
        result.append({
            "question":row["question"],
            "choices":json.loads(row["choices"]),
            "correct_answer":row["correct_answer"],
            "user_answer":row["user_answer"],
            "is_correct":row["is_correct"],
            "explanation":row["explanation"]
        })
    return result

if __name__=="__main__":
    init_db()
    print("db: ok")
    fake_questions=[
        {"section_id":5,"question":"What is SLATEFALL's mass ceiling?","choices":["A) 100kg","B) 240kg","C) 380kg","D) 500kg"],"correct_answer":"B) 240kg","explanation":"The mass ceiling is 240kg under standard conditions","user_answer":"B) 240kg","is_correct":1},
        {"section_id":5,"question":"What triggers Echo Lock?","choices":["A) Rain","B) Cold","C) Acoustic shock","D) Darkness"],"correct_answer":"C) Acoustic shock","explanation":"Acoustic shock above 145db triggers Echo Lock","user_answer":"A) Rain","is_correct":0}
    ]
    session_id=save_session([5],fake_questions)
    print(f"session_id: {session_id}")
    weak=get_weak_topics([5])
    print(f"weak: {weak}")
    snapshot=get_kb_snapshot()
    print(f"snapshot: {snapshot}")