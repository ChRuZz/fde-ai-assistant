from fastapi.testclient import TestClient


def test_list_books_returns_initial_books(
    client: TestClient,
) -> None:
    """查询全部图书时，返回三本初始图书。"""
    response = client.get("/books")

    assert response.status_code == 200

    books = response.json()

    assert len(books) == 3
    assert [book["id"] for book in books] == [
        1,
        2,
        3,
    ]
    assert books[0] == {
        "id": 1,
        "title": "Python 编程：从入门到实践",
        "author": "Eric Matthes",
        "available": True,
    }


def test_get_existing_book(
    client: TestClient,
) -> None:
    """根据存在的 ID 查询图书。"""
    response = client.get("/books/1")

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "title": "Python 编程：从入门到实践",
        "author": "Eric Matthes",
        "available": True,
    }


def test_get_missing_book_returns_404(
    client: TestClient,
) -> None:
    """查询不存在的图书时返回 404。"""
    response = client.get("/books/99999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "图书不存在",
    }


def test_create_book(
    client: TestClient,
) -> None:
    """新增图书成功时返回 201 和完整图书信息。"""
    response = client.post(
        "/books",
        json={
            "title": "计算机网络",
            "author": "谢希仁",
            "available": True,
        },
    )

    assert response.status_code == 201
    assert response.json() == {
        "id": 4,
        "title": "计算机网络",
        "author": "谢希仁",
        "available": True,
    }

    query_response = client.get("/books/4")

    assert query_response.status_code == 200
    assert query_response.json()["title"] == "计算机网络"


def test_create_duplicate_book_returns_409(
    client: TestClient,
) -> None:
    """相同书名和作者不能重复添加。"""
    payload = {
        "title": "计算机网络",
        "author": "谢希仁",
        "available": True,
    }

    first_response = client.post(
        "/books",
        json=payload,
    )
    second_response = client.post(
        "/books",
        json=payload,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json() == {
        "detail": "相同书名和作者的图书已经存在",
    }


def test_create_book_rejects_blank_title(
    client: TestClient,
) -> None:
    """空白书名不能通过请求模型校验。"""
    response = client.post(
        "/books",
        json={
            "title": "   ",
            "author": "测试作者",
            "available": True,
        },
    )

    assert response.status_code == 422


def test_create_book_rejects_non_boolean_value(
    client: TestClient,
) -> None:
    """StrictBool 拒绝使用数字代替布尔值。"""
    response = client.post(
        "/books",
        json={
            "title": "测试图书",
            "author": "测试作者",
            "available": 1,
        },
    )

    assert response.status_code == 422


def test_update_book_availability(
    client: TestClient,
) -> None:
    """可以修改图书的可借状态。"""
    response = client.patch(
        "/books/1/availability",
        json={
            "available": False,
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "title": "Python 编程：从入门到实践",
        "author": "Eric Matthes",
        "available": False,
    }

    query_response = client.get("/books/1")

    assert query_response.status_code == 200
    assert query_response.json()["available"] is False


def test_update_missing_book_returns_404(
    client: TestClient,
) -> None:
    """修改不存在的图书时返回 404。"""
    response = client.patch(
        "/books/99999/availability",
        json={
            "available": False,
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "图书不存在",
    }


def test_filter_books_by_keyword_and_availability(
    client: TestClient,
) -> None:
    """关键词和可借状态可以组合筛选。"""
    response = client.get(
        "/books",
        params={
            "keyword": "Python",
            "available": True,
        },
    )

    assert response.status_code == 200

    books = response.json()

    assert len(books) == 1
    assert books[0]["id"] == 1
    assert books[0]["available"] is True


def test_filter_unavailable_books(
    client: TestClient,
) -> None:
    """可以只查询不可借图书。"""
    response = client.get(
        "/books",
        params={
            "available": False,
        },
    )

    assert response.status_code == 200

    books = response.json()

    assert [book["id"] for book in books] == [2]
    assert all(
        book["available"] is False
        for book in books
    )


def test_book_pagination(
    client: TestClient,
) -> None:
    """limit 和 offset 能正确进行分页。"""
    create_response = client.post(
        "/books",
        json={
            "title": "算法导论",
            "author": "Thomas H. Cormen",
            "available": False,
        },
    )

    assert create_response.status_code == 201

    first_page = client.get(
        "/books",
        params={
            "limit": 2,
            "offset": 0,
        },
    )
    second_page = client.get(
        "/books",
        params={
            "limit": 2,
            "offset": 2,
        },
    )

    assert first_page.status_code == 200
    assert second_page.status_code == 200

    assert [
        book["id"]
        for book in first_page.json()
    ] == [1, 2]

    assert [
        book["id"]
        for book in second_page.json()
    ] == [3, 4]


def test_invalid_pagination_parameters(
    client: TestClient,
) -> None:
    """非法分页参数由 FastAPI 返回 422。"""
    invalid_limit = client.get(
        "/books",
        params={
            "limit": 0,
        },
    )
    invalid_offset = client.get(
        "/books",
        params={
            "offset": -1,
        },
    )
    excessive_limit = client.get(
        "/books",
        params={
            "limit": 101,
        },
    )

    assert invalid_limit.status_code == 422
    assert invalid_offset.status_code == 422
    assert excessive_limit.status_code == 422


def test_blank_keyword_returns_400(
    client: TestClient,
) -> None:
    """只有空格的关键词由业务代码返回 400。"""
    response = client.get(
        "/books",
        params={
            "keyword": "   ",
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "搜索关键词不能为空",
    }


def test_sql_injection_input_is_treated_as_data(
    client: TestClient,
) -> None:
    """疑似 SQL 注入内容只能作为普通关键词处理。"""
    response = client.get(
        "/books",
        params={
            "keyword": "' OR 1=1--",
        },
    )

    assert response.status_code == 200
    assert response.json() == []


def test_database_is_reset_between_tests(
    client: TestClient,
) -> None:
    """当前测试应从固定的三本初始图书开始。"""
    response = client.get("/books")

    assert response.status_code == 200
    assert len(response.json()) == 3
