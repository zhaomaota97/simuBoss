# simuBoss Backend

一个为 `simuBoss` 前端控制台准备的 Python 后端骨架，目标是逐步承接：

- 登录鉴权
- LLM / Agent runtime
- LangGraph 工作流
- 资产库 / 任务状态
- 未来的知识库与工具调用

## 运行

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -e .
uvicorn app.main:app --reload --port 8000
```

## 默认账号

- 用户名：`admin`
- 密码：`123456`

可以通过环境变量覆盖：

```env
SIMUBOSS_ADMIN_USERNAME=admin
SIMUBOSS_ADMIN_PASSWORD=123456
SIMUBOSS_FRONTEND_ORIGIN=http://127.0.0.1:5173
SIMUBOSS_DEEPSEEK_API_KEY=
SIMUBOSS_DEEPSEEK_MODEL=deepseek-chat
SIMUBOSS_DEEPSEEK_BASE_URL=https://api.deepseek.com
```

## 当前接口

- `GET /health`
- `POST /auth/login`
- `POST /auth/logout`
- `GET /auth/me`
- `POST /runtime/tasks/execute`

## 当前 LangGraph 能力

当前是一个可运行的最小图：

`planner -> workers -> synthesizer`

先用结构化占位逻辑把任务流跑通，后面可以逐步替换为真实 LLM、工具调用和资产库读写。
