# 作业管理系统 - 后端服务

微信小程序后端，用户通过完成作业打卡获得积分，积分可兑换奖品。

## 技术栈

- **Python 3.11 + FastAPI** — Web 框架
- **MySQL 8.0 + SQLAlchemy** — 数据库 & ORM
- **Redis** — 缓存 & 限流
- **Alembic** — 数据库迁移
- **APScheduler** — 定时任务
- **Docker Compose** — 容器化部署

## 项目结构

```
homework-server/
├── app/
│   ├── main.py              # FastAPI 入口
│   ├── config.py            # 配置
│   ├── database.py          # SQLAlchemy 引擎
│   ├── redis_client.py      # Redis 连接
│   ├── models/              # 数据模型
│   ├── schemas/             # Pydantic 模型
│   ├── api/                 # 路由
│   ├── services/            # 业务逻辑
│   ├── middleware/           # 中间件
│   └── utils/               # 工具函数
├── alembic/                 # 数据库迁移
├── scripts/                 # 脚本
├── docker-compose.yml
├── Dockerfile
└── nginx.conf
```

## 本地开发

### 1. 环境准备

确保已安装 Python 3.10+、MySQL 8.0、Redis。

### 2. 安装依赖

```bash
cd homework-server
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 填入实际配置
```

### 4. 初始化数据库

```bash
# 方式一：使用 Alembic 迁移
alembic revision --autogenerate -m "init"
alembic upgrade head

# 方式二：使用初始化脚本（含种子数据）
python -m scripts.init_db
```

### 5. 启动服务

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

访问 API 文档：http://localhost:8000/docs

## Docker 部署

### 1. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，特别注意：
# - MYSQL_HOST=mysql（Docker 网络内使用服务名）
# - REDIS_HOST=redis
# - JWT_SECRET 改为随机字符串
# - 填入微信小程序 APP_ID 和 APP_SECRET
```

### 2. 启动服务

```bash
docker-compose up -d --build
```

### 3. 初始化数据库（首次部署）

```bash
# Alembic 迁移在 api 容器启动时自动执行
# 如需种子数据：
docker-compose exec api python -m scripts.init_db
```

### 4. 查看日志

```bash
docker-compose logs -f api
```

### 5. 停止服务

```bash
docker-compose down
```

## API 接口

### 认证
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/v1/auth/login | 微信登录 |

### 用户
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/user/info | 获取用户信息 |
| PUT | /api/v1/user/info | 更新用户信息 |

### 作业
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/homeworks | 作业列表 |
| GET | /api/v1/homeworks/{id} | 作业详情 |
| POST | /api/v1/homeworks | 创建作业 |
| PUT | /api/v1/homeworks/{id} | 更新作业 |
| DELETE | /api/v1/homeworks/{id} | 删除作业 |
| POST | /api/v1/homeworks/{id}/complete | 完成打卡 |
| GET | /api/v1/homeworks/today | 今日待完成 |
| GET | /api/v1/homeworks/calendar | 月度日历 |

### 积分
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/points/stats | 积分统计 |
| GET | /api/v1/points/logs | 积分流水 |

### 奖品
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/rewards | 奖品列表 |
| POST | /api/v1/rewards/{id}/exchange | 兑换奖品 |
| GET | /api/v1/exchanges | 兑换记录 |

### 管理员
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/v1/admin/rewards | 创建奖品 |
| PUT | /api/v1/admin/rewards/{id} | 更新奖品 |
| DELETE | /api/v1/admin/rewards/{id} | 删除奖品 |
| POST | /api/v1/admin/points/adjust | 调整积分 |
| GET | /api/v1/admin/users | 用户列表 |
| GET | /api/v1/admin/stats | 统计数据 |

### 健康检查
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /health | DB + Redis 健康检查 |

## 统一响应格式

成功：
```json
{
  "code": 0,
  "message": "success",
  "data": { ... }
}
```

分页：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [...],
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total": 100,
      "total_pages": 5
    }
  }
}
```

错误：
```json
{
  "code": 10001,
  "message": "错误描述",
  "data": null
}
```

## 定时任务

| 时间 | 任务 | 说明 |
|------|------|------|
| 每天 00:05 | expire_points | 处理过期积分 |
| 每天 23:55 | penalize_incomplete | 未完成作业惩罚扣分 |

## License

MIT
