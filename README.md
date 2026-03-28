# 作业管理系统

微信小程序 + FastAPI 后端的作业管理应用，支持作业管理、积分打卡、奖品兑换功能。

## 项目组成

```
homework-manager/
├── backend/            # 后端服务 (Python + FastAPI + MySQL)
├── homework-mini/      # 微信小程序前端
├── PRD.md              # 产品需求文档
└── TECH_DESIGN.md      # 技术设计文档
```

## 功能特性

### 核心功能
- ✅ 用户注册/登录（微信授权）
- ✅ 作业增删改查（每日/每周/每月/自定义）
- ✅ 作业完成打卡
- ✅ 积分获取与统计
- ✅ 奖品管理与兑换
- ✅ 积分流水与兑换记录

### 辅助功能
- ✅ 今日作业视图
- ✅ 作业日历视图
- ✅ 积分过期机制
- ✅ 惩罚扣分机制
- ✅ 管理员权限
- ✅ API 自动文档（Swagger）

## 快速开始

### 1. 后端部署

```bash
cd backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env

# 初始化数据库
mysql -u root -p < scripts/init-db.sql

# 启动服务
uvicorn app.main:app --host 0.0.0.0 --port 3000 --reload
```

### 2. 小程序开发

1. 用微信开发者工具打开 `homework-mini` 目录
2. 修改 `app.js` 中的 `baseUrl` 为你的服务器地址
3. 配置微信小程序 AppID

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | 微信小程序原生 |
| 后端 | Python + FastAPI |
| ORM | SQLAlchemy 2.0 |
| 数据库 | MySQL 8.0 |
| 缓存 | Redis 7.x |
| 定时任务 | APScheduler |
| 部署 | Docker + Gunicorn + Uvicorn |

## API 接口

启动服务后访问 Swagger 文档：http://localhost:3000/docs

详见 [backend/README.md](backend/README.md)

## 开发计划

- [x] PRD 产品需求文档
- [x] TECH_DESIGN 技术设计文档
- [x] 后端项目结构
- [x] 数据库模型
- [x] 用户模块（登录/信息）
- [x] 作业模块（CRUD/今日/日历）
- [x] 积分模块（打卡/统计/流水）
- [x] 奖品模块（管理/兑换/记录）
- [x] 小程序首页
- [x] 小程序积分页
- [x] 小程序兑换页
- [x] 小程序个人页
- [ ] 服务器部署上线
- [ ] 微信审核发布
