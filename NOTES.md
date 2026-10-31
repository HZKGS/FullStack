# 进度沉淀

## 已完成

- [x] 阅读项目 Markdown 文档、`AGENT.md`、`AGENT_RULES.md` 和安装说明 PDF。
- [x] 建立并运行 `biz_bp` Flask 工程。
- [x] 确认项目虚拟环境的 Flask、Flask-CORS、PyJWT、bcrypt、PyMongo 可用。
- [x] 将 MongoDB 9.0.4 解压到项目内 `.mongo/server`，并使用项目内数据目录启动。
- [x] 导入 120 条 business 和 600 条 review，创建 4 个 demo users。
- [x] 建立本地 gitignored `.env.local`，不输出密钥。
- [x] 通过 Flask test client 端到端测试。
- [x] 通过真实 HTTP 进程验证 health、登录、CORS、业务/评论创建删除和 token 撤销。
- [x] 建立并解析 17 个请求的 Postman collection。
- [x] 建立 LocalLens Angular 前端，展示 MongoDB 业务数据、搜索、分类、分页和城镇统计。
- [x] Angular 生产构建和 2 个单元测试通过。
- [x] 通过 headless Chrome 截图确认 120 条业务数据实际渲染。
- [x] 导出四类集合 JSON，并生成 `requirements.lock.txt`。
- [x] 增加 CORS、重复创建 409、未认证 401 和非法 ObjectId 测试。

## 进行中

- [ ] 在 Postman Desktop 中导入并实际运行 collection。
- [ ] 保存 Postman 测试结果和 API 文档证据。

## 待办

- [ ] 安装 MongoDB Database Tools 或继续使用 Python 导出 fallback。
- [ ] 生成代码/数据 ZIP、代码 PDF、端点摘要 PDF、自评表 PDF 和演示视频。
- [ ] 完成最终提交前逐项检查。

## 当前状态摘要

- MongoDB：`127.0.0.1:27017`，数据目录 `G:\FullStack\.mongo\data`。
- Angular UI：`http://127.0.0.1:4200/`。
- Flask API：`http://127.0.0.1:5000/`。
- 一键启动：`G:\FullStack\run_locallens.ps1`。
- API：Flask 应用可在 `127.0.0.1:5000`（或 `PORT` 指定端口）启动。
- 测试：`.\scripts\run_smoke_test.ps1` 通过。
- 工作日记：`G:\FullStack\WORKLOG.md`。