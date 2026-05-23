import json
import os
import random
from pdf_parser import get_section_by_id
from database import init_db,save_session,get_weak_topics,get_kb_snapshot
from llm_service import generate_mcqs

def simulate_answers(questions):
    for q in questions:
        if random.random()>0.5:
            q["user_answer"]=q["correct_answer"]
            q["is_correct"]=1
        else:
            wrong_choices=[c for c in q["choices"] if c!=q["correct_answer"]]
            q["user_answer"]=random.choice(wrong_choices)
            q["is_correct"]=0
    return questions

def run_iteration(section_ids,output_folder,iter_num,n_per_section=5):
    print(f"iter: {section_ids}")
    weak_topics=get_weak_topics(section_ids)
    print(f"weak: {len(weak_topics)}")
    all_questions=[]
    for sid in section_ids:
        section=get_section_by_id(sid)
        if not section:
            print(f"sec{sid}: not found")
            continue
        print(f"mcqs: sec{sid}")
        questions=generate_mcqs(sid,section["content"],weak_topics,n_per_section)
        for q in questions:
            q["section_id"]=sid
        all_questions.extend(questions)
    all_questions=simulate_answers(all_questions)
    correct=sum(1 for q in all_questions if q["is_correct"])
    print(f"score: {correct}/{len(all_questions)}")
    session_id=save_session(section_ids,all_questions)
    print(f"session_id: {session_id}")
    os.makedirs(output_folder,exist_ok=True)
    questions_file={
        "session_id":session_id,
        "sections":section_ids,
        "weak_topics_used":weak_topics,
        "total_questions":len(all_questions),
        "correct":correct,
        "questions":all_questions
    }
    with open(f"{output_folder}/questions_iter{iter_num}.json","w") as f:
        json.dump(questions_file,f,indent=2)
    snapshot=get_kb_snapshot()
    with open(f"{output_folder}/kb_snapshot_iter{iter_num}.json","w") as f:
        json.dump(snapshot,f,indent=2)
    print(f"saved: {output_folder}")

init_db()
print("scenario_b: start")
run_iteration([5,8],"outputs/scenario_b_iter1",1)
run_iteration([6,8,9],"outputs/scenario_b_iter2",2)
run_iteration([8],"outputs/scenario_b_iter3",3)
print("scenario_b: done")