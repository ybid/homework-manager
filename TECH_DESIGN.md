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
| 后端 | Node.js + Express/Koa | 生态丰富、开发效率高、与前端语言统一 |
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
│                   │  Node.js  │                                      │
│                   │  API服务  │                                      │
│                   │  :3000    │                                      │
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
| 用户服务 | 用户注册、登录、权限 | Node.js |
| 作业服务 | 作业 CRUD、打卡 | Node.js |
| 积分服务 | 积分获取、消耗、统计 | Node.js |
| 奖品服务 | 奖品管理、兑换 | Node.js |
| 定时任务 | 积分过期、惩罚扣分 | Node-cron |
| 缓存服务 | 热点数据缓存、分布式锁 | Redis |
| 数据存储 | 持久化数据存储 | MySQL |
| 对象存储 | 图片文件存储 | MinIO/OSS |

---

## 3. 项目结构

### 3.1 后端项目结构

```
homework-server/
├── src/
│   ├── config/              # 配置文件
│   │   ├── index.js         # 主配置
│   │   ├── database.js      # 数据库配置
│   │   └── redis.js         # Redis配置
│   │
│   ├── controllers/         # 控制器
│   │   ├── user.controller.js
│   │   ├── homework.controller.js
│   │   ├── points.controller.js
│   │   ├── reward.controller.js
│   │   └── admin.controller.js
│   │
│   ├── services/            # 业务逻辑
│   │   ├── user.service.js
│   │   ├── homework.service.js
│   │   ├── points.service.js
│   │   ├── reward.service.js
│   │   └── task.service.js
│   │
│   ├── models/              # 数据模型
│   │   ├── user.model.js
│   │   ├── homework.model.js
│   │   ├── record.model.js
│   │   ├── point_log.model.js
│   │   ├── reward.model.js
│   │   └── exchange.model.js
│   │
│   ├── middlewares/         # 中间件
│   │   ├── auth.js          # 认证中间件
│   │   ├── admin.js         # 管理员权限
│   │   ├── validator.js     # 参数校验
│   │   └── errorHandler.js  # 错误处理
│   │
│   ├── routes/              # 路由
│   │   ├── index.js
│   │   ├── user.routes.js
│   │   ├── homework.routes.js
│   │   ├── points.routes.js
│   │   ├── reward.routes.js
│   │   └── admin.routes.js
│   │
│   ├── utils/               # 工具函数
│   │   ├── logger.js
│   │   ├── response.js
│   │   ├── wechat.js        # 微信接口
│   │   └── cron.js          # 定时任务
│   │
│   └── app.js               # 应用入口
│
├── tests/                   # 测试
│   ├── unit/
│   └── integration/
│
├── docker/                  # Docker配置
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── scripts/                 # 脚本
│   └── init-db.sql          # 数据库初始化
│
├── package.json
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

```javascript
// 1. 小程序调用 wx.login() 获取 code
wx.login({
  success: (res) => {
    const code = res.code
    // 2. 发送 code 到后端
    request.post('/auth/login', { code })
  }
})

// 3. 后端处理
async function login(code) {
  // 调用微信接口获取 openid
  const wxRes = await axios.get('https://api.weixin.qq.com/sns/jscode2session', {
    params: {
      appid: APP_ID,
      secret: APP_SECRET,
      js_code: code,
      grant_type: 'authorization_code'
    }
  })
  
  const { openid, session_key } = wxRes.data
  
  // 查询或创建用户
  let user = await User.findOne({ where: { openid } })
  if (!user) {
    user = await User.create({ openid })
  }
  
  // 生成 JWT token
  const token = jwt.sign({ userId: user.id }, JWT_SECRET, { expiresIn: '7d' })
  
  return { token, user }
}
```

### 6.2 打卡流程

```javascript
async function completeHomework(userId, homeworkId, date) {
  // 开启事务
  const transaction = await sequelize.transaction()
  
  try {
    // 1. 查询作业
    const homework = await Homework.findOne({
      where: { id: homeworkId, user_id: userId },
      transaction
    })
    
    if (!homework) throw new Error('作业不存在')
    
    // 2. 检查是否已打卡
    const existing = await Record.findOne({
      where: { user_id: userId, homework_id: homeworkId, complete_date: date },
      transaction
    })
    
    if (existing) throw new Error('今日已完成打卡')
    
    // 3. 创建打卡记录
    const record = await Record.create({
      user_id: userId,
      homework_id: homeworkId,
      homework_name: homework.name,
      points: homework.points,
      complete_date: date
    }, { transaction })
    
    // 4. 创建积分流水
    const user = await User.findByPk(userId, { transaction })
    const newBalance = user.total_points + homework.points
    
    await PointLog.create({
      user_id: userId,
      type: 'earn',
      amount: homework.points,
      balance: newBalance,
      source: 'homework',
      source_id: homeworkId,
      expire_at: homework.expire_days ? dayjs().add(homework.expire_days, 'day').toDate() : null
    }, { transaction })
    
    // 5. 更新用户积分
    await user.update({
      total_points: newBalance,
      total_earned: user.total_earned + homework.points
    }, { transaction })
    
    // 提交事务
    await transaction.commit()
    
    return { record, newBalance }
    
  } catch (error) {
    await transaction.rollback()
    throw error
  }
}
```

### 6.3 兑换流程

```javascript
async function exchangeReward(userId, rewardId, quantity = 1) {
  const transaction = await sequelize.transaction()
  
  try {
    // 1. 查询奖品
    const reward = await Reward.findOne({
      where: { id: rewardId, status: 'active' },
      transaction
    })
    
    if (!reward) throw new Error('奖品不存在或已下架')
    if (reward.stock < quantity) throw new Error('库存不足')
    
    // 2. 查询用户积分
    const user = await User.findByPk(userId, { transaction, lock: true })
    const pointsNeeded = reward.points * quantity
    
    if (user.total_points < pointsNeeded) {
      throw new Error(`积分不足，还需 ${pointsNeeded - user.total_points} 积分`)
    }
    
    // 3. 扣减库存（乐观锁）
    const [updated] = await Reward.update(
      { stock: sequelize.literal('stock - ' + quantity) },
      { where: { id: rewardId, stock: { [Op.gte]: quantity } }, transaction }
    )
    
    if (!updated) throw new Error('库存扣减失败，请重试')
    
    // 4. 创建兑换记录
    const exchange = await Exchange.create({
      user_id: userId,
      reward_id: rewardId,
      reward_name: reward.name,
      reward_image: reward.image_url,
      points: pointsNeeded,
      quantity
    }, { transaction })
    
    // 5. 创建积分流水
    const newBalance = user.total_points - pointsNeeded
    await PointLog.create({
      user_id: userId,
      type: 'spend',
      amount: -pointsNeeded,
      balance: newBalance,
      source: 'exchange',
      source_id: exchange.id
    }, { transaction })
    
    // 6. 更新用户积分
    await user.update({
      total_points: newBalance,
      total_spent: user.total_spent + pointsNeeded
    }, { transaction })
    
    await transaction.commit()
    
    return { exchange, remainingPoints: newBalance }
    
  } catch (error) {
    await transaction.rollback()
    throw error
  }
}
```

---

## 7. 定时任务

### 7.1 积分过期处理

**触发时间：** 每天 00:05

```javascript
const cron = require('node-cron')

// 积分过期处理
cron.schedule('5 0 * * *', async () => {
  const transaction = await sequelize.transaction()
  
  try {
    // 查询过期的积分流水
    const expiredLogs = await PointLog.findAll({
      where: {
        type: 'earn',
        expire_at: { [Op.lte]: new Date() },
        is_expired: false
      },
      transaction
    })
    
    for (const log of expiredLogs) {
      // 创建过期流水
      await PointLog.create({
        user_id: log.user_id,
        type: 'expire',
        amount: -log.amount,
        balance: 0, // 稍后计算
        source: 'expire',
        source_id: log.id,
        description: '积分过期'
      }, { transaction })
      
      // 更新用户积分
      await User.decrement('total_points', {
        by: log.amount,
        where: { id: log.user_id },
        transaction
      })
      
      // 标记原流水为已过期
      await log.update({ is_expired: true }, { transaction })
    }
    
    await transaction.commit()
    logger.info(`积分过期处理完成，共处理 ${expiredLogs.length} 条`)
    
  } catch (error) {
    await transaction.rollback()
    logger.error('积分过期处理失败:', error)
  }
})
```

### 7.2 惩罚扣分

**触发时间：** 每天 23:55

```javascript
// 未完成惩罚
cron.schedule('55 23 * * *', async () => {
  const today = dayjs().format('YYYY-MM-DD')
  
  try {
    // 查询今日未完成的作业（有惩罚设置）
    const users = await User.findAll()
    
    for (const user of users) {
      const homeworks = await Homework.findAll({
        where: { user_id: user.id, status: 'active', penalty: { [Op.gt]: 0 } }
      })
      
      for (const homework of homeworks) {
        // 检查今天是否需要执行
        if (!shouldExecuteToday(homework, today)) continue
        
        // 检查是否已打卡
        const record = await Record.findOne({
          where: { user_id: user.id, homework_id: homework.id, complete_date: today }
        })
        
        if (!record) {
          // 执行惩罚
          await applyPenalty(user, homework, today)
        }
      }
    }
    
    logger.info('惩罚扣分处理完成')
    
  } catch (error) {
    logger.error('惩罚扣分处理失败:', error)
  }
})
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
| Node.js | 18.x LTS |
| MySQL | 8.0 |
| Redis | 7.x |
| Nginx | 1.24 |
| Docker | 24.x (可选) |

### 8.3 Docker Compose 配置

```yaml
# docker-compose.yml
version: '3.8'

services:
  # Node.js API
  api:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - DB_HOST=mysql
      - REDIS_HOST=redis
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
      - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/init.sql
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
    server api:3000;
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

```javascript
// JWT 认证中间件
function authMiddleware(req, res, next) {
  const token = req.headers.authorization?.replace('Bearer ', '')
  
  if (!token) {
    return res.status(401).json({ code: 401, message: '未登录' })
  }
  
  try {
    const decoded = jwt.verify(token, JWT_SECRET)
    req.userId = decoded.userId
    next()
  } catch (error) {
    return res.status(401).json({ code: 401, message: 'token无效或已过期' })
  }
}

// 管理员权限中间件
function adminMiddleware(req, res, next) {
  const user = await User.findByPk(req.userId)
  
  if (user.role !== 'admin') {
    return res.status(403).json({ code: 403, message: '无权限' })
  }
  
  next()
}
```

### 9.2 数据安全

- 所有密码/敏感配置使用环境变量
- 数据库连接使用 SSL
- API 使用 HTTPS
- 用户数据隔离（只能操作自己的数据）

### 9.3 接口安全

- 请求频率限制（Redis 实现）
- 参数校验（Joi/express-validator）
- SQL 注入防护（ORM 参数化查询）
- XSS 防护（输入过滤）

```javascript
// 限流中间件
const rateLimit = require('express-rate-limit')
const RedisStore = require('rate-limit-redis')

const limiter = rateLimit({
  store: new RedisStore({
    client: redisClient
  }),
  windowMs: 60 * 1000, // 1分钟
  max: 100, // 最多100次请求
  message: { code: 429, message: '请求过于频繁，请稍后再试' }
})

app.use('/api/', limiter)
```

---

## 10. 性能优化

### 10.1 Redis 缓存

```javascript
// 用户积分缓存
async function getUserPoints(userId) {
  const cacheKey = `user:points:${userId}`
  
  // 先查缓存
  const cached = await redis.get(cacheKey)
  if (cached) return JSON.parse(cached)
  
  // 查数据库
  const user = await User.findByPk(userId)
  
  // 写入缓存，过期10分钟
  await redis.setex(cacheKey, 600, JSON.stringify({
    total_points: user.total_points,
    total_earned: user.total_earned,
    total_spent: user.total_spent
  }))
  
  return user
}

// 积分变动后清除缓存
async function invalidatePointsCache(userId) {
  await redis.del(`user:points:${userId}`)
}
```

### 10.2 数据库优化

- 合理使用索引
- 避免 N+1 查询
- 大表分页优化
- 读写分离（后期）

---

## 11. 监控与日志

### 11.1 日志配置

```javascript
const winston = require('winston')

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  transports: [
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' })
  ]
})

// 开发环境输出到控制台
if (process.env.NODE_ENV !== 'production') {
  logger.add(new winston.transports.Console())
}
```

### 11.2 健康检查

```javascript
// /health 接口
app.get('/health', async (req, res) => {
  try {
    // 检查数据库
    await sequelize.query('SELECT 1')
    
    // 检查 Redis
    await redis.ping()
    
    res.json({
      status: 'ok',
      timestamp: new Date(),
      uptime: process.uptime()
    })
  } catch (error) {
    res.status(503).json({
      status: 'error',
      message: error.message
    })
  }
})
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
- [Express.js 文档](https://expressjs.com/)
- [Sequelize ORM 文档](https://sequelize.org/)
- [微信小程序登录流程](https://developers.weixin.qq.com/miniprogram/dev/framework/open-ability/login.html)

---

## 版本历史

| 版本 | 日期 | 修改人 | 修改内容 |
|------|------|--------|----------|
| v1.0 | 2026-03-27 | architect-agent | 初始版本（云开发） |
| v1.1 | 2026-03-27 | architect-agent | 改为自建服务器方案 |