# Software Tester Skill (软件测试工程师)

一个集成了 **测试用例生成** 与 **自动执行** 能力的 AI Skill，可基于需求文档（docx / md / 文本描述）产出标准化的测试思维导图与测试用例表，并在用户明确要求时，通过 MCP 服务自动执行用例。

## 功能特性

- **测试点思维导图**：生成 `.xmind` + `.drawio` 双格式可编辑思维导图，覆盖正向 / 边界 / 异常 / 权限 / 性能 / 安全等测试类型。
- **标准化测试用例表**：生成符合「测试管理平台导入模版」的 34 列 `.xlsx` 用例表，可直接导入测试管理平台。
- **自动执行用例**：集成 `playwright`（浏览器自动化）与 `captcha`（验证码识别）MCP 服务，可自动执行 UI 用例并回填结果。
- **模糊用例标记**：执行过程中遇到步骤/预期结果不明确的用例，标记为 `AMBIGUOUS` 并列出待确认问题，不猜测执行。

## 目录结构

```
software-tester/
├── SKILL.md                        # Skill 主定义（工作流 + 输出规范）
├── README.md                       # 使用说明（本文件）
└── references/
    ├── test_case_template.md       # 测试用例导入模版规范（34 列）
    ├── mcp_integration.md          # MCP 集成参考（captcha / playwright）
    └── execution_workflow.md       # 自动执行用例工作流
```

## 前置条件

1. **启用 MCP 服务**（在 IDE 中配置并启用）：
   - `playwright` — 浏览器自动化（24 个工具）
   - `captcha` — 验证码识别（2 个工具）

   MCP 服务器通过 `mcp.json` 配置文件注册（IDE 全局配置位于 `C:\Users\<用户名>\AppData\Roaming\Lingma\SharedClientCache\mcp.json`），配置示例：

   ```json
   {
     "mcpServers": {
       "playwright": {
         "command": "npx",
         "args": ["@playwright/mcp@0.0.31"],
         "env": {
           "PLAYWRIGHT_BROWSER_PATH": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
         }
       },
       "captcha": {
         "command": "python",
         "args": ["D:/study/MCP/catpcha_mcp.py"]
       }
     }
   }
   ```

   - `playwright` 需要 Node.js 环境（`npx` 可用）。
   - `PLAYWRIGHT_BROWSER_PATH` 是 Playwright 官方标准环境变量，用于指定本机浏览器可执行文件路径（如 Chrome），避免下载浏览器内核；仅在 `mcp.json` 的 `env` 字段中配置即可，无需设置系统环境变量。
   - `captcha` 需要 Python 环境，并安装依赖：`pip install fastmcp ddddocr`。
   - 保存后需在 IDE 中刷新/重连 MCP 服务器，确认状态为「已连接」。
   - 详细配置说明见 `references/mcp_integration.md`。

2. **Python 环境**（生成 .xlsx 需要）：
   ```bash
   pip install openpyxl
   ```

## 使用方式

### 1. 生成测试用例

> 生成阶段**不会自动执行**用例，只产出思维导图和用例表。

```
根据这份需求文档生成测试用例
```

产出物：
- 测试点思维导图：`xxx.xmind` + `xxx.drawio`
- 测试用例表：`xxx.xlsx`（34 列，可直接导入测试管理平台）

### 2. 执行测试用例

> 只有明确说「执行用例」时才会执行。

```
执行用例，文件路径是 D:\tests\用例.xlsx
```

执行流程：
1. 确认用例文件路径与执行范围（全部 / 指定模块 / 指定用例）
2. 确认被测系统 URL 与登录凭据
3. 用 `playwright` 驱动浏览器逐条执行用例
4. 遇到验证码时用 `captcha` 自动识别
5. 截图留证（保存至 `evidence/` 目录）
6. 结果回填到用例表（V~Y 列）
7. 生成执行报告

### 3. 执行结果说明

| 结果 | 用例表标记 | 含义 |
|------|-----------|------|
| PASS | OK | 所有步骤执行成功，预期结果全部验证通过 |
| FAIL | NG | 某步骤失败或预期结果未满足 |
| SKIP | SKIP | 不可执行（性能/安全测试、缺少前置条件） |
| AMBIGUOUS | AMBIGUOUS | 步骤/预期结果不明确，需人工确认 |

> **模糊用例（AMBIGUOUS）**：遇到以下情况会标记为模糊并列出待确认问题，**不会猜测执行**：
> - 步骤描述不明确，无法确定操作哪个元素
> - 预期结果表述模糊，无法客观断言
> - 步骤缺失或前后矛盾
> - 页面出现多个相似元素/弹窗
> - 需要人工判断的业务规则或外部依赖

## 输出规范要点

- **思维导图**：`.xmind`（ZIP 内含 content.json / metadata.json / manifest.json）+ `.drawio`（XML）
- **用例表**：34 列（A~AH），表头在第 10 行，数据从第 11 行开始
- **字段格式**：前置条件 / 测试方法和步骤 / 预期结果 一律单行、用中文分号 `；` 分隔、编号 `1、2、3、`
- **用例编号**：`TC-{模块缩写}-{3位数字}`，如 `TC-LOG-001`

## 版本历史

| 版本 | 说明 |
|------|------|
| V1.0 | 集成 captcha / playwright MCP，支持自动执行用例；默认不执行、需提供用例文件路径、模糊用例标记 AMBIGUOUS |

## 远程仓库

- 仓库：`https://e.coding.csair.com/codingcorp/22851/TesterSkills.git`
- 分支：`master`（稳定版）、`V1.0`（开发版）
