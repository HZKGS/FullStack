### 1. 后端 API 代码（Zip 文件）

- 一个 Zip 文件，包含运行后端 API 所需的**所有代码文件**。
- 可以是单个 `app.py`，也可以是 Flask Blueprints 分模块的多文件结构。
- 如果有不存放在 MongoDB 中的配置文件等，也要一并放入。

### 2. 数据库集合 JSON 文件（Zip 文件）

- 一个 Zip 文件，内含**每个 MongoDB collection 一个 JSON 文件**。
- 这些 JSON **必须通过 `mongoexport` 从你最终数据库导出**，不能直接提交原始数据集。
- 这样能体现你做的数据修改与转换。

### 3. 演示视频（≤5 分钟，mp4）

视频必须包含三部分：

- **(i)** 介绍你的应用领域和数据集；
- **(ii)** 用 **Postman** 演示 API 功能；
- **(iii)** 代码走查（walkthrough）。

注意：

- 不需要出镜，但**必须有语音解说**。
- 超过 5 分钟有惩罚：最多允许 +10%（即 5.5 分钟）不扣分；明显超过的部分不予评阅。

### 4. 单独的 PDF 文件（若干）

需要提交以下 PDF：

- **完整后端 API 代码清单**（code listing）；
- **所有 API endpoints 的摘要**（summary of all API endpoints）；
- **Postman 自动化测试运行结果的打印/截图**（printout of the result of running an automated collection of tests）；
- **Postman 生成的 API 文档**（printout of the API documentation generated through Postman）。

### 5. 自评表（Self-Evaluation Sheet）

- 使用提供的 `CW1 Assessment Grid.xlsx`，按各项评分标准给自己打分并写简短理由。
- 自评本身不计入最终分数，但**提交它会计入 “Submission Package” 这一项**。

### 6. 如使用 AI，还需 Design and Implementation 文档

- 规格书明确允许使用 AI（如 GitHub Copilot），但要求：
  - 在 Design and Development 文档中说明哪些部分是 AI 生成的；
  - 包含 AI 聊天的历史记录（prompts 和 responses）；
  - 在视频代码走查中展示你对复杂代码的深入理解。