# simuBoss

`simuBoss` 是一个基于 Vue 3、Vite、Pinia 的多员工协作模拟器。

当前项目已改为纯前端部署模式，直接由浏览器请求 DeepSeek API。

## 本地开发

1. 安装依赖

```bash
npm install
```

2. 创建环境变量文件

```bash
cp .env.example .env
```

3. 在 `.env` 中填写前端可见的 DeepSeek 配置

```env
VITE_DEEPSEEK_API_KEY=your_deepseek_api_key
VITE_DEEPSEEK_MODEL=deepseek-chat
VITE_DEEPSEEK_BASE_URL=https://api.deepseek.com
```

4. 启动开发环境

```bash
npm run dev
```

默认地址：

- `http://localhost:5173`

## 构建产物

生成生产构建：

```bash
npm run build
```

构建完成后，静态文件位于 `dist/`。

## 注意事项

- `VITE_*` 环境变量会被打进前端产物，任何访问页面的人都能看到 API Key。
- 这个仓库当前没有后端代理层，也不会替你隐藏密钥。
- 如果 DeepSeek 对浏览器直连请求做了 CORS 限制，部署后可能仍需要重新加一个代理层。
