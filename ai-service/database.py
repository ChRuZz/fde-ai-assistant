import os
from pathlib import Path
import sqlite3


BASE_DIR = Path(__file__).resolve().parent

# 默认使用项目目录下的 books.db。
# 测试时可以通过环境变量切换到独立测试数据库。
DATABASE_PATH = Path(
    os.environ.get(
        "BOOKS_DATABASE_PATH",
        str(BASE_DIR / "books.db"),
    )
)


def get_connection() -> sqlite3.Connection:
    """创建并返回数据库连接。"""

    connection = sqlite3.connect(
        DATABASE_PATH,
        timeout=5.0,
    )

    # 查询结果支持 row["title"] 形式访问。
    connection.row_factory = sqlite3.Row

    # 为后续可能添加的关联表启用外键约束。
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def init_database() -> None:
    """创建图书表，并在空表中写入初始数据。"""

    DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                available INTEGER NOT NULL DEFAULT 1
                    CHECK (available IN (0, 1))
            )
            """
        )

        # 数据库层面阻止完全相同的书名和作者被重复添加。
        connection.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS
                idx_books_unique_title_author
            ON books (title, author)
            """
        )

        book_count = connection.execute(
            "SELECT COUNT(*) FROM books"
        ).fetchone()[0]

        if book_count == 0:
            connection.executemany(
                """
                INSERT INTO books (
                    id,
                    title,
                    author,
                    available
                )
                VALUES (?, ?, ?, ?)
                """,
                [
                    (
                        1,
                        "Python 编程：从入门到实践",
                        "Eric Matthes",
                        1,
                    ),
                    (
                        2,
                        "深入理解计算机系统",
                        "Randal E. Bryant",
                        0,
                    ),
                    (
                        3,
                        "Java 核心技术",
                        "Cay S. Horstmann",
                        1,
                    ),
                ],
            )


if __name__ == "__main__":
    init_database()
    print(f"数据库初始化完成：{DATABASE_PATH}")
