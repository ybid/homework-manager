# 作业管理系统技术方案

## 文档信息

| 字段 | 内容 |
|------|------|
| 项目名称 | 作业管理系统（小程序） |
| 版本号 | v1.1 |
| 作者 | architect-agent |
| 创建日期 | 2026-03-27 |
| 更新日期 | 2026-03-27 |
| PRD 关联 | PRD.md |

---

## 1. 概述

### 1.1 背景
基于 PRD 文档，设计作业管理系统的技术架构。系统采用微信小程序 + 自建后端服务模式，部署在自有服务器上。

### 1.2 目标
- 高可用、易扩展的架构设计
- 清晰的数据模型
- 规范的接口定义
- 良好的性能表现
- 支持后期扩展

### 1.3 技术选型

| 层级 | 技术选型 | 选型理由 |
|------|----------|----------|
| 前端 | 微信小程序原生 | 性能好、开发成本低、官方支持 |
| 后端 | Python 3.11 + FastAPI | 高性能异步框架、类型安全、自动生成API文档 |
| 数据库 | MySQL 8.0 | 稳定可靠、事务支持好、运维成熟 |
| 缓存 | Redis | 高性能缓存、支持分布式锁 |
| 对象存储 | MinIO / 阿里云 OSS | 图片存储 |
| 部署 | Docker + Nginx | 容器化部署、便于扩展 |

---

## 2. 整体架构

### 2.1 架构图

```
┌─────────────────────────────────────────────────────────────────────┐
│                           微信小程序端                               │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐                   │
│  │ 首页    │ │ 积分页  │ │ 兑换页  │ │ 我的页  │                   │
│  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘                   │
│       │           │           │           │                        │
│       └───────────┴─────┬─────┴───────────┘                        │
│                         │                                            │
│                    HTTPS API                                        │
└─────────────────────────┼───────────────────────────────────────────┘
                          │
                    ┌─────▼─────┐
                    │   Nginx   │ (反向代理 + SSL)
                    │  :443     │
                    └─────┬─────┘
                          │
┌─────────────────────────┼───────────────────────────────────────────┐
│                     自建服务器                                        │
│                         │                                            │
│                   ┌─────▼─────┐                                      │
│                   │  FastAPI  │                                      │
│                   │  API服务  │                                      │
│                   │  :8000    │                                      │
│                   └─────┬─────┘                                      │
│                         │                                            │
│    ┌────────────────────┼────────────────────┐                      │
│    │                    │                    │                      │
│ ┌──▼──┐           ┌─────▼─────┐         ┌───▼───┐                  │
│ │用户 │           │   业务    │         │ 定时  │                  │
│ │服务 │           │   服务    │         │ 任务  │                  │
│ └──┬──┘           └─────┬─────┘         └───┬───┘                  │
│    │                    │                    │                      │
│    └────────────────────┼────────────────────┘                      │
│                         │                                            │
│    ┌────────────────────┼────────────────────┐                      │
│    │                    │                    │                      │
│ ┌──▼────┐          ┌────▼────┐          ┌───▼───┐                 │
│ │ MySQL │          │  Redis  │          │ MinIO │                 │
│ │ :3306 │          │  :6379  │          │ :9000 │                 │
│ └───────┘          └─────────┘          └───────┘                 │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 模块划分

| 模块 | 职责 | 技术栈 |
|------|------|--------|
| 小程序端 | UI 展示、用户交互 | 微信小程序原生 |
| API 网关 | 路由、限流、鉴权 | Nginx |
| 用户服务 | 用户注册、登录、权限 | FastAPI |
| 作业服务 | 作业 CRUD、打卡 | FastAPI |
| 积分服务 | 积分获取、消耗、统计 | FastAPI |
| 奖品服务 | 奖品管理、兑换 | FastAPI |
| 定时任务 | 积分过期、惩罚扣分 | APScheduler |
| 缓存服务 | 热点数据缓存、分布式锁 | Redis |
| 数据存储 | 持久化数据存储 | MySQL |
| 对象存储 | 图片文件存储 | MinIO/OSS |

---

## 3. 项目结构

### 3.1 后端项目结构

```
homework-server/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 应用入口
│   ├── config.py             # 配置（Pydantic Settings，从环境变量读取）
│   ├── database.py           # SQLAlchemy 引擎、Session
│   ├── redis_client.py       # Redis 连接
│   │
│   ├── models/               # SQLAlchemy 模型
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── homework.py
│   │   ├── record.py
│   │   ├── point_log.py
│   │   ├── reward.py
│   │   └── exchange.py
│   │
│   ├── schemas/              # Pydantic 请求/响应模型
│   │   ├── __init__.py
│   │   ├── common.py         # 通用响应、分页
│   │   ├── user.py
│   │   ├── homework.py
│   │   ├── points.py
│   │   ├── reward.py
│   │   └── exchange.py
│   │
│   ├── api/                  # 路由
│   │   ├── __init__.py
│   │   ├── deps.py           # 依赖注入（get_db, get_current_user, require_admin）
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── homework.py
│   │   ├── points.py
│   │   ├── reward.py
│   │   ├── exchange.py
│   │   └── admin.py
│   │
│   ├── services/             # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── user_service.py
│   │   ├── homework_service.py
│   │   ├── points_service.py
│   │   ├── reward_service.py
│   │   └── task_service.py   # 定时任务
│   │
│   ├── middleware/
│   │   ├── __init__.py
│   │   └── rate_limit.py     # Redis 限流中间件
│   │
│   └── utils/
│       ├── __init__.py
│       ├── response.py       # 统一响应封装
│       ├── wechat.py         # 微信 jscode2session
│       └── security.py       # JWT 生成/验证
│
├── alembic/                  # 数据库迁移
│   ├── env.py
│   └── versions/
├── alembic.ini
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── scripts/
│   └── init_db.py            # 初始化脚本（建表 + 种子数据）
└── README.md
```

### 3.2 小程序项目结构

```
homework-mini/
├── pages/
│   ├── index/               # 首页（作业列表）
│   ├── points/              # 积分页
│   ├── exchange/            # 兑换页
│   └── mine/                # 我的页
│
├── components/              # 公共组件
│   ├── homework-card/
│   ├── points-card/
│   └── reward-card/
│
├── utils/
│   ├── request.js           # 请求封装
│   ├── auth.js              # 登录相关
│   └── util.js              # 工具函数
│
├── config/
│   └── index.js             # 配置（API地址等）
│
├── app.js
├── app.json
└── app.wxss
```

---

## 4. 数据库设计

### 4.1 ER 图

```
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│   users     │       │  homeworks  │       │   records   │
│─────────────│       │─────────────│       │─────────────│
│ id          │───┐   │ id          │   ┌───│ id          │
│ openid      │   │   │ user_id     │◄──┘   │ user_id     │
│ nick_name   │   │   │ name        │       │ homework_id │
│ avatar_url  │   │   │ description │       │ points      │
│ role        │   │   │ type        │       │ complete_date│
│ total_points│   │   │ config      │       │ created_at  │
│ created_at  │   │   │ points      │       └─────────────┘
│ updated_at  │   │   │ penalty     │           │
└─────────────┘   │   │ expire_days │           │
      │           │   │ status      │           │
      │           │   │ created_at  │           │
      │           │   └─────────────┘           │
      │           │                             │
      │           └─────────────────────────────┘
      │
      │       ┌─────────────┐       ┌─────────────┐
      │       │   rewards   │       │  exchanges  │
      │       │─────────────│       │─────────────│
      │       │ id          │       │ id          │
      └──────►│ name        │       │ user_id     │
              │ description │       │ reward_id   │
              │ image_url   │       │ reward_name │
              │ points      │──────►│ points      │
              │ stock       │       │ status      │
              │ status      │       │ created_at  │
              │ created_at  │       └─────────────┘
              └─────────────┘
                    │
                    ▼
              ┌─────────────┐
              │ point_logs  │
              │─────────────│
              │ id          │
              │ user_id     │
              │ type        │
              │ amount      │
              │ balance     │
              │ source      │
              │ source_id   │
              │ expire_at   │
              │ created_at  │
              └─────────────┘
```

### 4.2 表结构设计

#### 4.2.1 用户表 (users)

```sql
CREATE TABLE `users` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键',
  `openid` varchar(64) NOT NULL COMMENT '微信openid',
  `unionid` varchar(64) DEFAULT NULL COMMENT '微信unionid',
  `nick_name` varchar(50) DEFAULT '用户' COMMENT '昵称',
  `avatar_url` varchar(500) DEFAULT NULL COMMENT '头像URL',
  `role` varchar(20) NOT NULL DEFAULT 'user' COMMENT '角色：user/admin',
  `total_points` int NOT NULL DEFAULT 0 COMMENT '当前总积分',
  `total_earned` int NOT NULL DEFAULT 0 COMMENT '累计获得积分',
  `total_spent` int NOT NULL DEFAULT 0 COMMENT '累计消耗积分',
  `status` varchar(20) NOT NULL DEFAULT 'active' COMMENT '状态：active/banned',
  `last_login_at` datetime DEFAULT NULL COMMENT '最后登录时间',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_openid` (`openid`),
  KEY `idx_role` (`role`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';
```

---

#### 4.2.2 作业表 (homeworks)

```sql
CREATE TABLE `homeworks` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键',
  `user_id` bigint NOT NULL COMMENT '用户ID',
  `name` varchar(50) NOT NULL COMMENT '作业名称',
  `description` varchar(200) DEFAULT NULL COMMENT '作业描述',
  `type` varchar(20) NOT NULL COMMENT '类型：daily/weekly/monthly/custom',
  `config` json DEFAULT NULL COMMENT '类型配置JSON',
  `points` int NOT NULL COMMENT '完成获得积分',
  `penalty` int NOT NULL DEFAULT 0 COMMENT '未完成惩罚积分',
  `expire_days` int DEFAULT NULL COMMENT '积分过期天数，NULL不过期',
  `status` varchar(20) NOT NULL DEFAULT 'active' COMMENT '状态：active/archived',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_user_status` (`user_id`, `status`),
  KEY `idx_user_type` (`user_id`, `type`),
  KEY `idx_created_at` (`created_at`),
  CONSTRAINT `fk_homeworks_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='作业表';
```

**config 字段示例：**
```json
// daily 类型
{}

// weekly 类型
{
  "days": [1, 3, 5]
}

// monthly 类型
{
  "dates": [1, 15]
}

// custom 类型
{
  "start_date": "2026-03-01",
  "end_date": "2026-03-31"
}
```

---

#### 4.2.3 打卡记录表 (records)

```sql
CREATE TABLE `records` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键',
  `user_id` bigint NOT NULL COMMENT '用户ID',
  `homework_id` bigint NOT NULL COMMENT '作业ID',
  `homework_name` varchar(50) NOT NULL COMMENT '作业名称（冗余）',
  `points` int NOT NULL COMMENT '获得积分',
  `complete_date` date NOT NULL COMMENT '完成日期',
  `note` varchar(200) DEFAULT NULL COMMENT '备注',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_user_homework_date` (`user_id`, `homework_id`, `complete_date`),
  KEY `idx_user_date` (`user_id`, `complete_date`),
  KEY `idx_created_at` (`created_at`),
  CONSTRAINT `fk_records_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_records_homework` FOREIGN KEY (`homework_id`) REFERENCES `homeworks` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='打卡记录表';
```

---

#### 4.2.4 积分流水表 (point_logs)

```sql
CREATE TABLE `point_logs` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键',
  `user_id` bigint NOT NULL COMMENT '用户ID',
  `type` varchar(20) NOT NULL COMMENT '类型：earn/spend/expire/adjust',
  `amount` int NOT NULL COMMENT '金额（正数获得，负数消耗）',
  `balance` int NOT NULL COMMENT '操作后余额',
  `source` varchar(20) NOT NULL COMMENT '来源：homework/exchange/expire/adjust',
  `source_id` bigint DEFAULT NULL COMMENT '来源ID',
  `description` varchar(200) DEFAULT NULL COMMENT '描述',
  `expire_at` datetime DEFAULT NULL COMMENT '过期时间',
  `is_expired` tinyint(1) NOT NULL DEFAULT 0 COMMENT '是否已过期',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_user_created` (`user_id`, `created_at`),
  KEY `idx_user_type` (`user_id`, `type`),
  KEY `idx_expire_at` (`expire_at`, `is_expired`),
  CONSTRAINT `fk_point_logs_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='积分流水表';
```

---

#### 4.2.5 奖品表 (rewards)

```sql
CREATE TABLE `rewards` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键',
  `name` varchar(50) NOT NULL COMMENT '奖品名称',
  `description` varchar(200) DEFAULT NULL COMMENT '奖品描述',
  `image_url` varchar(500) DEFAULT NULL COMMENT '奖品图片',
  `points` int NOT NULL COMMENT '所需积分',
  `stock` int NOT NULL DEFAULT 0 COMMENT '库存数量',
  `status` varchar(20) NOT NULL DEFAULT 'active' COMMENT '状态：active/inactive',
  `created_by` bigint NOT NULL COMMENT '创建人ID',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_status_created` (`status`, `created_at`),
  CONSTRAINT `fk_rewards_creator` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='奖品表';
```

---

#### 4.2.6 兑换记录表 (exchanges)

```sql
CREATE TABLE `exchanges` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键',
  `user_id` bigint NOT NULL COMMENT '用户ID',
  `reward_id` bigint NOT NULL COMMENT '奖品ID',
  `reward_name` varchar(50) NOT NULL COMMENT '奖品名称（冗余）',
  `reward_image` varchar(500) DEFAULT NULL COMMENT '奖品图片（冗余）',
  `points` int NOT NULL COMMENT '消耗积分',
  `quantity` int NOT NULL DEFAULT 1 COMMENT '兑换数量',
  `status` varchar(20) NOT NULL DEFAULT 'completed' COMMENT '状态：completed/cancelled',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_user_created` (`user_id`, `created_at`),
  KEY `idx_reward_id` (`reward_id`),
  CONSTRAINT `fk_exchanges_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_exchanges_reward` FOREIGN KEY (`reward_id`) REFERENCES `rewards` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='兑换记录表';
```

---

## 5. 接口设计

### 5.1 接口规范

**基础路径：** `https://your-domain.com/api/v1`

**请求头：**
```
Content-Type: application/json
Authorization: Bearer <token>   // 需要登录的接口
```

**响应格式：**
```javascript
// 成功响应
{
  "code": 0,
  "message": "success",
  "data": { ... }
}

// 错误响应
{
  "code": 10001,
  "message": "错误描述",
  "data": null
}
```

**分页参数：**
```
?page=1&page_size=20
```

**分页响应：**
```javascript
{
  "code": 0,
  "data": {
    "list": [...],
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total": 100,
      "total_pages": 5
    }
  }
}
```

---

### 5.2 接口列表

| 模块 | 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|------|
| 用户 | 登录 | POST | /auth/login | 微信登录 |
| 用户 | 获取用户信息 | GET | /user/info | 当前用户信息 |
| 用户 | 更新用户信息 | PUT | /user/info | 更新昵称头像 |
| 作业 | 获取作业列表 | GET | /homeworks | 用户作业列表 |
| 作业 | 获取作业详情 | GET | /homeworks/:id | 单个作业详情 |
| 作业 | 创建作业 | POST | /homeworks | 创建新作业 |
| 作业 | 更新作业 | PUT | /homeworks/:id | 更新作业 |
| 作业 | 删除作业 | DELETE | /homeworks/:id | 删除作业 |
| 作业 | 完成打卡 | POST | /homeworks/:id/complete | 完成作业 |
| 作业 | 今日作业 | GET | /homeworks/today | 今日待完成 |
| 作业 | 日历视图 | GET | /homeworks/calendar | 月度日历 |
| 积分 | 积分统计 | GET | /points/stats | 积分概况 |
| 积分 | 积分流水 | GET | /points/logs | 积分明细 |
| 奖品 | 奖品列表 | GET | /rewards | 可兑换奖品 |
| 奖品 | 兑换奖品 | POST | /rewards/:id/exchange | 兑换 |
| 奖品 | 兑换记录 | GET | /exchanges | 兑换历史 |
| 管理 | 创建奖品 | POST | /admin/rewards | 管理员 |
| 管理 | 更新奖品 | PUT | /admin/rewards/:id | 管理员 |
| 管理 | 删除奖品 | DELETE | /admin/rewards/:id | 管理员 |
| 管理 | 调整积分 | POST | /admin/points/adjust | 管理员 |
| 管理 | 用户列表 | GET | /admin/users | 管理员 |
| 管理 | 统计数据 | GET | /admin/stats | 管理员 |

---

### 5.3 接口详细设计

#### 5.3.1 用户登录

**POST /api/v1/auth/login**

**请求参数：**
```javascript
{
  "code": "微信login code"  // 小程序 wx.login() 获取
}
```

**响应：**
```javascript
{
  "code": 0,
  "data": {
    "token": "jwt_token",
    "expires_in": 7200,
    "user": {
      "id": 1,
      "nick_name": "用户昵称",
      "avatar_url": "头像URL",
      "role": "user",
      "total_points": 100
    },
    "is_new": false
  }
}
```

---

#### 5.3.2 创建作业

**POST /api/v1/homeworks**

**请求参数：**
```javascript
{
  "name": "背单词",
  "description": "每天背50个",
  "type": "daily",
  "config": {},
  "points": 10,
  "penalty": 0,
  "expire_days": null
}
```

**响应：**
```javascript
{
  "code": 0,
  "data": {
    "id": 1,
    "name": "背单词",
    "type": "daily",
    "points": 10,
    "created_at": "2026-03-27T15:00:00.000Z"
  }
}
```

---

#### 5.3.3 完成打卡

**POST /api/v1/homeworks/:id/complete**

**请求参数：**
```javascript
{
  "date": "2026-03-27",  // 可选，默认今天
  "note": "备注"         // 可选
}
```

**响应：**
```javascript
{
  "code": 0,
  "data": {
    "record_id": 1,
    "points": 10,
    "total_points": 110,
    "complete_date": "2026-03-27"
  }
}
```

---

#### 5.3.4 获取今日作业

**GET /api/v1/homeworks/today**

**响应：**
```javascript
{
  "code": 0,
  "data": {
    "date": "2026-03-27",
    "weekday": 5,
    "list": [
      {
        "id": 1,
        "name": "背单词",
        "type": "daily",
        "points": 10,
        "penalty": 0,
        "completed": false,
        "completed_at": null
      },
      {
        "id": 2,
        "name": "健身",
        "type": "weekly",
        "config": { "days": [1, 3, 5] },
        "points": 20,
        "completed": true,
        "completed_at": "2026-03-27T08:30:00.000Z"
      }
    ],
    "stats": {
      "total": 5,
      "completed": 2,
      "pending": 3,
      "today_points": 30
    }
  }
}
```

---

#### 5.3.5 兑换奖品

**POST /api/v1/rewards/:id/exchange**

**请求参数：**
```javascript
{
  "quantity": 1  // 可选，默认1
}
```

**响应：**
```javascript
{
  "code": 0,
  "data": {
    "exchange_id": 1,
    "reward_name": "电影票",
    "points": 100,
    "remaining_points": 400,
    "created_at": "2026-03-27T15:00:00.000Z"
  }
}
```

---

## 6. 核心流程

### 6.1 用户登录流程

```python
# 1. 小程序端调用 wx.login() 获取 code，发送到后端 /api/v1/auth/login

# 2. 后端处理 (app/services/user_service.py)
async def login(code: str, db: Session) -> dict:
    # 调用微信接口获取 openid
    openid = await get_openid_by_code(code)  # httpx 调用 jscode2session

    # 查询或创建用户
    user = db.query(User).filter(User.openid == openid).first()
    is_new = False
    if not user:
        user = User(openid=openid)
        db.add(user)
        db.commit()
        db.refresh(user)
        is_new = True

    # 生成 JWT token
    token = create_access_token(user.id)  # PyJWT, 7天过期

    return {"token": token, "user": user, "is_new": is_new}
```

### 6.2 打卡流程

```python
def complete_homework(user_id: int, homework_id: int, date: date, db: Session) -> dict:
    # 1. 查询作业
    homework = db.query(Homework).filter(
        Homework.id == homework_id, Homework.user_id == user_id
    ).first()
    if not homework:
        raise AppException(code=20001, message="作业不存在")

    # 2. 检查是否已打卡
    existing = db.query(Record).filter(
        Record.user_id == user_id,
        Record.homework_id == homework_id,
        Record.complete_date == date,
    ).first()
    if existing:
        raise AppException(code=20002, message="今日已完成该作业，不可重复打卡")

    try:
        # 3. 创建打卡记录
        record = Record(
            user_id=user_id, homework_id=homework_id,
            homework_name=homework.name, points=homework.points,
            complete_date=date,
        )
        db.add(record)

        # 4. 更新用户积分
        user = db.query(User).filter(User.id == user_id).first()
        new_balance = user.total_points + homework.points
        user.total_points = new_balance
        user.total_earned += homework.points

        # 5. 创建积分流水
        expire_at = None
        if homework.expire_days:
            expire_at = datetime.now() + timedelta(days=homework.expire_days)
        point_log = PointLog(
            user_id=user_id, type="earn", amount=homework.points,
            balance=new_balance, source="homework", source_id=homework_id,
            description=f"完成作业: {homework.name}", expire_at=expire_at,
        )
        db.add(point_log)

        db.commit()
        return {"record_id": record.id, "points_earned": homework.points, "total_points": new_balance}
    except Exception:
        db.rollback()
        raise
```

### 6.3 兑换流程

```python
def exchange_reward(user_id: int, reward_id: int, quantity: int, db: Session) -> dict:
    # 1. 查询奖品
    reward = db.query(Reward).filter(
        Reward.id == reward_id, Reward.status == "active"
    ).first()
    if not reward:
        raise AppException(code=30001, message="奖品不存在或已下架")

    points_needed = reward.points * quantity

    # 2. 查询用户积分
    user = db.query(User).filter(User.id == user_id).first()
    if user.total_points < points_needed:
        raise AppException(code=30002, message=f"积分不足，还需 {points_needed - user.total_points} 积分")

    try:
        # 3. 扣减库存（乐观锁）
        updated = db.query(Reward).filter(
            Reward.id == reward_id, Reward.stock >= quantity
        ).update({"stock": Reward.stock - quantity})
        if not updated:
            raise AppException(code=30003, message="库存扣减失败，请重试")

        # 4. 创建兑换记录
        exchange = Exchange(
            user_id=user_id, reward_id=reward_id,
            reward_name=reward.name, reward_image=reward.image_url,
            points=points_needed, quantity=quantity,
        )
        db.add(exchange)

        # 5. 更新用户积分
        new_balance = user.total_points - points_needed
        user.total_points = new_balance
        user.total_spent += points_needed

        # 6. 创建积分流水
        point_log = PointLog(
            user_id=user_id, type="spend", amount=-points_needed,
            balance=new_balance, source="exchange", source_id=exchange.id,
        )
        db.add(point_log)

        db.commit()
        return {"exchange_id": exchange.id, "points_spent": points_needed, "total_points": new_balance}
    except Exception:
        db.rollback()
        raise
```

---

## 7. 定时任务

### 7.1 积分过期处理

**触发时间：** 每天 00:05

```python
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

# 积分过期处理 (app/services/task_service.py)
def expire_points():
    db = SessionLocal()
    try:
        expired_logs = db.query(PointLog).filter(
            PointLog.type == "earn",
            PointLog.expire_at <= datetime.now(),
            PointLog.is_expired == False,
        ).all()

        for log in expired_logs:
            user = db.query(User).filter(User.id == log.user_id).first()
            user.total_points -= log.amount

            db.add(PointLog(
                user_id=log.user_id, type="expire", amount=-log.amount,
                balance=user.total_points, source="expire",
                source_id=log.id, description="积分过期",
            ))
            log.is_expired = True

        db.commit()
        logger.info(f"积分过期处理完成，共处理 {len(expired_logs)} 条")
    except Exception as e:
        db.rollback()
        logger.error(f"积分过期处理失败: {e}")
    finally:
        db.close()

scheduler.add_job(expire_points, "cron", hour=0, minute=5, id="expire_points")
```

### 7.2 惩罚扣分

**触发时间：** 每天 23:55

```python
def penalize_incomplete():
    db = SessionLocal()
    today = date.today()
    try:
        users = db.query(User).filter(User.status == "active").all()
        for user in users:
            homeworks = db.query(Homework).filter(
                Homework.user_id == user.id,
                Homework.status == "active",
                Homework.penalty > 0,
            ).all()

            for hw in homeworks:
                if not should_execute_today(hw, today):
                    continue
                record = db.query(Record).filter(
                    Record.user_id == user.id,
                    Record.homework_id == hw.id,
                    Record.complete_date == today,
                ).first()
                if not record:
                    user.total_points -= hw.penalty
                    db.add(PointLog(
                        user_id=user.id, type="adjust", amount=-hw.penalty,
                        balance=user.total_points, source="penalty",
                        source_id=hw.id,
                        description=f"未完成作业惩罚: {hw.name}",
                    ))
        db.commit()
        logger.info("惩罚扣分处理完成")
    except Exception as e:
        db.rollback()
        logger.error(f"惩罚扣分处理失败: {e}")
    finally:
        db.close()

scheduler.add_job(penalize_incomplete, "cron", hour=23, minute=55, id="penalize_incomplete")
```

---

## 8. 部署方案

### 8.1 服务器要求

| 项目 | 最低配置 | 推荐配置 |
|------|----------|----------|
| CPU | 2核 | 4核 |
| 内存 | 4GB | 8GB |
| 硬盘 | 50GB SSD | 100GB SSD |
| 带宽 | 3Mbps | 5Mbps |

### 8.2 软件环境

| 软件 | 版本 |
|------|------|
| Ubuntu | 22.04 LTS |
| Python | 3.11+ |
| MySQL | 8.0 |
| Redis | 7.x |
| Nginx | 1.24 |
| Docker | 24.x (可选) |

### 8.3 Docker Compose 配置

```yaml
# docker-compose.yml
version: '3.8'

services:
  # FastAPI
  api:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - mysql
      - redis
    restart: always

  # Nginx
  nginx:
    image: nginx:1.24-alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - api
    restart: always

  # MySQL
  mysql:
    image: mysql:8.0
    environment:
      - MYSQL_ROOT_PASSWORD=your_password
      - MYSQL_DATABASE=homework
    volumes:
      - mysql_data:/var/lib/mysql
      # 初始化用 python -m scripts.init_db
    ports:
      - "3306:3306"
    restart: always

  # Redis
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    restart: always

volumes:
  mysql_data:
  redis_data:
```

### 8.4 Nginx 配置

```nginx
# nginx.conf
upstream api {
    server api:8000;
}

server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;

    # SSL 配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # API 代理
    location /api/ {
        proxy_pass http://api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # 限流
        limit_req zone=api_limit burst=20 nodelay;
    }

    # 健康检查
    location /health {
        proxy_pass http://api/health;
    }
}

# 限流配置
limit_req_zone $binary_remote_addr zone=api_limit=10m rate=10r/s;
```

---

## 9. 安全设计

### 9.1 认证授权

```python
# JWT 认证依赖注入 (app/api/deps.py)
from fastapi import Depends, Header
from app.utils.security import decode_access_token

async def get_current_user(
    authorization: str = Header(...),
    db: Session = Depends(get_db),
) -> User:
    token = authorization.replace("Bearer ", "")
    payload = decode_access_token(token)
    if not payload:
        raise AppException(code=10001, message="token无效或已过期", status_code=401)
    user = db.query(User).filter(User.id == payload["user_id"]).first()
    if not user:
        raise AppException(code=10001, message="用户不存在", status_code=401)
    return user


# 管理员权限依赖注入
async def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise AppException(code=10003, message="无权限", status_code=403)
    return user
```

### 9.2 数据安全

- 所有密码/敏感配置使用环境变量
- 数据库连接使用 SSL
- API 使用 HTTPS
- 用户数据隔离（只能操作自己的数据）

### 9.3 接口安全

- 请求频率限制（Redis 实现）
- 参数校验（Pydantic 自动校验）
- SQL 注入防护（SQLAlchemy 参数化查询）
- XSS 防护（输入过滤）

```python
# Redis 限流中间件 (app/middleware/rate_limit.py)
from starlette.middleware.base import BaseHTTPMiddleware
from app.redis_client import get_redis

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        client_ip = request.client.host
        key = f"rate_limit:{client_ip}"
        r = get_redis()
        count = r.incr(key)
        if count == 1:
            r.expire(key, 60)
        if count > settings.RATE_LIMIT_PER_MINUTE:  # 默认 100次/分钟
            return JSONResponse(
                status_code=429,
                content={"code": 429, "message": "请求过于频繁，请稍后再试", "data": None},
            )
        return await call_next(request)
```

---

## 10. 性能优化

### 10.1 Redis 缓存

```python
# 用户积分缓存 (app/services/points_service.py)
import json
from app.redis_client import get_redis

def get_user_points_cached(user_id: int, db: Session) -> dict:
    r = get_redis()
    cache_key = f"user:points:{user_id}"

    # 先查缓存
    cached = r.get(cache_key)
    if cached:
        return json.loads(cached)

    # 查数据库
    user = db.query(User).filter(User.id == user_id).first()
    data = {
        "total_points": user.total_points,
        "total_earned": user.total_earned,
        "total_spent": user.total_spent,
    }

    # 写入缓存，过期 10 分钟
    r.setex(cache_key, 600, json.dumps(data))
    return data


def invalidate_points_cache(user_id: int):
    get_redis().delete(f"user:points:{user_id}")
```

### 10.2 数据库优化

- 合理使用索引
- 避免 N+1 查询
- 大表分页优化
- 读写分离（后期）

---

## 11. 监控与日志

### 11.1 日志配置

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("error.log", level=logging.ERROR),
        logging.FileHandler("combined.log"),
        logging.StreamHandler(),  # 控制台输出
    ],
)
logger = logging.getLogger(__name__)
```

### 11.2 健康检查

```python
@app.get("/health")
def health():
    from sqlalchemy import text
    db_ok = redis_ok = False
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        pass
    try:
        get_redis().ping()
        redis_ok = True
    except Exception:
        pass
    status = "healthy" if (db_ok and redis_ok) else "unhealthy"
    return {"status": status, "database": "ok" if db_ok else "error", "redis": "ok" if redis_ok else "error"}
```

---

## 12. 扩展性设计

### 12.1 预留扩展点

- 多端支持：接口设计兼容 Web/H5
- 社交功能：数据表预留分享字段
- 统计报表：积分流水支持多维度查询

### 12.2 后期规划

| 功能 | 说明 |
|------|------|
| 作业模板 | 预设作业模板，快速创建 |
| 作业分类 | 支持作业分类管理 |
| 团队/家庭 | 支持多人协作打卡 |
| 数据导出 | 导出打卡记录和统计数据 |
| 消息通知 | 打卡提醒、积分变动通知 |

---

## 13. 风险评估

### 13.1 技术风险

| 风险 | 可能性 | 影响 | 应对措施 |
|------|--------|------|----------|
| 服务器故障 | 低 | 高 | 多实例部署、自动重启 |
| 数据库性能 | 中 | 中 | 索引优化、读写分离 |
| 积分并发冲突 | 中 | 中 | 数据库事务 + 乐观锁 |
| SSL 证书过期 | 低 | 高 | 自动续期监控 |

### 13.2 技术债务

| 债务项 | 原因 | 计划归还时间 |
|--------|------|--------------|
| 无单元测试 | 一期时间紧 | 二期补充 |
| 无监控告警 | 一期未接入 | 二期接入 |
| 无 CI/CD | 手动部署 | 二期配置 |

---

## 附录

### 参考资料
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [SQLAlchemy ORM 文档](https://docs.sqlalchemy.org/)
- [微信小程序登录流程](https://developers.weixin.qq.com/miniprogram/dev/framework/open-ability/login.html)

---

## 版本历史

| 版本 | 日期 | 修改人 | 修改内容 |
|------|------|--------|----------|
| v1.0 | 2026-03-27 | architect-agent | 初始版本（云开发） |
| v1.1 | 2026-03-27 | architect-agent | 改为自建服务器方案 |
| v1.2 | 2026-04-06 | 大龙虾主管 | 技术栈从 Node.js 改为 Python + FastAPI，同步更新代码示例、项目结构、部署配置 |