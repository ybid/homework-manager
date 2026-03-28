# 作业管理系统 - 后端服务

基于 Python + FastAPI 的作业管理后端 API。

## 技术栈

- **框架:** FastAPI
- **ORM:** SQLAlchemy 2.0
- **数据库:** MySQL 8.0
- **缓存:** Redis
- **定时任务:** APScheduler
- **部署:** Docker + Gunicorn + Uvicorn

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env`，修改配置：

```bash
cp .env.example .env
```

### 3. 初始化数据库

确保 MySQL 已运行，执行初始化脚本：

```bash
mysql -u root -p < scripts/init-db.sql
```

### 4. 启动服务

```bash
uvicorn app.main:app --host 0.0.0.0 --port 3000 --reload
```

服务默认运行在 `http://localhost:3000`

## API 文档

启动服务后访问：
- Swagger UI: http://localhost:3000/docs
- ReDoc: http://localhost:3000/redoc

## API 接口

### 用户模块
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/v1/auth/login | 微信登录 |
| GET | /api/v1/user/info | 获取用户信息 |
| PUT | /api/v1/user/info | 更新用户信息 |

### 作业模块
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/homeworks | 作业列表 |
| GET | /api/v1/homeworks/today | 今日作业 |
| GET | /api/v1/homeworks/calendar | 日历数据 |
| POST | /api/v1/homeworks | 创建作业 |
| PUT | /api/v1/homeworks/:id | 更新作业 |
| DELETE | /api/v1/homeworks/:id | 删除作业 |

### 积分模块
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/v1/points/complete/:id | 完成打卡 |
| GET | /api/v1/points/stats | 积分统计 |
| GET | /api/v1/points/logs | 积分流水 |

### 奖品模块
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/rewards | 奖品列表 |
| POST | /api/v1/rewards/:id/exchange | 兑换奖品 |
| GET | /api/v1/rewards/exchanges | 兑换记录 |

### 管理模块
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/v1/admin/rewards | 创建奖品 |
| PUT | /api/v1/admin/rewards/:id | 更新奖品 |
| DELETE | /api/v1/admin/rewards/:id | 删除奖品 |

## 项目结构

```
backend/
├── app/
│   ├── api/           # API 路由
│   ├── core/          # 核心配置
│   ├── models/        # 数据库模型
│   ├── schemas/       # Pydantic 模型
│   ├── services/      # 业务逻辑
│   └── main.py        # 入口
├── scripts/           # 脚本
├── docker/            # Docker配置
├── requirements.txt   # 依赖
└── .env              # 环境变量
```

## 定时任务

- **00:05** - 积分过期处理
- **23:55** - 未完成惩罚扣分
