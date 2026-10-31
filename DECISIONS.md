# 决策日志

## D-001 数据集选择
- 决策：选用 OpenDataNI 某 JSON 数据集
- 备选：Kaggle 某数据集
- 理由：含地理坐标与子文档，满足 15% 评分项
- 影响：需生成 GeoJSON location 字段
- 状态：已被 D-002 取代；保留用于回溯。

## D-002 数据集改为可复现的合成 LocalLens 数据
- 决策：使用项目内 `scripts/make_seed_data.py` 生成至少 120 条 business、500 条 review 和测试用户数据。
- 备选：OpenDataNI 外部下载；Yelp Open Dataset。
- 理由：`AGENT.md` 明确禁止 Yelp；当前环境不访问外部网络；合成数据可稳定覆盖文本、数值、日期、地理坐标、布尔值、父/子集合与分页场景。
- 影响：数据不来源于真实企业；最终报告必须如实说明生成方式，并在提交包中包含生成脚本和导出的 JSON。

## D-003 工程目录与运行边界
- 决策：Flask 工程放在 `G:\FullStack\biz_bp`，MongoDB 数据目录放在 `G:\FullStack\.mongo\data`。
- 理由：满足“只在项目文件夹生成”的约束，避免写入系统盘或项目外路径。
- 影响：所有命令、环境变量、导出文件和测试产物均使用上述目录。

## D-004 API 版本与认证风格
- 决策：保留指导书要求的 `/api/v1.0` 前缀和 `GET /login`、`GET /logout`；同时让登录端点兼容 `POST` JSON。
- 理由：满足硬性端点表，同时降低凭证出现在 URL 中的风险；Postman 演示可使用 POST。
- 影响：GET 登录仅作为兼容入口，文档中优先展示 POST。
## D-005 MongoDB 使用项目内解压版本
- 决策：从已有的 `G:\MongoDB\mongodb-windows-x86_64-9.0.4-signed.msi` 将 MongoDB Server 解压到 `G:\FullStack\.mongo\server`，直接运行项目内 `mongod.exe`。
- 备选：系统级安装 MongoDB；启动 Docker Desktop；使用远程数据库。
- 理由：保持数据和服务端二进制在项目目录内，避免新增系统服务或写入用户目录；Docker daemon 当前未运行。
- 影响：启动命令使用 `scripts/start_mongo.ps1`；MongoDB Database Tools 仍需单独安装。

## D-006 本地开发配置使用 gitignored `.env.local`
- 决策：`globals.py` 使用标准库读取 `biz_bp\.env.local`，该文件由 `scripts/init_local_env.ps1` 生成并被 `.gitignore` 排除。
- 理由：不增加 dotenv 依赖，不在源码、文档或日志中写入密码/JWT secret。
- 影响：Postman 运行时从该文件读取管理员密码并填入 collection variable；提交前必须确认 `.env.local` 不进入 ZIP。

## D-007 数据导入/导出 fallback
- 决策：优先保留 `mongoimport`/`mongoexport` 脚本；当前环境使用 PyMongo 的 `import_seed_data.py` 和 `export_data.py`。
- 理由：MongoDB Server MSI 不包含 Database Tools；Python fallback 能维持开发与测试流程。
- 影响：最终提交若严格要求 `mongoexport` 证据，需安装 MongoDB Database Tools 并补跑 PowerShell 脚本。
## D-008 Angular 前端展示策略
- 决策：使用 Angular 22 standalone 组件直接调用 Flask API，展示业务列表、搜索、分类过滤、分页和城镇统计。
- 备选：仅保留 Angular 默认模板；只提供后端 API。
- 理由：用户需要看到项目实际效果，且前端能验证 CORS、分页和 API 响应。
- 影响：Angular 开发服务器使用 4200，Flask API 使用 5000；生产构建的组件样式预算调整为 12/16 kB。