# Slatefall Adaptive Prep System

Reads the SLATEFALL PDF, generates MCQs using Groq LLM,
tracks performance, and adapts questions to weak areas.

## Setup

1. Clone repo
2. Create venv and activate it
3. Run pip install -r requirements.txt
4. Create .env file with GROQ_API_KEY=key
5. Place SLATEFALL_DOSSIER.pdf in root folder

## Run:
Start server:Run the command bellow

uvicorn main:app --reload
## Scenario B: Run these commands bellow
del DB.db

python scenario_b.py

## Additional Documentation

**System_Working_Procedure.txt** — step by step explanation of 
how each file works, what methods they have, and how data flows 
through the system.

**My_Choices_and_Thinking.txt** — explains every technical 
decision made during the project and the reasoning behind each 
choice.
