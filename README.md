# simuBoss

`simuBoss` 现在分成两部分：

- `src/`：现有 Vue 前端控制台
- `backend/`：新的 Python + LangGraph 后端骨架

## 前端

当前前端仍然可以独立开发：

```bash
npm install
npm run dev
```

默认地址：

- `http://127.0.0.1:5173`

## 后端

后端目录在 `backend/`，目前已经提供：

- FastAPI 服务入口
- 固定账号登录接口
- 健康检查接口
- LangGraph runtime 骨架
- 任务执行 API

启动方式：

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -e .
uvicorn app.main:app --reload --port 8000
```

可参考：

- [backend/README.md](C:/Users/40902/Desktop/simuBoss/backend/README.md)
- [backend/.env.example](C:/Users/40902/Desktop/simuBoss/backend/.env.example)

## 迁移方向

接下来可以逐步把这些能力从前端迁到后端：

- 登录鉴权
- LLM 调用
- 调度器
- 资产库
- 知识库与工具调用

这样前端会逐步收敛成控制台，后端则变成真正的 Agent Runtime。
