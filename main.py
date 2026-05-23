from fastapi import FastAPI,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from pdf_perser import get_all_sections,get_section_by_id,get_section_list
from database import init_db,save_session,get_weak_topics,get_kb_snapshot,get_session_questions
from llm_service import generate_mcqs

app=FastAPI(title="Slatefall Prep System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

init_db()

class StartSessionRequest(BaseModel):
    section_ids:list[int]
    n_per_section:int=5

class SubmitAnswersRequest(BaseModel):
    session_id:int
    answers:list[dict]

@app.get("/sections")
def list_sections():
    sections=get_section_list()
    return{"sections":sections}

@app.get("/sections/{section_id}")
def get_section(section_id:int):
    section=get_section_by_id(section_id)
    if not section:
        raise HTTPException(status_code=404,detail=f"section {section_id} not found")
    return{"section_id":section_id,"title":section["title"],"content":section["content"]}

@app.post("/start-session")
def start_session(request:StartSessionRequest):
    all_questions=[]
    weak_topics=get_weak_topics(request.section_ids)
    for section_id in request.section_ids:
        section=get_section_by_id(section_id)
        if not section:
            continue
        questions=generate_mcqs(
            section_id=section_id,
            section_text=section["content"],
            weak_topics=weak_topics,
            n=request.n_per_section
        )
        for q in questions:
            q["section_id"]=section_id
            q["user_answer"]=""
            q["is_correct"]=0
        all_questions.extend(questions)
    if not all_questions:
        raise HTTPException(status_code=500,detail="failed to generate questions")
    return{
        "section_ids":request.section_ids,
        "weak_topics_found":len(weak_topics),
        "total_questions":len(all_questions),
        "questions":all_questions
    }

@app.post("/submit-answers")
def submit_answers(request:SubmitAnswersRequest):
    if not request.answers:
        raise HTTPException(status_code=400,detail="no answers provided")
    scored=[]
    for q in request.answers:
        is_correct=1 if q["user_answer"]==q["correct_answer"] else 0
        scored.append({
            "section_id":q.get("section_id",0),
            "question":q["question"],
            "choices":q["choices"],
            "correct_answer":q["correct_answer"],
            "explanation":q["explanation"],
            "user_answer":q["user_answer"],
            "is_correct":is_correct
        })
    section_ids=list(set(q["section_id"] for q in scored))
    session_id=save_session(section_ids,scored)
    correct_count=sum(q["is_correct"] for q in scored)
    total=len(scored)
    score_percent=round((correct_count/total)*100)
    wrong=[]
    for q in scored:
        if not q["is_correct"]:
            wrong.append({
                "question":q["question"],
                "your_answer":q["user_answer"],
                "correct_answer":q["correct_answer"],
                "explanation":q["explanation"]
            })
    return{
        "session_id":session_id,
        "score":f"{correct_count}/{total}",
        "percentage":score_percent,
        "wrong_answers":wrong
    }

@app.get("/history")
def get_history():
    snapshot=get_kb_snapshot()
    return{"sessions":snapshot}

@app.get("/history/{session_id}")
def get_session_detail(session_id:int):
    questions=get_session_questions(session_id)
    if not questions:
        raise HTTPException(status_code=404,detail=f"session {session_id} not found")
    return{"session_id":session_id,"questions":questions}

@app.get("/weak-topics")
def weak_topics(section_ids:list[int]=[]):
    if not section_ids:
        return{"weak_topics":[]}
    topics=get_weak_topics(section_ids)
    return{"weak_topics":topics}