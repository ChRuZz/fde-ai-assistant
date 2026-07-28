import os
import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


# 在导入项目模块前设置测试数据库路径。
# main.py 导入时会执行 init_database()，
# 因此必须提前确保它使用临时数据库，而不是正式 books.db。
_TEMP_DIRECTORY = tempfile.TemporaryDirectory(
    prefix="fde-book-api-tests-"
)
TEST_DATABASE_PATH = (
    Path(_TEMP_DIRECTORY.name) / "test_books.db"
)

os.environ["BOOKS_DATABASE_PATH"] = str(
    TEST_DATABASE_PATH
)


from database import DATABASE_PATH, init_database
from main import app


# 防止配置错误导致测试污染正式数据库。
if DATABASE_PATH != TEST_DATABASE_PATH:
    raise RuntimeError(
        "测试数据库配置失败，已停止执行测试"
    )


@pytest.fixture(autouse=True)
def reset_database() -> Generator[None, None, None]:
    """
    每个测试开始前重建数据库。

    这样每个测试都从相同的三本初始图书开始，
    不会受到其他测试新增或修改数据的影响。
    """
    if TEST_DATABASE_PATH.exists():
        TEST_DATABASE_PATH.unlink()

    init_database()

    yield

    if TEST_DATABASE_PATH.exists():
        TEST_DATABASE_PATH.unlink()


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """提供 FastAPI 测试客户端。"""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(
    scope="session",
    autouse=True,
)
def cleanup_test_directory() -> Generator[
    None,
    None,
    None,
]:
    """全部测试结束后删除临时目录。"""
    yield
    _TEMP_DIRECTORY.cleanup()
