import sqlite3
from typing import Annotated

from fastapi import FastAPI, HTTPException, Path, Query, status
from pydantic import BaseModel, Field

from database import get_connection, init_database
from schemas import Book, BookAvailabilityUpdate, BookCreate


init_database()


app = FastAPI(
    title="FDE AI Assistant",
    description="智能图书管理系统的 AI 服务",
    version="0.5.0",
)


PositiveBookId = Annotated[
    int,
    Path(
        gt=0,
        description="图书 ID，必须是正整数",
    ),
]


class AskRequest(BaseModel):
    question: str = Field(
        min_length=1,
        max_length=200,
        description="用户提出的问题",
    )


class AskResponse(BaseModel):
    question: str
    answer: str
    sources: list[str]


def row_to_book(row: sqlite3.Row) -> Book:
    """将 SQLite 查询结果转换为图书响应模型。"""

    return Book(
        id=row["id"],
        title=row["title"],
        author=row["author"],
        available=bool(row["available"]),
    )


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


@app.get("/books", response_model=list[Book])
def list_books(
    keyword: str | None = Query(
        default=None,
        min_length=1,
        max_length=50,
        description="按书名或作者搜索",
    ),
    available: bool | None = Query(
        default=None,
        description="按可借状态筛选",
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
        description="单次最多返回的图书数量",
    ),
    offset: int = Query(
        default=0,
        ge=0,
        description="跳过的图书数量",
    ),
):
    sql = """
        SELECT id, title, author, available
        FROM books
    """

    conditions: list[str] = []
    parameters: list[object] = []

    if keyword is not None:
        normalized_keyword = keyword.strip()

        if not normalized_keyword:
            raise HTTPException(
                status_code=400,
                detail="搜索关键词不能为空",
            )

        search_value = f"%{normalized_keyword}%"

        conditions.append(
            "(title LIKE ? OR author LIKE ?)"
        )
        parameters.extend(
            [
                search_value,
                search_value,
            ]
        )

    if available is not None:
        conditions.append("available = ?")
        parameters.append(int(available))

    if conditions:
        sql += " WHERE " + " AND ".join(conditions)

    sql += """
        ORDER BY id
        LIMIT ?
        OFFSET ?
    """

    parameters.extend(
        [
            limit,
            offset,
        ]
    )

    with get_connection() as connection:
        rows = connection.execute(
            sql,
            parameters,
        ).fetchall()

    return [row_to_book(row) for row in rows]


@app.get("/books/{book_id}", response_model=Book)
def get_book(book_id: PositiveBookId):
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

    return row_to_book(row)


@app.post(
    "/books",
    response_model=Book,
    status_code=status.HTTP_201_CREATED,
)
def create_book(request: BookCreate):
    try:
        with get_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO books (
                    title,
                    author,
                    available
                )
                VALUES (?, ?, ?)
                """,
                (
                    request.title,
                    request.author,
                    int(request.available),
                ),
            )

            new_book_id = cursor.lastrowid

            if new_book_id is None:
                raise HTTPException(
                    status_code=500,
                    detail="新增图书失败",
                )

            row = connection.execute(
                """
                SELECT id, title, author, available
                FROM books
                WHERE id = ?
                """,
                (new_book_id,),
            ).fetchone()

    except sqlite3.IntegrityError as exc:
        raise HTTPException(
            status_code=409,
            detail="相同书名和作者的图书已经存在",
        ) from exc

    if row is None:
        raise HTTPException(
            status_code=500,
            detail="新增图书后无法读取数据",
        )

    return row_to_book(row)


@app.patch(
    "/books/{book_id}/availability",
    response_model=Book,
)
def update_book_availability(
    book_id: PositiveBookId,
    request: BookAvailabilityUpdate,
):
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE books
            SET available = ?
            WHERE id = ?
            """,
            (
                int(request.available),
                book_id,
            ),
        )

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

    return row_to_book(row)
