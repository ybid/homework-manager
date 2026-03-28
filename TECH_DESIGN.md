# 作业管理系统技术方案

## 文档信息

| 字段 | 内容 |
|------|------|
| 项目名称 | 作业管理系统（小程序） |
| 版本号 | v2.0 |
| 更新日期 | 2026-03-28 |
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
| 后端 | Python + FastAPI | 开发快、自动文档、异步支持、生态丰富 |
| ORM | SQLAlchemy 2.0 | Python 最流行的 ORM，成熟稳定 |
| 数据库 | MySQL 8.0 | 稳定可靠、事务支持好、运维成熟 |
| 缓存 | Redis 7.x | 高性能缓存、支持分布式锁 |
| 定时任务 | APScheduler | Python 原生定时任务库 |
| 部署 | Docker + Gunicorn + Uvicorn | 容器化部署、便于扩展 |

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
│                   │  Uvicorn  │                                      │
│                   │  :3000    │                                      │
│                   └─────┬─────┘                                      │
│                         │                                            │
│    ┌────────────────────┼────────────────────┐                      │
│    │                    │                    │                      │
│ ┌──▼────┐          ┌────▼────┐         ┌────▼────┐                │
│ │用户   │          │  业务   │         │ 定时    │                │
│ │服务   │          │  服务   │         │ 任务    │                │
│ └──┬────┘          └────┬────┘         │APScheduler│                │
│    │                    │              └────┬────┘                │
│    └────────────────────┼────────────────────┘                      │
│                         │                                            │
│    ┌────────────────────┼────────────────────┐                      │
│    │                    │                    │                      │
│ ┌──▼────┐          ┌────▼────┐         ┌────▼────┐                │
│ │ MySQL │          │  Redis  │         │ 对象存储│                │
│ │ :3306 │          │  :6379  │         │ MinIO   │                │
│ └───────┘          └─────────┘         └─────────┘                │
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

---

## 3. 项目结构

### 3.1 后端项目结构

```
backend/
├── app/
│   ├── api/               # API 路由
│   │   ├── auth.py        # 登录认证
│   │   ├── user.py        # 用户接口
│   │   ├── homework.py    # 作业接口
│   │   ├── points.py      # 积分接口
│   │   └── reward.py      # 奖品接口
│   │
│   ├── core/              # 核心配置
│   │   ├── config.py      # 配置管理
│   │   ├── database.py    # 数据库连接
│   │   └── security.py    # JWT 认证
│   │
│   ├── models/            # 数据模型
│   │   ├── user.py        # 用户模型
│   │   ├── homework.py    # 作业模型
│   │   └── reward.py      # 奖品模型
│   │
│   ├── schemas/           # Pydantic 模型
│   │   ├── user.py        # 用户 Schema
│   │   ├── homework.py    # 作业 Schema
│   │   ├── reward.py      # 奖品 Schema
│   │   └── common.py      # 通用响应
│   │
│   ├── services/          # 业务逻辑
│   │   ├── user_service.py
│   │   ├── homework_service.py
│   │   ├── points_service.py
│   │   └── reward_service.py
│   │
│   └── main.py            # 应用入口
│
├── scripts/               # 脚本
│   └── init-db.sql        # 数据库初始化
│
├── docker/                # Docker 配置
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── requirements.txt       # Python 依赖
├── .env.example           # 环境变量示例
└── .env                   # 环境变量（不提交）
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
├── utils/
│   ├── request.js           # 请求封装
│   └── auth.js              # 登录相关
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
  CONSTRAINT `fk_homeworks_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='作业表';
```

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
  CONSTRAINT `fk_records_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_records_homework` FOREIGN KEY (`homework_id`) REFERENCES `homeworks` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='打卡记录表';
```

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
  KEY `idx_expire_at` (`expire_at`, `is_expired`),
  CONSTRAINT `fk_point_logs_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='积分流水表';
```

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
  KEY `idx_status` (`status`),
  CONSTRAINT `fk_rewards_creator` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='奖品表';
```

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
```json
// 成功响应
{
  "code": 0,
  "message": "success",
  "data": { ... }
}

// 错误响应
{
  "code": 400,
  "message": "错误描述",
  "data": null
}
```

### 5.2 接口列表

| 模块 | 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|------|
| 用户 | 登录 | POST | /api/v1/auth/login | 微信登录 |
| 用户 | 获取用户信息 | GET | /api/v1/user/info | 当前用户信息 |
| 用户 | 更新用户信息 | PUT | /api/v1/user/info | 更新昵称头像 |
| 作业 | 获取作业列表 | GET | /api/v1/homeworks | 用户作业列表 |
| 作业 | 获取作业详情 | GET | /api/v1/homeworks/:id | 单个作业详情 |
| 作业 | 创建作业 | POST | /api/v1/homeworks | 创建新作业 |
| 作业 | 更新作业 | PUT | /api/v1/homeworks/:id | 更新作业 |
| 作业 | 删除作业 | DELETE | /api/v1/homeworks/:id | 删除作业 |
| 作业 | 完成打卡 | POST | /api/v1/points/complete/:id | 完成作业 |
| 作业 | 今日作业 | GET | /api/v1/homeworks/today | 今日待完成 |
| 作业 | 日历视图 | GET | /api/v1/homeworks/calendar | 月度日历 |
| 积分 | 积分统计 | GET | /api/v1/points/stats | 积分概况 |
| 积分 | 积分流水 | GET | /api/v1/points/logs | 积分明细 |
| 奖品 | 奖品列表 | GET | /api/v1/rewards | 可兑换奖品 |
| 奖品 | 兑换奖品 | POST | /api/v1/rewards/:id/exchange | 兑换 |
| 奖品 | 兑换记录 | GET | /api/v1/rewards/exchanges | 兑换历史 |
| 管理 | 创建奖品 | POST | /api/v1/admin/rewards | 管理员 |
| 管理 | 更新奖品 | PUT | /api/v1/admin/rewards/:id | 管理员 |
| 管理 | 删除奖品 | DELETE | /api/v1/admin/rewards/:id | 管理员 |

### 5.3 API 文档

启动服务后自动访问 Swagger 文档：
- Swagger UI: http://localhost:3000/docs
- ReDoc: http://localhost:3000/redoc

---

## 6. 核心流程

### 6.1 用户登录流程

```python
# 小程序端
wx.login({
  success: (res) => {
    // 发送 code 到后端
    request.post('/auth/login', { code: res.code })
  }
})

# 后端处理
async def login(code: str, db: Session):
    # 调用微信接口获取 openid
    wx_data = await get_wechat_openid(code)
    openid = wx_data["openid"]
    
    # 查询或创建用户
    user = db.query(User).filter(User.openid == openid).first()
    if not user:
        user = User(openid=openid, ...)
        db.add(user)
        db.commit()
    
    # 生成 JWT token
    token = create_access_token({"user_id": user.id})
    
    return {"token": token, "user": {...}}
```

### 6.2 打卡流程

```python
def complete_homework(user_id: int, homework_id: int, date: date, db: Session):
    # 1. 查询作业
    homework = db.query(Homework).filter(Homework.id == homework_id).first()
    
    # 2. 检查是否已打卡
    existing = db.query(Record).filter(
        Record.user_id == user_id,
        Record.homework_id == homework_id,
        Record.complete_date == date
    ).first()
    if existing:
        raise ValueError("今日已完成打卡")
    
    # 3. 创建打卡记录
    record = Record(user_id=user_id, homework_id=homework_id, ...)
    db.add(record)
    
    # 4. 更新用户积分
    user = db.query(User).filter(User.id == user_id).first()
    user.total_points += homework.points
    user.total_earned += homework.points
    
    # 5. 创建积分流水
    log = PointLog(user_id=user_id, type="earn", amount=homework.points, ...)
    db.add(log)
    
    db.commit()
    return {"record_id": record.id, "points": homework.points}
```

### 6.3 兑换流程

```python
def exchange_reward(user_id: int, reward_id: int, quantity: int, db: Session):
    # 1. 查询奖品
    reward = db.query(Reward).filter(Reward.id == reward_id, Reward.status == "active").first()
    
    # 2. 检查库存和积分
    if reward.stock < quantity:
        raise ValueError("库存不足")
    
    user = db.query(User).filter(User.id == user_id).first()
    points_needed = reward.points * quantity
    
    if user.total_points < points_needed:
        raise ValueError(f"积分不足，还需 {points_needed - user.total_points} 积分")
    
    # 3. 扣减库存和积分
    reward.stock -= quantity
    user.total_points -= points_needed
    user.total_spent += points_needed
    
    # 4. 创建兑换记录
    exchange = Exchange(user_id=user_id, reward_id=reward_id, ...)
    db.add(exchange)
    
    # 5. 创建积分流水
    log = PointLog(user_id=user_id, type="spend", amount=-points_needed, ...)
    db.add(log)
    
    db.commit()
    return {"exchange_id": exchange.id, "remaining_points": user.total_points}
```

---

## 7. 定时任务

### 7.1 积分过期处理

**触发时间：** 每天 00:05

```python
from apscheduler.schedulers.background import BackgroundScheduler

def expire_points():
    """处理过期积分"""
    expired_logs = db.query(PointLog).filter(
        PointLog.type == "earn",
        PointLog.expire_at <= datetime.now(),
        PointLog.is_expired == False
    ).all()
    
    for log in expired_logs:
        user = db.query(User).filter(User.id == log.user_id).first()
        user.total_points -= log.amount
        
        expire_log = PointLog(
            user_id=log.user_id,
            type="expire",
            amount=-log.amount,
            balance=user.total_points,
            source="expire",
            source_id=log.id,
            description="积分过期"
        )
        db.add(expire_log)
        log.is_expired = True
    
    db.commit()
```

### 7.2 惩罚扣分

**触发时间：** 每天 23:55

```python
def apply_penalty():
    """未完成惩罚扣分"""
    today = date.today()
    
    for user in db.query(User).all():
        homeworks = db.query(Homework).filter(
            Homework.user_id == user.id,
            Homework.status == "active",
            Homework.penalty > 0
        ).all()
        
        for hw in homeworks:
            if not should_execute_today(hw, today):
                continue
            
            record = db.query(Record).filter(
                Record.user_id == user.id,
                Record.homework_id == hw.id,
                Record.complete_date == today
            ).first()
            
            if not record:
                user.total_points -= hw.penalty
                log = PointLog(user_id=user.id, type="spend", amount=-hw.penalty, ...)
                db.add(log)
    
    db.commit()
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
| Python | 3.10+ |
| MySQL | 8.0 |
| Redis | 7.x |
| Nginx | 1.24 |
| Docker | 24.x (可选) |

### 8.3 Docker 部署

```yaml
# docker-compose.yml
version: '3.8'

services:
  # FastAPI API
  api:
    build: .
    ports:
      - "3000:3000"
    environment:
      - DB_HOST=mysql
      - REDIS_HOST=redis
      - JWT_SECRET=${JWT_SECRET}
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
    depends_on:
      - api
    restart: always

  # MySQL
  mysql:
    image: mysql:8.0
    environment:
      - MYSQL_ROOT_PASSWORD=${DB_PASSWORD}
      - MYSQL_DATABASE=homework
    volumes:
      - mysql_data:/var/lib/mysql
    restart: always

  # Redis
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: always

volumes:
  mysql_data:
  redis_data:
```

### 8.4 Nginx 配置

```nginx
upstream api {
    server api:3000;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;

    location /api/ {
        proxy_pass http://api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /docs {
        proxy_pass http://api;
    }
}
```

---

## 9. 安全设计

### 9.1 认证授权

```python
from jose import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

def verify_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="token无效")

async def get_current_user(credentials = Depends(security), db = Depends(get_db)):
    payload = verify_token(credentials.credentials)
    user = db.query(User).filter(User.id == payload["user_id"]).first()
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
    return user
```

### 9.2 数据安全

- 所有密码/敏感配置使用环境变量
- 数据库连接使用 SSL
- API 使用 HTTPS
- 用户数据隔离（只能操作自己的数据）

### 9.3 接口安全

- 请求频率限制（Redis 实现）
- 参数校验（Pydantic）
- SQL 注入防护（SQLAlchemy ORM）
- XSS 防护（输入过滤）

---

## 10. 监控与日志

### 10.1 日志配置

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

### 10.2 健康检查

```python
@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "version": settings.APP_VERSION,
    }
```

---

## 11. 扩展性设计

### 11.1 预留扩展点

- 多端支持：接口设计兼容 Web/H5
- 社交功能：数据表预留分享字段
- 统计报表：积分流水支持多维度查询

### 11.2 后期规划

| 功能 | 说明 |
|------|------|
| 作业模板 | 预设作业模板，快速创建 |
| 作业分类 | 支持作业分类管理 |
| 团队/家庭 | 支持多人协作打卡 |
| 数据导出 | 导出打卡记录和统计数据 |
| 消息通知 | 打卡提醒、积分变动通知 |

---

## 附录

### 参考资料
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [SQLAlchemy 文档](https://docs.sqlalchemy.org/)
- [微信小程序登录流程](https://developers.weixin.qq.com/miniprogram/dev/framework/open-ability/login.html)

---

## 版本历史

| 版本 | 日期 | 修改内容 |
|------|------|----------|
| v1.0 | 2026-03-27 | 初始版本（云开发） |
| v1.1 | 2026-03-27 | 改为自建服务器方案 |
| v2.0 | 2026-03-28 | 重写为 Python + FastAPI |
