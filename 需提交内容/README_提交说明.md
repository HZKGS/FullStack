# CW1 提交包说明（LocalLens）

生成时间：2026-10-30
依据：`需提交内容/Guide.md`（COM661 CW1 提交要求）

## 已生成的文件

| 要求 | 文件 | 状态 |
| :--- | :--- | :--- |
| 1. 后端 API 代码 Zip | `1_Backend_API_Code.zip` | 已生成（biz_bp 全部源码、requirements、.env.example、Postman 集合、docs；已排除 venv/__pycache__/tmp/.env.local） |
| 2. 数据库集合 JSON Zip | `2_Database_Collections_JSON.zip` | 已生成（businesses / reviews / users / blacklist，mongoexport extended JSON 格式） |
| 3. 演示视频 ≤5 分钟 mp4 | — | **需人工录制**（见下） |
| 4. 代码清单 PDF | `4_PDFs/Backend_API_Code_Listing.pdf` | 已生成（带文件头与行号） |
| 4. API 端点摘要 PDF | `4_PDFs/API_Endpoints_Summary.pdf` | 已生成 |
| 4. Postman 自动化测试结果 PDF | `4_PDFs/Postman_Test_Results.pdf` | 已生成（Flask 自动化测试 + 现有证据；**需补真实 Postman Runner 截图**） |
| 4. Postman API 文档 PDF | `4_PDFs/Postman_API_Documentation.pdf` | 已生成（由集合生成；**建议替换为 Postman Publish 导出**） |
| 5. 自评表 | `5_Self_Evaluation_Sheet.xlsx` | 已生成（保留原评分网格并新增 Self-Evaluation 页，加权自评 69.2） |
| 6. AI 使用说明文档 | — | 若课程要求申报 AI，需人工补充 Design & Implementation 文档与聊天记录 |

## 需要人工完成的操作

1. **填写身份信息**：打开 `5_Self_Evaluation_Sheet.xlsx`，把 `Sheet1!B2` 与 `D2` 的 `[Your Name]` / `[Your ID]` 换成真实姓名和学号。
2. **运行 Postman 自动化测试**：导入 `biz_bp/postman/LocalLens.postman_collection.json`，先启动 MongoDB 与 Flask（`.\run_locallens.ps1`），在 Collection Runner 中运行全部 17 个请求，截图或导出运行结果，替换/补入 `4_PDFs/Postman_Test_Results.pdf`。
3. **生成 Postman 官方 API 文档**：在 Postman 中 Publish Documentation 并打印为 PDF，替换 `4_PDFs/Postman_API_Documentation.pdf`（当前版本由集合 JSON 生成，内容等价但非官方导出）。
4. **录制演示视频（≤5 分钟，mp4，必须有语音解说）**，三部分：
   - (i) 应用领域与数据集介绍（LocalLens 本地商户点评；120 businesses / 600 reviews / 4 users，GeoJSON、日期、布尔、嵌套子文档）；
   - (ii) 用 Postman 演示 API：登录拿 JWT、分页与多值 category 过滤、GET/POST/PUT/DELETE business、review CRUD、聚合统计 `/stats/by-town`、地理查询 `/nearby`、401/403/404 错误演示；
   - (iii) 代码走查：`app.py` 蓝图注册与 CORS、`decorators.py` 的 JWT/角色校验、`businesses.py` 的聚合与 `$geoNear`、`reviews.py` 的评分重算。
5. **核实数据导出**：`2_Database_Collections_JSON.zip` 使用项目内 `biz_bp/data/export/*.json`（已为 `mongoexport --jsonArray` 的 extended JSON）。若本机有 Database Tools，建议重新执行 `biz_bp/scripts/export_data.ps1` 后再打包，确保是“最终数据库”的导出。
6. **（如需）AI 使用声明**：整理 AI prompts/responses 与 AI 生成部分说明，放入 Design and Implementation 文档。

## 快速自检

```powershell
Set-Location 'G:\FullStack'
.\run_locallens.ps1 -OpenBrowser
# UI:  http://127.0.0.1:4200/
# API: http://127.0.0.1:5000/api/v1.0/businesses?pn=1&ps=5
```
