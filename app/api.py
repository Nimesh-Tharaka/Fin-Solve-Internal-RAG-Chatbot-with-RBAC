from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.auth import authenticate_user
from app.chatbot import ask_chatbot
from app.logger import log_chat

app = FastAPI()


class LoginRequest(BaseModel):
    username: str
    password: str


class ChatRequest(BaseModel):
    question: str
    role: str
    username: str


@app.get("/")
def root():
    return {"message": "RAG RBAC Chatbot API is running"}


@app.post("/login")
def login(data: LoginRequest):
    user = authenticate_user(data.username, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return user


@app.post("/chat")
def chat(data: ChatRequest):
    result = ask_chatbot(data.question, data.role)

    log_chat(
        username=data.username,
        role=data.role,
        question=data.question,
        answer=result["answer"],
        sources=result["sources"],
        status=result["status"]
    )

    return result