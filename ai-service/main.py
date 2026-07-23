from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field


app = FastAPI(
    title="FDE AI Assistant",
    description="智能图书管理系统的 AI 服务",
    version="0.2.0",
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


# 临时图书数据，后续会替换为数据库
BOOKS = [
    Book(
        id=1,
        title="Python 编程：从入门到实践",
        author="Eric Matthes",
        available=True,
    ),
    Book(
        id=2,
        title="深入理解计算机系统",
        author="Randal E. Bryant",
        available=False,
    ),
    Book(
        id=3,
        title="Java 核心技术",
        author="Cay S. Horstmann",
        available=True,
    ),
]

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
    # 去掉问题首尾的空格
    question = request.question.strip()

    # 拦截只包含空格的问题
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

# 查询图书列表
@app.get("/books", response_model=list[Book])
def list_books(
    keyword: str | None = Query(
        default=None,
        min_length=1,
        max_length=50,
        description="按书名或作者搜索",
    ),
):
    # 没有关键词时返回全部图书
    if keyword is None:
        return BOOKS

    normalized_keyword = keyword.strip().lower()

    # 搜索书名或作者
    return [
        book
        for book in BOOKS
        if normalized_keyword in book.title.lower()
        or normalized_keyword in book.author.lower()
    ]


# 根据 ID 查询单本图书
@app.get("/books/{book_id}", response_model=Book)
def get_book(book_id: int):
    for book in BOOKS:
        if book.id == book_id:
            return book

    raise HTTPException(
        status_code=404,
        detail="图书不存在",
    )
