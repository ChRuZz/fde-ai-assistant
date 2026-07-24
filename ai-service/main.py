from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from database import get_connection, init_database


# 每次服务启动时检查并初始化数据库
# CREATE TABLE IF NOT EXISTS 不会重复创建表
# 只有表为空时才会插入初始数据
init_database()


app = FastAPI(
    title="FDE AI Assistant",
    description="智能图书管理系统的 AI 服务",
    version="0.3.0",
)


# /ask 接收的请求格式
class AskRequest(BaseModel):
    question: str = Field(
        min_length=1,
        max_length=200,
        description="用户提出的问题",
    )


# /ask 返回的响应格式
class AskResponse(BaseModel):
    question: str
    answer: str
    sources: list[str]


# 图书响应模型
class Book(BaseModel):
    id: int
    title: str
    author: str
    available: bool


@app.get("/")
def root():
    return {
        "service": "fde-ai-assistant",
        "message": "AI service is running",
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
    }


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):
    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="问题内容不能为空",
        )

    return AskResponse(
        question=question,
        answer=f"这是对“{question}”的模拟回答。",
        sources=[],
    )


# 查询全部图书，或根据关键词搜索
@app.get("/books", response_model=list[Book])
def list_books(
    keyword: str | None = Query(
        default=None,
        min_length=1,
        max_length=50,
        description="按书名或作者搜索",
    ),
):
    with get_connection() as connection:
        if keyword is None:
            rows = connection.execute(
                """
                SELECT id, title, author, available
                FROM books
                ORDER BY id
                """
            ).fetchall()
        else:
            normalized_keyword = keyword.strip()

            if not normalized_keyword:
                raise HTTPException(
                    status_code=400,
                    detail="搜索关键词不能为空",
                )

            search_value = f"%{normalized_keyword}%"

            rows = connection.execute(
                """
                SELECT id, title, author, available
                FROM books
                WHERE title LIKE ?
                   OR author LIKE ?
                ORDER BY id
                """,
                (search_value, search_value),
            ).fetchall()

    return [
        Book(
            id=row["id"],
            title=row["title"],
            author=row["author"],
            available=bool(row["available"]),
        )
        for row in rows
    ]


# 根据 ID 查询单本图书
@app.get("/books/{book_id}", response_model=Book)
def get_book(book_id: int):
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT id, title, author, available
            FROM books
            WHERE id = ?
            """,
            (book_id,),
        ).fetchone()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="图书不存在",
        )

    return Book(
        id=row["id"],
        title=row["title"],
        author=row["author"],
        available=bool(row["available"]),
    )
