# AGENT.md

> 本文件为 AI Agent 执行“Flask + MongoDB CRUD API”作业项目的操作指南。Agent 应严格按照本文件执行任务，确保满足指导书中的评分标准。
>
> ```
> 通用行为准则见 [AGENT_RULES.md](./AGENT_RULES.md)，优先于本文件。本文件只描述本项目如何做。
> ```

------

## 1. 项目目标

构建一个 **Python Flask 后端 API**，连接 **MongoDB**，围绕自选数据集实现完整 CRUD、复杂查询、JWT 认证与权限控制，并产出测试、文档与提交包。

**最终截止**：2026 年 11 月 6 日（周五）中午 12:00

------

## 2. 评分标准与 Agent 对应动作

| 标准           | 权重 | Agent 必须完成                                               |
| :------------- | :--- | :----------------------------------------------------------- |
| 数据集选择     | 15%  | 选择 ≥100 条顶层文档、含子文档、多集合、多类型数据的数据集（禁止 Yelp） |
| 数据库功能     | 25%  | 完整 CRUD + 多值搜索 + 聚合管道 + 地理查询                   |
| API 结构与设计 | 25%  | RESTful、正确 HTTP 动词/状态码、Blueprint 模块化             |
| 可用性         | 25%  | 输入验证、错误处理、多前端支持（CORS）                       |
| 提交包         | 10%  | 代码 Zip、数据 Zip、视频、代码 PDF、端点摘要 PDF、Postman 测试/文档 PDF、自评表 |

------

## 3. 数据集准备流程

Agent 按以下顺序执行，并生成 `make_dataset.py`：

1. **下载/生成数据**：转换为 JSON 格式。
2. **导入 MongoDB**：优先使用 `mongoimport`；当前项目环境未含 Database Tools 时使用 `scripts/import_seed_data.py` 等价导入。
3. **合并子文档**：将 reviews、tips、photos 等合并进主文档。
4. **处理不一致性**：
   - 删除孤立子文档
   - 清理非活跃用户
   - `user_id` 转换为 `_id`
   - 生成 GeoJSON `location` 字段
5. **导出备份**：`mongoexport` 生成各集合 JSON 文件（提交用）。

**验收标准**：顶层文档 ≥100 条；至少 1 个子文档集合；至少 2 个集合；数据类型涵盖文本/数值/日期/地理坐标/布尔值。

------

## 4. 项目结构（必须遵守）

text

```
biz_bp/
├── app.py                  # 主入口，注册 Blueprints + CORS
├── globals.py              # secret_key、MongoDB 连接
├── decorators.py           # jwt_required、admin_required
├── blueprints/
│   ├── businesses/
│   │   └── businesses.py
│   ├── reviews/
│   │   └── reviews.py
│   └── auth/
│       └── auth.py
├── requirements.txt
└── data/                   # 数据集 JSON
```



------

## 5. API 端点清单（必须全部实现）

| 方法   | URL                                       | 权限     | 成功码 |
| :----- | :---------------------------------------- | :------- | :----- |
| GET    | `/api/v1.0/businesses`                    | 公开     | 200    |
| POST   | `/api/v1.0/businesses`                    | 注册用户 | 201    |
| GET    | `/api/v1.0/businesses/<id>`               | 公开     | 200    |
| PUT    | `/api/v1.0/businesses/<id>`               | 注册用户 | 200    |
| DELETE | `/api/v1.0/businesses/<id>`               | 管理员   | 204    |
| GET    | `/api/v1.0/businesses/<id>/reviews`       | 公开     | 200    |
| POST   | `/api/v1.0/businesses/<id>/reviews`       | 注册用户 | 201    |
| GET    | `/api/v1.0/businesses/<id>/reviews/<rid>` | 公开     | 200    |
| PUT    | `/api/v1.0/businesses/<id>/reviews/<rid>` | 注册用户 | 200    |
| DELETE | `/api/v1.0/businesses/<id>/reviews/<rid>` | 管理员   | 204    |
| GET    | `/api/v1.0/login`                         | 公开     | 200    |
| GET    | `/api/v1.0/logout`                        | 已登录   | 200    |

**状态码规范**：GET 集合/单个 200/404；POST 201/400/409；PUT 200/404；DELETE 204/404。

------

## 6. 认证与权限

- **JWT**（pyjwt，HS256）+ **bcrypt** 密码哈希。
- **黑名单**：logout 时将 token 插入 `blacklist` 集合，`jwt_required` 需校验黑名单。
- **三级权限**：
  - 公开：GET 业务/评论
  - 注册用户：POST/PUT（`@jwt_required`）
  - 管理员：DELETE（`@jwt_required` + `@admin_required`）
- 生成 `create_users.py` 创建至少 1 个普通用户 + 1 个管理员。

------

## 7. 进阶查询（必须实现）

### 7.1 聚合管道

至少实现一个多阶段管道：`$match → $project → $unwind → $match → $sort → $skip → $limit`，并提供按城镇 `$group` 统计业务数量的端点。

### 7.2 地理空间查询

- 创建 `2dsphere` 索引。
- 使用 `$geoNear` 查找附近业务（`maxDistance`、`minDistance`、`distanceField`、`spherical: true`）。

------

## 8. 代码生成原则

1. **模块化**：每个 Blueprint 独立文件，共享资源放 `globals.py` / `decorators.py`。
2. **错误处理**：所有端点必须有输入验证 + 正确状态码。
3. **注释**：JSDoc 风格，便于生成文档。
4. **测试**：每个端点配套 Postman 测试脚本。
5. **多前端支持**：启用 `flask-cors`。
6. **分页**：支持 `pn`（页码）和 `ps`（每页数量）参数。

------

## 9. 测试与文档产出

Agent 必须生成：

1. **Postman Collection**，含自动化测试：
   - 登录 → 存 `jwt_token`
   - 添加业务 → 201，存 `new_biz_url`
   - 添加评论 → 201，存 `new_review_url`
   - 获取/更新业务 → 200
   - 删除评论/业务 → 204
   - 登出 → 200
2. **Postman 文档**：每个请求含描述、参数说明、示例请求/响应，发布到 Web。
3. **提交包**：代码 Zip、数据 Zip（各集合 JSON）、≤5 分钟视频、代码列表 PDF、API 端点摘要 PDF、Postman 测试结果 PDF、Postman 文档 PDF、自评表 PDF。

------

## 10. 环境搭建（Windows）

cmd

```
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
cd G:\FullStack\biz_bp
python -m venv venv
venv\Scripts\activate
pip install flask flask-cors pyjwt bcrypt pymongo
npm config set registry https://registry.npmmirror.com
```



MongoDB 启动：

powershell

```
Set-Location 'G:\FullStack\biz_bp'
.\scripts\start_mongo.ps1

# 项目内 MongoDB 服务端位于 G:\FullStack\.mongo\server，数据目录为 G:\FullStack\.mongo\data。
# 若安装 MongoDB Database Tools，可使用 mongosh；当前基线运行不依赖 mongosh。
```



------

## 11. Agent 执行检查清单

- □ 

  数据集 ≥100 条，含子文档、多集合、多类型

- □ 

  所有 CRUD 操作完整（业务 + 评论子文档）

- □ 

  JWT 认证 + 黑名单生效

- □ 

  管理员权限装饰器正确

- □ 

  输入验证（必填字段、类型、范围）

- □ 

  分页（`pn`/`ps`）支持

- □ 

  聚合管道查询已实现

- □ 

  地理空间查询已实现

- □ 

  Postman 自动化测试全部通过

- □ 

  Postman 文档已发布

- □ 

  提交包 8 项文件齐全

- □ 

  自评表对照评分标准填写

------

## 12. 禁止事项

- ❌ 禁止使用 Yelp Open Dataset。
- ❌ 禁止跳过输入验证直接写库。
- ❌ 禁止在 DELETE 端点缺少管理员校验。
- ❌ 禁止提交缺少黑名单校验的 JWT 实现。
- ❌ 禁止遗漏子文档（reviews）的独立 CRUD 端点。

------

## 13. 参考资源

- Flask：https://flask.palletsprojects.com/
- PyMongo：https://pymongo.readthedocs.io/
- MongoDB 聚合：https://docs.mongodb.com/manual/core/aggregation-pipeline/
- JWT：https://jwt.io/
- Postman：https://learning.postman.com/
------

## 14. 当前工程初始化约定

- 工程根目录：`G:\FullStack`；Flask 工程目录：`G:\FullStack\biz_bp`。
- 数据集采用**可复现的合成 LocalLens 数据生成器**，禁止使用 Yelp Open Dataset。
- 所有运行时生成物、MongoDB 数据目录和提交产物必须位于 `G:\FullStack` 内。
- 当前阶段已完成真实 MongoDB 导入、用户创建、端到端测试与真实 HTTP 验证；证据记录在 `NOTES.md`、`WORKLOG.md` 和 `biz_bp\docs\TEST_EVIDENCE.md`。
- 现有 Markdown 是默认信息源；除非用户明确授权（例如安装说明 PDF），不得为补充上下文而扫描 `C:\` 或读取未授权的非 Markdown 文件。

## 15. 初始化后的目录

```text
G:\FullStack\
├── AGENT.md
├── AGENT_RULES.md
├── AGENT_RULE.md
├── AGENTS.md
├── README.md
├── DECISIONS.md
├── ERROR.md
├── NOTES.md
├── WORKLOG.md
├── .mongo\data\
├── .mongo\server\
├── run_locallens.ps1
├── stop_locallens.ps1
├── locallens-ui\
└── biz_bp\
    ├── app.py
    ├── make_dataset.py
    ├── create_users.py
    ├── globals.py
    ├── decorators.py
    ├── utils.py
    ├── requirements.txt
    ├── blueprints\
    │   ├── auth\
    │   ├── businesses\
    │   └── reviews\
    ├── tests\
    ├── data\
    ├── docs\
    ├── postman\
    └── scripts\
```
## 16. 前端展示层

- Angular 工程位于 `G:\FullStack\locallens-ui`，开发服务器默认端口为 4200。
- 前端直接调用 Flask API `http://127.0.0.1:5000/api/v1.0`，展示业务搜索、分类过滤、分页和城镇统计。
- 一键启动：`G:\FullStack\run_locallens.ps1`；停止 API/UI：`G:\FullStack\stop_locallens.ps1`。
- 前端生产构建：`cd G:\FullStack\locallens-ui; npm run build`。
- 前端单元测试：`cd G:\FullStack\locallens-ui; npx ng test --watch=false`。