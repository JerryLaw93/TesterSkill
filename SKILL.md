---
name: tester-skill
description: This skill should be used when the user needs to test a web application end-to-end: generate test cases from requirements/UI into the standard 34-column Excel template (测试管理平台—测试用例导入模版), execute them via Playwright with per-step screenshots, and produce a self-contained Allure HTML report. Triggers on requests like "执行测试用例", "输出 Allure 报告", "补充测试用例", "执行测试并输出报告", "automate these test cases", "run the xlsx test cases", "generate Allure report from execution results", or any task that combines maintaining an xlsx test suite with Playwright execution and Allure reporting.
---

# Tester Skill

End-to-end testing workflow for web applications: **generate → maintain → execute → report**.

## Overview

This skill automates the full Web app QA loop:

1. Generate or extend test cases into the standard 34-column Excel template (`测试管理平台—测试用例导入模版`).
2. Drive a real browser with Playwright, capturing one screenshot per step.
3. Convert execution results into a self-contained Allure HTML report (no Java/Allure CLI required — pure Python).
4. Serve the report locally so the user can open it in a browser.

The skill is designed to be triggered on a working directory that already contains:

- `index.html` (or a running dev server URL)
- `testcases/测试用例.xlsx` (the standard 34-column template)

## When to Use

Trigger this skill when the user says any of:

- "执行测试用例 + 输出报告"
- "跑一下 xlsx 里的用例"
- "补几条测试用例 + 执行 + 出 Allure"
- "用 Playwright 跑这些步骤"
- "把执行结果转 Allure"
- "打开 Allure 报告"

Skip this skill for: backend-only APIs (no DOM), unit tests, performance/load tests.

## Quick Start

```bash
# 0. (Once) install python deps into a venv
python3 -m venv testcases/.venv
testcases/.venv/bin/pip install openpyxl allure-pytest json2allure 2>/dev/null
# (json2allure only needed if using the JSON path; pure-Python path needs nothing)

# 1. Generate / extend test cases
testcases/.venv/bin/python scripts/gen_testcases.py \
    --xlsx testcases/测试用例.xlsx \
    --requirements docs/需求.md

# 2. Execute against the running app (Playwright MCP tools)
#    See references/execution-runbook.md for the full pattern.

# 3. Build the Allure report from the result JSON
testcases/.venv/bin/python scripts/gen_allure.py \
    --results testcases/execution_results.json \
    --out testcases/allure-report

# 4. Serve the report
bash scripts/allure_serve.sh testcases/allure-report 8080
# open http://localhost:8080/testcases/allure-report/index.html
```

## Task 1 — Generate & Maintain Test Cases (`xlsx`)

Use `references/xlsx-template.md` for the 34-column schema (序号, 模块, 用例编号, 优先级, 分类, 是否已评审, 用例描述, 前置条件, 测试方法和步骤, 预期结果, 已自动化, 实际结果, 是否通过, …).

`scripts/xlsx_helpers.py` provides:

```python
from scripts.xlsx_helpers import open_xlsx, set_cell, append_case

wb, ws = open_xlsx('testcases/测试用例.xlsx')
append_case(ws, {
    'cid': 'TC-LOG-007',
    'module1': '登录模块', 'module2': '验证码', 'module3': '大小写',
    'priority': '中', 'category': '功能测试', 'reviewed': '否',
    'desc': '验证码大小写不敏感',
    'precondition': '1、已打开登录页',
    'steps': '1、输入小写验证码；2、点击登录',
    'expect': '1、登录成功',
    'auto': '是',
})
wb.save('testcases/测试用例.xlsx')
```

Conventions:

- `cid` must be unique; format `TC-{MODULE}-{NNN}`.
- Steps and expectations use full-width separators `；` between items; numbering `1、2、3、`.
- Always update the counter cell at row 5, column 3 after appending.

## Task 2 — Execute with Playwright (MCP)

Use the Playwright MCP tools (`browser_navigate`, `browser_snapshot`, `browser_evaluate`, `browser_run_code_unsafe`, `browser_take_screenshot`).

The recommended pattern, documented in `references/execution-runbook.md`:

1. `browser_navigate` to the app URL.
2. `browser_evaluate` to clear `localStorage` and reload (deterministic start).
3. For each test case:
   - Drive the DOM (click/fill) using `browser_click` / `browser_fill_form`.
   - `browser_take_screenshot` after every step → save to `testcases/evidence/steps/<cid>-sN.jpg`.
   - Push a result object `{cid, status, steps:[{idx,status,shot}]}` into a list.
4. Persist the result list:
   - Preferred: `fs.writeFileSync('testcases/execution_results.json', JSON.stringify({summary, results}))` inside `browser_run_code_unsafe`.
   - Fallback: `localStorage.setItem('__exec_results', JSON.stringify(...))`, then read it back.

Always install a **dialog handler** before clicking destructive buttons:

```js
let dialogAction = 'accept';
page.on('dialog', async d => { try { await d[dialogAction](); } catch(e){} });
```

## Task 3 — Build Allure Report (Pure Python, no Java)

`scripts/gen_allure.py` reads `execution_results.json` and writes a self-contained `allure-report/` directory (HTML + JSON data, no Allure CLI). It produces:

- `index.html` — landing page
- `data/test-cases/*.json` — one file per test case
- `data/suites.json` — suite tree
- `widgets/*` — overview, suites, categories, timeline
- `history/` — trend data
- Per-step `evidence/steps/<cid>-sN.jpg` is referenced as an attachment (inline image in Description).

Run:

```bash
testcases/.venv/bin/python scripts/gen_allure.py \
    --results testcases/execution_results.json \
    --out testcases/allure-report
```

Serve:

```bash
bash scripts/allure_serve.sh testcases/allure-report 8080
# open http://localhost:8080/testcases/allure-report/index.html
```

If port 8080 is busy, pick another: `bash scripts/allure_serve.sh testcases/allure-report 9090`.

## Resources

### scripts/
- `xlsx_helpers.py` — load/save/append helpers for the 34-column template.
- `gen_testcases.py` — read a requirements doc, draft cases, write to xlsx.
- `gen_allure.py` — JSON → self-contained Allure HTML (no Java/Allure CLI).
- `allure_serve.sh` — `python3 -m http.server` wrapper that maps a sub-path.

### references/
- `xlsx-template.md` — full 34-column schema with examples.
- `execution-runbook.md` — Playwright MCP execution pattern, dialog handling, screenshot naming.
- `allure-format.md` — JSON shapes expected by `gen_allure.py`.
- `test-points.md` — six-dimension test point checklist (功能/边界/异常/权限/性能/安全).

### assets/
- `测试用例模板.xlsx` — empty 34-column template pre-filled with header rows and example rows 11–14 (LOGIN module) for orientation.
