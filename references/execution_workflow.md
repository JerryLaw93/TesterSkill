# Automated Test Execution Workflow (自动执行用例工作流)

This document defines the complete workflow for automatically executing test cases generated
by the software-tester skill, using the `playwright` (browser automation) and `captcha`
(verification code recognition) MCP servers.

## Overview

```
生成用例 (.xlsx) → 解析用例 → 准备环境 → 逐条执行 → 收集证据 → 回填结果 → 生成报告
```

---

## Phase 1: Parse Test Cases

Read the generated `.xlsx` test case table and extract the following fields per case:

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

For FAIL cases, record in 备注 (Y column):
```
失败步骤：第3步「点击保存按钮」；失败原因：按钮未找到/页面无响应；证据：evidence/TC-LOG-001_03.png
```

---

## Phase 6: Backfill Results into .xlsx

Update the test case table:

| Column | Field | Value |
|--------|-------|-------|
| V | 测试结果 (第1轮) | OK / NG / SKIP |
| W | 测试版本 (第1轮) | e.g., V1.0 |
| X | 测试人 (第1轮) | executor name |
| Y | 备注 (第1轮) | failure reason / evidence path |

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
- 跳过：2
- 通过率：83.3%
- 执行率：90%

## 按模块统计
| 模块 | 总数 | 通过 | 失败 | 跳过 |
|------|------|------|------|------|
| 登录 | 5 | 4 | 1 | 0 |
| ...   | ... | ... | ... | ... |

## 失败详情
| 用例编号 | 失败步骤 | 原因 | 证据 |
|----------|---------|------|------|
| TC-LOG-003 | 第2步 | 元素未找到 | evidence/TC-LOG-003_02.png |
```

---

## Execution Rules

1. **Best-effort**: If a case cannot be reliably automated, mark SKIP and note for manual testing.
2. **Isolation**: If a case modifies data (create/delete), reset state between cases when possible.
3. **Evidence**: Always capture screenshots; they are the primary proof of execution.
4. **Retry**: CAPTCHA recognition failures → refresh + retry (max 3). Other transient failures → retry once.
5. **Stop conditions**: Stop execution if login fails after 3 attempts, or if the SUT is unreachable.
6. **Report**: Always produce a final execution report with pass/fail/skip statistics.
