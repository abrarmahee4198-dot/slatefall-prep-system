import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY=os.getenv("GROQ_API_KEY")
GROQ_URL="https://api.groq.com/openai/v1/chat/completions"

def generate_mcqs(section_id:int,section_text:str,weak_topics:list,n:int=5):
    weak_context=""
    if weak_topics:
        weak_list=[w["question"] for w in weak_topics]
        weak_context=f"""
The user has previously answered these questions WRONG in past sessions:
{weak_list}
Focus more questions around these weak areas and similar topics.
Do not repeat the exact same questions but cover the same concepts.
"""

    prompt=f"""
You are a quiz generator. Read the text below and generate exactly {n} multiple choice questions.

{weak_context}

TEXT FROM SECTION {section_id}:
{section_text[:3000]}

Rules:
- Each question must have exactly 4 choices labelled A) B) C) D)
- Only one correct answer per question
- Explanation must be 1-2 sentences max
- Base every question strictly on the text provided

Return ONLY a valid JSON array, no extra text, no markdown, no backticks.
Format exactly like this:
[
  {{
    "question": "question text here?",
    "choices": ["A) option1", "B) option2", "C) option3", "D) option4"],
    "correct_answer": "A) option1",
    "explanation": "brief explanation here"
  }}
]
"""

    body={
        "model":"llama-3.3-70b-versatile",
        "messages":[{"role":"user","content":prompt}],
        "temperature":0.7
    }

    headers={
        "Authorization":f"Bearer {GROQ_API_KEY}",
        "Content-Type":"application/json"
    }

    response=requests.post(GROQ_URL,headers=headers,json=body)
    result=response.json()

    if "error" in result:
        print(f"groq_error: {result['error']['message']}")
        return []

    raw_text=result["choices"][0]["message"]["content"]
    raw_text=raw_text.strip()

    if "```" in raw_text:
        parts=raw_text.split("```")
        for part in parts:
            part=part.strip()
            if part.startswith("json"):
                part=part[4:]
            if part.strip().startswith("["):
                raw_text=part.strip()
                break

    questions=json.loads(raw_text.strip())
    return questions

if __name__=="__main__":
    from pdf_perser import get_section_by_id
    section=get_section_by_id(1)
    if not section:
        print("sec1: not found")
        exit()
    questions=generate_mcqs(1,section["content"],[],3)
    if questions:
        print(f"questions: {len(questions)}")
        for i,q in enumerate(questions):
            print(f"Q{i+1}: {q['question']}")
            for choice in q["choices"]:
                print(f"  {choice}")
            print(f"  ans: {q['correct_answer']}")
    else:
        print("questions: none returned")