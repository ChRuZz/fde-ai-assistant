FROM python:3.14-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    BOOKS_DATABASE_PATH=/data/books.db

WORKDIR /app

# 优先复制依赖文件，源代码变化时可复用依赖缓存层。
COPY requirements.txt ./

RUN python -m pip install --no-cache-dir \
    -r requirements.txt

# 生产镜像只复制运行服务需要的文件。
COPY main.py database.py schemas.py ./

# 使用非 root 用户运行，并允许其读写数据库目录。
RUN useradd \
        --create-home \
        --user-group \
        --uid 10001 \
        appuser \
    && mkdir -p /data \
    && chown -R appuser:appuser /app /data

USER appuser

EXPOSE 8000

HEALTHCHECK \
    --interval=30s \
    --timeout=3s \
    --start-period=5s \
    --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)"

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
