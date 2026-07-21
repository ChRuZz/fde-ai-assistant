from fastapi import FastAPI
from pydantic import BaseModel


# 创建 FastAPI 应用对象
app = FastAPI(
    title="FDE AI Assistant",
    description="智能图书管理系统的 AI 服务",
    version="0.1.0",
)


# 定义 POST /ask 接口接收的数据格式
class AskRequest(BaseModel):
    question: str


# 根接口
@app.get("/")
def root():
    return {
        "service": "fde-ai-assistant",
        "message": "AI service is running",
    }


# 健康检查接口
@app.get("/health")
def health():
    return {
        "status": "ok",
    }


# 模拟问答接口
@app.post("/ask")
def ask(request: AskRequest):
    return {
        "question": request.question,
        "answer": f"这是对“{request.question}”的模拟回答。",
        "sources": [],
    }
