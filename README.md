# UPDG 一站式项目数字化运营管理平台

> 银行级项目管理平台 | FastAPI + Vue3

## 项目概述

面向银行 UPDG 的一站式项目数字化运营管理平台，覆盖项目全生命周期管理、人力外包资源池、成本自动核算、AI 辅助文档生成等核心能力。

## 技术栈

| 层级 | 技术选型 |
|------|---------|
| 后端 | FastAPI 0.110+, Uvicorn (async) |
| ORM | SQLAlchemy 2.0 async + asyncpg |
| 数据库 | PostgreSQL 16 (prod) / SQLite (dev) |
| 缓存/队列 | Redis 7 + Celery 5.3 |
| 存储 | MinIO |
| 迁移 | Alembic 1.13 |
| 前端 | Vue 3.4, Vite 5.2, Element Plus 2.6, Pinia 2.1 |
| 安全 | JWT + SM3 密码哈希 |
| 部署 | Docker Compose, K8s |

## 快速开始

### 后端

```bash
cd python-backend

# 启动基础设施 (PostgreSQL, Redis, MinIO)
docker compose up -d

# 初始化数据库
python init_db.py

# 启动开发服务器
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

## 开发规范

- Python 代码遵循 ruff 格式化规则
- 前端遵循 Vue 官方规范
- 所有接口返回统一格式 `{code: "SUCCESS", message, data}`
- 敏感数据禁止硬编码
- 单元测试覆盖率 >= 80%

## 许可证

版权所有 © 2026
