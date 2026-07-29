# FDE AI Assistant

## 目标用户

学校图书馆工作人员和学生。

## 用户问题

图书馆规章、图书信息和借阅数据分散，用户查询效率低，工作人员需要重复回答相似问题。

## 系统目标

构建一个智能知识库与业务助手，帮助用户查询图书馆规定、搜索图书，并完成部分业务信息查询。

## 核心功能

1. 用户登录和权限管理。
2. 文档知识库问答，并显示回答来源。
3. 查询图书信息和借阅状态。

## 成功标准

1. 用户能够正常登录并使用对应权限。
2. 系统能够根据上传文档回答问题。
3. 回答能够显示引用来源。
4. 图书查询接口能够正常返回结果。
5. 项目能够通过 Docker 一键启动。

## 使用 Docker 启动 AI 服务

构建并启动服务：

```bash
docker compose up -d --build
```

查看容器状态：

```bash
docker compose ps
```

测试服务：

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/books
```

查看日志：

```bash
docker compose logs -f ai-service
```

停止并删除容器：

```bash
docker compose down
```

SQLite 数据保存在名为 `fde-ai-service-data` 的 Docker Volume 中。普通的
`docker compose down` 不会删除数据卷；只有明确需要删除全部数据库数据时，
才使用 `docker compose down -v`。
