# Automated Test Execution Workflow (自动执行用例工作流)

This document defines the complete workflow for automatically executing test cases generated
by the software-tester skill, using the `playwright` (browser automation) and `captcha`
(verification code recognition) MCP servers.

## Overview

```
[用户明确要求执行] → 确认用例文件路径 → 解析用例 → 准备环境 → 逐条执行 → 收集证据 → 回填结果 → 生成报告
```

> **IMPORTANT — 默认不执行**: 生成用例后**不会自动执行**。只有用户明确说「执行用例」等指令时才进入本流程。
> 执行前必须向用户确认**用例文件路径**（`.xlsx`），不要自行猜测。

---

## Phase 0: Confirm Execution Request

**必须满足以下条件才可开始执行：**

1. 用户明确要求执行（如「执行用例」「开始执行」「run the tests」）。
2. 用户提供（或确认）用例文件路径：
   - 若用户未提供，**先询问**，例如：
     > 请提供要执行的用例文件路径（.xlsx）
   - 不要猜测或搜索文件路径后直接执行。
3. 确认执行范围：全部用例 / 指定模块 / 指定用例编号。
4. 确认 SUT URL 与登录凭据。

---

## Phase 1: Parse Test Cases

Read the user-provided `.xlsx` test case table and extract the following fields per case:

| Field | Excel Column | Purpose |
|-------|-------------|---------|
| 用例编号 | G | Unique case ID (e.g., TC-LOG-001) |
| 一级模块 | D | Top-level module |
| 二级模块 | E | Second-level module |
| 三级模块 | F | Third-level module |
| 优先级 | H | 高/中/低 (execution order: 高 first) |
| 分类 | I | 功能测试/接口测试/性能测试/安全测试 |
| 用例描述 | K | Test objective |
| 前置条件 | L | Preconditions |
| 测试方法和步骤 | M | Steps (numbered, `；`-separated) |
| 预期结果 | N | Expected results (one-to-one with steps) |

**Executability filter**:
- Executable: 功能测试, 接口测试 (UI-verifiable)
- SKIP: 性能测试, 安全测试 (or cases requiring external dependencies)

---

## Phase 2: Prepare Test Environment

1. Ask the user for (if not already provided):
   - SUT URL (system under test)
   - Login credentials (username/password)
   - Test version (for 测试版本 column)
   - Executor name (for 测试人 column)
2. Ensure `playwright` and `captcha` MCP servers are enabled.
3. Create the `evidence/` directory for screenshots.

---

## Phase 3: Login (if required)

Follow the login flow in SKILL.md §5.3:

```
browser_navigate(url=SUT_URL)
browser_snapshot()                    # locate fields
browser_type(...)                     # username
browser_type(...)                     # password
browser_take_screenshot(...)          # captcha image
recognize_captcha(image_path=...)     # OCR
browser_type(...)                     # captcha code
browser_click(...)                    # login
browser_snapshot()                    # verify success
```

- If login fails, refresh CAPTCHA and retry (max 3 attempts).
- If login still fails, stop execution and report.

---

## Phase 4: Execute Cases

For each executable case (ordered by priority 高 → 中 → 低):

### 4.1 Step Translation

Translate each numbered step in 测试方法和步骤 into playwright actions using the
mapping table in SKILL.md §5.4:

| Natural language step | Playwright action |
|-----------------------|-------------------|
| 点击「XX」 | `browser_click` |
| 输入「XX」 | `browser_type` |
| 选择「XX」 | `browser_select_option` |
| 打开「XX」页面 | `browser_navigate` |
| 上传「XX」文件 | `browser_file_upload` |
| 等待「XX」 | `browser_wait_for` |
| 验证「XX」 | `browser_snapshot` (assert) |
| 验证接口 | `browser_network_requests` |
| 处理弹窗 | `browser_handle_dialog` |
| 验证码 | `captcha.recognize_captcha*` |

### 4.2 Verification

After each step, verify the corresponding expected result:
- Element presence/text: `browser_snapshot`
- API response: `browser_network_requests`
- Console errors: `browser_console_messages`

### 4.3 Evidence Collection

After each case (and after critical steps), call `browser_take_screenshot` and save as:
```
evidence/{用例编号}_{step}.png
e.g., evidence/TC-LOG-001_01.png
```

---

## Phase 5: Record Results

For each case, determine the result:

| Result | 测试结果 (V) | Condition |
|--------|-------------|-----------|
| PASS | OK | All steps executed, all expected results verified |
| FAIL | NG | Any step failed / expected result not met |
| SKIP | SKIP | Not executable (性能/安全测试, missing prerequisites) |
| AMBIGUOUS | AMBIGUOUS | 步骤/预期结果不明确，无法客观判断，需人工确认 |

**AMBIGUOUS (模糊/不确定) 判定标准** — 遇到以下情况**不要猜测执行**，标记为 AMBIGUOUS：

1. 步骤描述不明确，无法确定操作哪个元素（如「点击相关按钮」但页面有多个候选）。
2. 预期结果表述模糊，无法客观断言（如「页面正常显示」无具体断言点）。
3. 步骤缺失或前后矛盾（前置条件未满足、步骤顺序不合理）。
4. 页面出现多个相似元素/弹窗，无法确定目标。
5. 涉及需要人工判断的业务规则或外部依赖。

For FAIL cases, record in 备注 (Y column):
```
失败步骤：第3步「点击保存按钮」；失败原因：按钮未找到/页面无响应；证据：evidence/TC-LOG-001_03.png
```

For AMBIGUOUS cases, record in 备注 (Y column):
```
模糊：第2步「点击相关按钮」页面存在多个候选按钮；待确认：请明确要点击哪个按钮
```

---

## Phase 6: Backfill Results into .xlsx

Update the test case table:

| Column | Field | Value |
|--------|-------|-------|
| V | 测试结果 (第1轮) | OK / NG / SKIP / AMBIGUOUS |
| W | 测试版本 (第1轮) | e.g., V1.0 |
| X | 测试人 (第1轮) | executor name |
| Y | 备注 (第1轮) | failure reason / ambiguity description / evidence path |

Also update the header statistics zone (rows 5~9):
- 用例条数 = total cases
- 纳入测试 = executed cases
- 执行率 = executed / total
- 通过率 = passed / executed

---

## Phase 7: Generate Execution Report

Create a summary report (`.md` or in the 统计 sheet):

```
# 测试执行报告

- 测试版本：V1.0
- 执行人：XXX
- 执行时间：YYYY-MM-DD HH:mm

## 汇总
- 总用例数：20
- 已执行：18
- 通过：15
- 失败：3
- 跳过：1
- 模糊：1
- 通过率：83.3%
- 执行率：90%

## 按模块统计
| 模块 | 总数 | 通过 | 失败 | 跳过 | 模糊 |
|------|------|------|------|------|------|
| 登录 | 5 | 4 | 1 | 0 | 0 |
| ...   | ... | ... | ... | ... | ... |

## 失败详情
| 用例编号 | 失败步骤 | 原因 | 证据 |
|----------|---------|------|------|
| TC-LOG-003 | 第2步 | 元素未找到 | evidence/TC-LOG-003_02.png |

## 模糊用例（需人工确认）
| 用例编号 | 模糊点 | 待确认问题 |
|----------|--------|-----------|
| TC-LOG-007 | 第2步「点击相关按钮」页面存在多个候选按钮 | 请明确要点击哪个按钮 |
```

---

## Phase 8: Generate Allure Report (Allure 静态报告)

> 可选步骤，用户要求生成 Allure 报告时执行。将执行结果转换为静态 HTML 页面。

### 前置条件

- 安装 Allure 命令行工具：
  - **Windows**：`scoop install allure` 或 `choco install allure`，或官网下载 zip 解压并配置 PATH。
  - **macOS**：`brew install allure`。
  - 验证：`allure --version`。

### 8.1 写入 Allure 结果文件

每个用例在 `allure-results/` 目录下生成一个 `<uuid>-result.json` 文件：

```json
{
  "name": "TC-LOG-001 验证登录功能",
  "status": "passed",
  "stage": "finished",
  "description": "验证用户使用正确账号密码可成功登录",
  "start": 1700000000000,
  "stop": 1700000060000,
  "labels": [
    {"name": "suite", "value": "登录模块"},
    {"name": "testCaseId", "value": "TC-LOG-001"},
    {"name": "severity", "value": "critical"}
  ],
  "steps": [
    {"name": "步骤1：打开登录页", "status": "passed"},
    {"name": "步骤2：输入账号密码", "status": "passed"}
  ],
  "attachments": [
    {"name": "evidence/TC-LOG-001_01.png", "type": "image/png"}
  ]
}
```

### 8.2 状态映射

| 执行结果 | Allure status |
|----------|---------------|
| PASS | `passed` |
| FAIL | `failed` |
| SKIP | `skipped` |
| AMBIGUOUS | `broken` |

### 8.3 生成静态报告

```bash
# 生成报告（allure-results 为执行时写入的结果目录）
allure generate allure-results -o allure-report --clean

# 本地预览（可选）
allure open allure-report
```

### 8.4 输出物（输出位置）

Allure 相关文件统一输出到**用例文件（.xlsx）所在目录**下：

```
<用例文件所在目录>/
├── 用例.xlsx                    # 原始用例文件（含回填的执行结果）
├── evidence/                    # 执行截图证据
├── allure-results/              # 原始结果 JSON（可再次生成报告）
└── allure-report/               # 静态 HTML 报告（index.html 为入口）
```

- `allure-results/` — 原始结果 JSON（可再次生成报告）
- `allure-report/` — 静态 HTML 报告（`index.html` 为入口）

> **静态页面说明**：`allure-report/index.html` 可直接用浏览器打开，无需启动服务；
> 也可将 `allure-report` 目录整体部署到任意静态站点（Nginx、GitHub Pages 等）供团队查看。
> 若用户指定了其他输出目录，则按用户指定位置输出。

---

## Execution Rules

1. **默认不执行**: 生成用例后不自动执行，只有用户明确要求执行时才进入本流程。
2. **用例文件路径**: 执行前必须确认用户提供的 `.xlsx` 用例文件路径，未提供则询问，不自行猜测。
3. **Best-effort**: If a case cannot be reliably automated, mark SKIP and note for manual testing.
4. **不猜测执行**: 遇到模糊/不确定的步骤或预期结果，标记 AMBIGUOUS 并列出待确认问题，不猜测执行。
5. **Isolation**: If a case modifies data (create/delete), reset state between cases when possible.
6. **Evidence**: Always capture screenshots; they are the primary proof of execution.
7. **Retry**: CAPTCHA recognition failures → refresh + retry (max 3). Other transient failures → retry once.
8. **Stop conditions**: Stop execution if login fails after 3 attempts, or if the SUT is unreachable.
9. **Report**: Always produce a final execution report with pass/fail/skip/ambiguous statistics.
