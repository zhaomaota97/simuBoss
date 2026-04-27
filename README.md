# simuBoss

[中文](#中文) | [English](#english)

---

## 中文

### 项目简介

simuBoss（Boss模拟器）是一个模拟真实公司的agent编排平台，是支持可视化管理的实验性项目。它尝试把“老板控制台”“员工招募”“团队搭建”“组织画布”“资产管理”和“任务运行时”放进同一个工作空间中，用更直观的方式表达 AI 角色、团队结构和执行流程。

当前仓库主要包含三部分：

- Vue 3 前端：用于 Boss 控制台、员工与团队管理、公司大楼画布、资产库等界面
- FastAPI + LangGraph 后端：用于登录鉴权、健康检查、任务流式执行
- `ppt/` 原型目录：用于基于 `pptx` 模板和结构化 JSON 生成 PPT

### 核心能力

- Boss 控制台：任务派发、审批流、运行状态和执行反馈
- 员工中心：招募与配置经理 / 员工角色
- 团队中心：可视化搭建团队结构
- 公司大楼：通过画布管理楼层、团队和员工布局
- 资产库：管理可复用的知识、模板和交付物资产
- 人才市场：浏览预设团队与员工推荐
- 运行时后端：通过 SSE 流式返回任务执行过程

### 技术栈

#### 前端

- Vue 3
- Vite
- Pinia
- Vue Router
- Tailwind CSS
- Reka UI

#### 后端

- FastAPI
- Uvicorn
- LangGraph
- LangChain Core
- Pydantic / pydantic-settings

#### PPT 原型

- Python
- `python-pptx`
- JSON 驱动的模板化 PPT 生成

### 仓库结构

```text
simuBoss/
├─ src/                    # Vue 前端应用
│  ├─ components/          # 通用 UI、画布与业务组件
│  ├─ router/              # 前端路由
│  ├─ services/            # API / 运行时相关调用
│  ├─ stores/              # Pinia 状态管理
│  └─ views/               # 主要页面
├─ backend/                # FastAPI + LangGraph 后端
│  ├─ app/
│  │  ├─ api/              # auth / health / runtime 路由
│  │  ├─ graphs/           # LangGraph 图定义
│  │  ├─ schemas/          # 请求 / 响应模型
│  │  └─ services/         # 运行时与 LLM 服务层
│  ├─ pyproject.toml
│  └─ .env.example
├─ ppt/                    # PPT 生成原型
│  ├─ app.py               # 模板驱动的 PPT 生成脚本
│  ├─ content.json         # 示例结构化内容
│  └─ *.pptx               # PPT 模板文件
├─ .env.example            # 前端环境变量示例
├─ package.json
└─ README.md
```

### 主要页面

当前前端路由包括：

- `/login`：登录页
- `/`：Boss 控制台
- `/employees`：员工中心 / 招募页
- `/teams`：团队中心
- `/market`：团队与员工市场
- `/assets`：资产库
- `/building`：公司大楼可视化画布

### 快速开始

#### 1. 安装前端依赖

```bash
npm install
```

#### 2. 配置前端环境变量

参考根目录 `.env.example` 创建本地 `.env`：

```env
VITE_DEEPSEEK_API_KEY=your_deepseek_api_key
VITE_DEEPSEEK_MODEL=deepseek-chat
VITE_DEEPSEEK_BASE_URL=https://api.deepseek.com
VITE_API_BASE_URL=http://127.0.0.1:8000
```

#### 3. 启动前端

```bash
npm run dev
```

默认地址：

- `http://127.0.0.1:5173`

### 后端启动

#### 1. 创建虚拟环境

```bash
cd backend
python -m venv .venv
```

#### 2. 激活虚拟环境

PowerShell：

```powershell
.\.venv\Scripts\Activate.ps1
```

#### 3. 安装后端依赖

```bash
pip install -e .
```

#### 4. 配置后端环境变量

参考 `backend/.env.example` 创建 `backend/.env`：

```env
SIMUBOSS_FRONTEND_ORIGIN=http://127.0.0.1:5173
SIMUBOSS_ADMIN_USERNAME=admin
SIMUBOSS_ADMIN_PASSWORD=123456
SIMUBOSS_DEEPSEEK_API_KEY=
SIMUBOSS_DEEPSEEK_MODEL=deepseek-chat
SIMUBOSS_DEEPSEEK_BASE_URL=https://api.deepseek.com
```

#### 5. 启动后端

```bash
uvicorn app.main:app --reload --port 8000
```

默认地址：

- `http://127.0.0.1:8000`
- Swagger 文档：`http://127.0.0.1:8000/docs`

### 默认登录账号

使用默认后端配置时：

- 用户名：`admin`
- 密码：`123456`

### 后端接口

当前后端接口包括：

- `GET /`：服务元信息
- `GET /health`：健康检查
- `POST /auth/login`：登录
- `POST /auth/logout`：登出
- `GET /auth/me`：恢复 / 校验登录态
- `POST /runtime/tasks/execute`：通过 SSE 流式执行任务

其中运行时接口返回 `text/event-stream`，适合长任务执行反馈。

### PPT 原型说明

`ppt/` 目录是一个相对独立的实验原型，目前的数据流是：

```text
pptx 模板 + content.json -> app.py -> 生成 pptx
```

关键文件：

- `ppt/app.py`：负责复制模板页并写入结构化内容
- `ppt/content.json`：示例输入内容
- `ppt/*.pptx`：模板文件

这一部分后续非常适合扩展为：

- Word -> LLM -> 结构化 JSON -> PPT
- 标准化提案自动生成
- 报告与汇报材料自动化生成

### 当前项目定位

simuBoss 已经不只是静态页面原型，但也还没有完全演进为生产级 SaaS。更准确地说，它是一个：

- 带有产品交互的 AI 团队管理实验项目
- 带有基础后端运行时能力的控制台原型
- 带有独立文档生成方向探索的研发仓库

如果你准备把它发布到 GitHub，比较合适的定位是：

> 一个用于探索 AI 团队招募、组织设计、资产管理与任务编排的可视化 Boss 控制台实验项目。

### Roadmap 建议

- 将 PPT 流程接入后端，做成任务式文档生成服务
- 引入数据库而不是仅依赖本地存储
- 增强角色权限、工具权限和执行沙箱
- 支持 Word / Markdown / 知识库输入
- 为生成内容增加更强的 schema 校验与纠错能力
- 为长任务增加异步队列与下载式结果交付

### License

当前仓库还没有正式附带 License。

如果准备公开发布，建议补充一个明确的许可证，例如：

- MIT
- Apache-2.0
- GPL-3.0

如果没有 License，其他人通常只能浏览代码，而不能默认复用或二次分发。

---

## English

### Overview

simuBoss is an experimental AI team orchestration sandbox. It explores how a single workspace could combine a boss console, employee recruitment, team design, organization layout, asset management, and a lightweight runtime for task execution.

The repository currently contains three main parts:

- A Vue 3 frontend for the boss console and visual management workflows
- A FastAPI + LangGraph backend for authentication, health checks, and streamed task execution
- A standalone `ppt/` prototype for generating PowerPoint files from a template and structured JSON

### Core Features

- Boss console: task dispatch, approvals, runtime status, and execution feedback
- Employee center: recruit and configure manager / worker roles
- Team center: build editable team structures visually
- Company building: place teams and employees on a canvas-based floor layout
- Asset library: manage reusable knowledge, templates, and deliverable assets
- Market: browse preset team and employee recommendations
- Backend runtime: stream task execution results over SSE

### Tech Stack

#### Frontend

- Vue 3
- Vite
- Pinia
- Vue Router
- Tailwind CSS
- Reka UI

#### Backend

- FastAPI
- Uvicorn
- LangGraph
- LangChain Core
- Pydantic / pydantic-settings

#### PPT Prototype

- Python
- `python-pptx`
- JSON-driven PowerPoint generation

### Repository Structure

```text
simuBoss/
├─ src/                    # Vue frontend app
│  ├─ components/          # Shared UI, canvas, and business components
│  ├─ router/              # Frontend routing
│  ├─ services/            # API and runtime helpers
│  ├─ stores/              # Pinia stores
│  └─ views/               # Main pages
├─ backend/                # FastAPI + LangGraph backend
│  ├─ app/
│  │  ├─ api/              # auth / health / runtime routes
│  │  ├─ graphs/           # LangGraph definitions
│  │  ├─ schemas/          # request / response models
│  │  └─ services/         # runtime and LLM service layer
│  ├─ pyproject.toml
│  └─ .env.example
├─ ppt/                    # PPT generation prototype
│  ├─ app.py               # Template-driven PPT generator
│  ├─ content.json         # Sample structured content
│  └─ *.pptx               # PPT template files
├─ .env.example            # Frontend env example
├─ package.json
└─ README.md
```

### Main Pages

Current frontend routes:

- `/login` - login page
- `/` - boss console
- `/employees` - employee center / recruitment
- `/teams` - team center
- `/market` - team and employee market
- `/assets` - asset library
- `/building` - company building canvas

### Quick Start

#### 1. Install frontend dependencies

```bash
npm install
```

#### 2. Configure frontend environment

Create a local `.env` based on `.env.example`:

```env
VITE_DEEPSEEK_API_KEY=your_deepseek_api_key
VITE_DEEPSEEK_MODEL=deepseek-chat
VITE_DEEPSEEK_BASE_URL=https://api.deepseek.com
VITE_API_BASE_URL=http://127.0.0.1:8000
```

#### 3. Start the frontend

```bash
npm run dev
```

Default frontend URL:

- `http://127.0.0.1:5173`

### Backend Setup

#### 1. Create a virtual environment

```bash
cd backend
python -m venv .venv
```

#### 2. Activate the environment

PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

#### 3. Install backend dependencies

```bash
pip install -e .
```

#### 4. Configure backend environment

Create `backend/.env` based on `backend/.env.example`:

```env
SIMUBOSS_FRONTEND_ORIGIN=http://127.0.0.1:5173
SIMUBOSS_ADMIN_USERNAME=admin
SIMUBOSS_ADMIN_PASSWORD=123456
SIMUBOSS_DEEPSEEK_API_KEY=
SIMUBOSS_DEEPSEEK_MODEL=deepseek-chat
SIMUBOSS_DEEPSEEK_BASE_URL=https://api.deepseek.com
```

#### 5. Start the backend

```bash
uvicorn app.main:app --reload --port 8000
```

Default backend URL:

- `http://127.0.0.1:8000`
- Swagger docs: `http://127.0.0.1:8000/docs`

### Default Login

With the default backend configuration:

- Username: `admin`
- Password: `123456`

### Backend API

Current backend routes:

- `GET /` - service metadata
- `GET /health` - health check
- `POST /auth/login` - login
- `POST /auth/logout` - logout
- `GET /auth/me` - restore / validate session
- `POST /runtime/tasks/execute` - stream runtime execution over SSE

The runtime endpoint returns `text/event-stream` and is intended for long-running task feedback.

### PPT Prototype

The `ppt/` directory is a separate prototype pipeline.

Current flow:

```text
pptx template + content.json -> app.py -> generated pptx
```

Key files:

- `ppt/app.py` - copies template slides and injects structured content
- `ppt/content.json` - sample structured input
- `ppt/*.pptx` - source templates

This part of the repo is a strong base for future workflows such as:

- Word -> LLM -> structured JSON -> PPT
- proposal automation
- AI-assisted report generation

### Project Positioning

simuBoss is already more than a static UI mock, but it is not yet a production SaaS system. A more accurate description would be:

- an experimental AI team management product prototype
- a lightweight boss console backed by an extendable runtime shell
- a repository that also explores structured document generation workflows

If you want to publish it on GitHub today, a good positioning line would be:

> An experimental visual boss console for AI team recruitment, organization design, asset management, and task orchestration.

### Roadmap Ideas

- Integrate the PPT pipeline into the backend as a job-based document generation service
- Add persistent database storage instead of local-only state
- Add stronger role, tool, and execution sandbox controls
- Support Word / Markdown / knowledge-base ingestion
- Add stronger schema validation and correction for generated outputs
- Introduce async queues and downloadable results for long-running tasks

### License

This repository does not currently include a finalized license.

If you plan to publish it publicly, consider adding one such as:

- MIT
- Apache-2.0
- GPL-3.0

Without a license, other users can generally view the code but do not automatically have permission to reuse or redistribute it.
