from pathlib import Path
import sqlite3


# 数据库文件保存在 ai-service 目录
BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "books.db"


def get_connection() -> sqlite3.Connection:
    """创建并返回数据库连接。"""
    connection = sqlite3.connect(DATABASE_PATH)

    # 查询结果可以通过字段名读取，而不只是下标
    connection.row_factory = sqlite3.Row
    return connection


def init_database() -> None:
    """创建 books 表，并在表为空时写入初始数据。"""
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                available INTEGER NOT NULL
                    CHECK (available IN (0, 1))
            )
            """
        )

        book_count = connection.execute(
            "SELECT COUNT(*) FROM books"
        ).fetchone()[0]

        # 只有空表才插入，避免每次启动都重复添加
        if book_count == 0:
            connection.executemany(
                """
                INSERT INTO books (id, title, author, available)
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
