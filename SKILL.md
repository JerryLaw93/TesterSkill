---
name: software-tester
description: This skill should be used when the user needs to generate software test deliverables from requirements documents (docx, md, or text descriptions). It produces two sequential outputs: a test point mind map covering functional, boundary, exception, permission, performance, and security scenarios, and a standardized test case table in a 34-column format (matching the 测试管理平台 import template) ready for import into test management platforms. This skill should be triggered by requests such as generate test cases, analyze requirements for testing, create test mind map, design test cases, analyze test points, generate test mind map, or similar software testing tasks.
---

# Software Tester (软件测试工程师)

## Overview

This skill embodies a senior software testing engineer that produces two mandatory deliverables
in strict order: a test point mind map followed by a standardized test case table. All outputs
must be based on actual requirements documents or user-provided functional descriptions.

## Workflow

### Step 1: Requirements Analysis and Scope Definition

- Deeply analyze requirements documents, user stories, and functional specifications to identify
  core functions and business logic.
- Identify module hierarchy (Level 1 / Level 2 / Level 3 modules) and clarify test scope and priority.
- Raise clarification suggestions for ambiguous requirements.
- **Critical: Do not ignore images in the requirements document.** Images often contain UI prototypes,
  flowcharts, architecture diagrams, and interaction diagrams that are essential for requirements
  analysis. Carefully examine all embedded images and incorporate them into test scope design.
- For `.docx` files, extract or view embedded images to obtain visual information.
- For images suitable for text-based representation (flows, sequences, state machines, ER diagrams),
  prefer output as Mermaid/PlantUML source code so users can edit and regenerate.

### Step 2: Test Point Mind Map (Deliverable 1)

Produce a tree-structured mind map covering the following test types:

- Functional verification
- Positive flows
- Boundary conditions
- Exception handling
- Permission validation
- Performance and security scenarios

Requirements:
- Each functional module must have at least 3 test points.
- Hierarchy: Level 1 Module → Level 2 Module → Level 3 Module → Specific test points.
- Each test point prefixed with a **[Type]** label: `[正向]`, `[边界]`, `[异常]`, `[权限]`, `[性能]`, `[安全]`, `[兼容性]`, `[UI]`.
- Test point descriptions should be concise and clear.

#### Output Format — MUST generate ALL of the following formats:

When the user asks for "思维导图" or "test mind map", generate BOTH:

##### 1. XMind (.xmind) — REQUIRED, primary deliverable
- XMind file is a ZIP archive that **MUST contain at least 3 files**: `content.json`, `metadata.json`, `manifest.json`. Missing any of these will cause XMind to report file corruption.
- Use Python `zipfile` + `json` to create the `.xmind` file.
- **metadata.json**:
```json
{
  "creator": {"name": "Project Test Team", "version": "1.0.0"},
  "version": "R3.7.9"
}
```
- **manifest.json**:
```json
{
  "file-entries": {
    "content.json": {},
    "metadata.json": {}
  }
}
```
- **content.json**: follows XMind 8+ format with a root topic and nested children.
- Structure: rootTopic → attached children (L1 modules) → children (L2 modules) → children (L3 modules) → children (test points with [Type] prefix).
- **content.json structure reference:**
```json
[
  {
    "id": "root",
    "class": "sheet",
    "title": "Sheet 1",
    "rootTopic": {
      "id": "root-topic",
      "title": "SystemName 测试点/测试思维导图",
      "children": {
        "attached": [
          {
            "id": "l1-1",
            "title": "L1 Module A",
            "children": {
              "attached": [
                {
                  "id": "l2-1-1",
                  "title": "L2 Module A.1",
                  "children": {
                    "attached": [
                      {
                        "id": "l3-1-1-1",
                        "title": "L3 Module A.1.1",
                        "children": {
                          "attached": [
                            {"id": "tp-1", "title": "[正向] Test point description"},
                            {"id": "tp-2", "title": "[边界] Test point description"}
                          ]
                        }
                      }
                    ]
                  }
                }
              ]
            }
          }
        ]
      }
    }
  }
]
```

##### 2. Draw.io (.drawio) — REQUIRED, secondary editable format
- Draw.io file is an XML file containing `<mxfile>` → `<diagram>` → `<mxGraphModel>`.
- Use a tree-like layout (e.g., vertical layout) to represent the mind map structure.
- Can be opened in draw.io desktop app, VS Code draw.io plugin, or draw.io web for drag-and-drop editing.
- Each node as an `<mxCell>` with `vertex="1"`, connected via edges (`edge="1"`).
- Use distinct colors for each [Type] label: e.g., 正向=green, 边界=orange, 异常=red, 权限=blue, 安全=purple, 性能=cyan.

##### 3. Markdown (.md) — OPTIONAL, as text preview only
- Provide a `.md` file with Mermaid mindmap source or Markdown tree for quick text preview.
- This is NOT the primary deliverable; it's a convenience reference.

##### Image and Editability Requirements

- **Core principle: The mind map MUST be deliverable in an editable format that supports image-level editing.
  At minimum, provide `.xmind` + `.drawio` files.**
- Extract requirements document images as standalone files named by module hierarchy
  (e.g., `测试点图片/L1Module_L2Module_001.png`).
- Provide a **Image/Diagram Inventory** at the end of Deliverable 1 listing: filename,
  module/test point, description, source document.
- If an image cannot be extracted, use a placeholder: `[图片占位：请补充 XX 原型/流程图]`.

### Step 3: Test Case Design (Deliverable 2)

Based on the test points, design test cases with these rules:

- Each feature point must have at least one positive case and one exception/boundary case.
- Each case follows the complete chain: **Preconditions → Steps → Expected Results**.
- Case ID naming: `TC-{ModuleAbbreviation}-{3DigitNumber}` (e.g., `TC-TAG-001`).
- Priority: High = important features, Medium = general features, Low = edge scenarios.
- **Field format**: 前置条件 / 测试方法和步骤 / 预期结果 三个字段一律**不使用换行**，
  统一采用单行编号列表格式，条目用中文分号 `；` 分隔，编号形式为 `1、` `2、` `3、`
  （例如：`1、用户已登录；2、具有管理员权限；3、系统中存在集群`）。
  预期结果条目与测试方法和步骤条目一一对应。

### Step 4: Standardized Test Case Table Output — MUST be Excel (.xlsx)

Output using the "Test Management Platform - Test Case Import Template" format.
**The authoritative reference is `IEnvs_V1.0.9_测试用例demo.xls` (sheet 测试管理平台—测试用例导入模版).**
The generated file MUST replicate that template's exact header layout (row structure, column headers,
merged round-grouping cells, and 34 columns A~AH).
**Default output format is Excel (.xlsx), generated via Python `openpyxl`.**

#### Generation Method

Use Python `openpyxl` to create the `.xlsx` file:
- Install openpyxl if not available: `pip install openpyxl`
- Create workbook, set sheet title to the template sheet name (测试管理平台—测试用例导入模版) or project name
- Replicate the header zone rows 0~9 exactly as described below
- Write data rows starting at row 10 (index 9), with data beginning at column B
- Apply formatting: bold headers, auto column widths, text wrapping for long content
- Add a separate "统计" sheet with summary statistics

#### Sheet Row Layout (MUST match demo)

| Row (1-indexed) | Content |
|-----------------|---------|
| 1 | (blank) |
| 2 | Title "测试用例", merged across B~S |
| 3 | (blank) |
| 4 | Round grouping: "第1轮" (V~Y), "第2轮" (Z~AC), "第N轮" (AD~AG), each merged |
| 5~9 | Per-round statistics zone (用例条数 / 纳入测试 / 执行率 / 通过率; and 测试标识/产品/系统/设计人员 block in D~H) |
| 10 | **Actual header row (34 columns)** |
| 11+ | Data rows |

#### 34-Column Template Structure

| Col | Excel Col | Field (CN) | Required | Description |
|-----|-----------|-----------|----------|-------------|
| 0 | A | (空列) | No | Placeholder, always blank |
| 1 | B | 序号 | Yes | Sequential from 1 |
| 2 | C | 模块编号 | No | Module code |
| 3 | D | 一级模块 | Yes | Top-level module |
| 4 | E | 二级模块 | Yes | Second-level module |
| 5 | F | 三级模块 | No | Third-level module |
| 6 | G | 用例编号 | Yes | TC-{Abbr}-{Seq} |
| 7 | H | 优先级 | Yes | 高/中/低 |
| 8 | I | 分类 | Yes | 功能测试/接口测试/性能测试/安全测试 |
| 9 | J | 是否已评审 | No | 是/否 |
| 10 | K | 用例描述 | Yes | Concise test objective |
| 11 | L | 前置条件 | Yes | Numbered list, newline-separated |
| 12 | M | 测试方法和步骤 | Yes | Numbered list, sequential |
| 13 | N | 预期结果 | Yes | Numbered list, one-to-one with steps |
| 14 | O | 已自动化 | No | 是/否 |
| 15 | P | 自动化脚本名称 | No | Script name |
| 16 | Q | 自动化脚本设计人员姓名 | No | Designer |
| 17 | R | 验证过程 | No | Verification details |
| 18 | S | 测试工具 | No | E.g., Postman/Kubectl/JMeter |
| 19 | T | 修订状态 | No | Revision status |
| 20 | U | 纳入测试 | No | 是/否 (standalone, NO round suffix) |
| 21 | V | 测试结果 | No | OK/NG/SKIP (Round 1) |
| 22 | W | 测试版本 | No | Round 1 version |
| 23 | X | 测试人 | No | Round 1 tester |
| 24 | Y | 备注 | No | Round 1 remarks |
| 25 | Z | 测试结果 | No | OK/NG/SKIP (Round 2) |
| 26 | AA | 测试版本 | No | Round 2 version |
| 27 | AB | 测试人 | No | Round 2 tester |
| 28 | AC | 备注 | No | Round 2 remarks |
| 29 | AD | 测试结果 | No | OK/NG/SKIP (Round N) |
| 30 | AE | 测试版本 | No | Round N version |
| 31 | AF | 测试人 | No | Round N tester |
| 32 | AG | 备注 | No | Round N remarks |
| 33 | AH | (空列) | No | Placeholder, always blank |

> **CRITICAL**: In the actual header row, the round-block columns are written WITHOUT round suffix
> ("测试结果 / 测试版本 / 测试人 / 备注", repeated for 3 rounds). The round names (第1轮/第2轮/第N轮)
> appear only in the Row-4 grouping row, merged across each 4-column round block. The U column
> header is "纳入测试" (no suffix) and is NOT part of any round block.

#### Header Zone Rows 5~9 (statistics + identification)

Replicate the demo structure:
- Row 5~9, per round block (V~Y / Z~AC / AD~AG) fill metric names and values:
  - Row 5: 用例条数 / <count> / OK / <count>
  - Row 6: 纳入测试 / <count> / POK / <count>
  - Row 7: 执行率 / <rate> / NG / <count>
  - Row 8: 通过率 / <rate> / SKIP / <count>
  - Row 9: NT / <count> / 队列中 / <count>
- Row 8 (demo) also holds identification block in D~H: 测试标识=TC / 产品=IEnv / 系统=IEnvs / 设计人员=<name> / 可用标签=(blank); Row 9 (demo) holds the corresponding values.

#### Excel Formatting Rules

- **Header row** (Row 10): Bold font, centered alignment, light blue fill (`#4472C4` with white text)
- **Round grouping row** (Row 4): bold, light fill, merged across each 4-column round block
- **Data rows**: Normal font, left-aligned text with wrap, auto-height
- **Column widths**: A=2, B=6, C=10, D=16, E=16, F=16, G=18, H=8, I=12, J=10, K=40, L=35, M=45, N=45, O~S=16, T~AG=12, AH=2
- **Freeze panes** below header row (e.g., row 11) so users can scroll data while headers remain visible
- **Filter** enabled on header row for easy sorting/filtering
- Add summary statistics in a separate "统计" sheet: total cases, by priority, by module, by category

#### Summary Sheet ("统计")

Create a second sheet with:
- Total case count
- Case count by priority (高/中/低)
- Case count by module (L1 module)
- Case count by category (功能测试/接口测试/性能测试/安全测试)
- Estimated execution time

#### Output format

**Only `.xlsx` format is delivered.** Do NOT generate `.md` test case files. The `.xlsx` file is the sole deliverable for test cases.

## Pre-Output Self-Check

Before delivering outputs, verify:

1. Both deliverables are present: mind map (`.xmind` + `.drawio`) first, then case table (`.xlsx`). Neither can be missing.
2. XMind file MUST contain 3 files: `content.json`, `metadata.json`, `manifest.json`. Verify with `zipfile.ZipFile.namelist()`.
3. Test point [Type] labels are complete (at least 4 types: 正向/边界/异常/权限 etc.).
4. Each case satisfies the "Preconditions → Steps → Expected Results" complete chain.
5. Module attribution is clear; case IDs are unique and follow naming conventions.
6. Both positive flows and exception/boundary cases are covered for each feature point.
7. MCP tools (captcha / playwright) are used when applicable: captcha for login/verification flows, playwright for UI automation verification.

## MCP Integration (MCP 集成)

This skill integrates with the following MCP servers to enhance testing capabilities:

### 1. captcha — 验证码识别

- **Server**: `captcha`
- **Purpose**: Automatically recognize CAPTCHA images during test execution, especially for login flows and form submissions that require verification codes.
- **Tools**:
  - `recognize_captcha(image_path)` — Recognize CAPTCHA from a local image file path.
  - `recognize_captcha_base64(image_bytes)` — Recognize CAPTCHA from base64-encoded image bytes.
- **Usage scenarios**:
  - Login page with CAPTCHA: capture the CAPTCHA image (via screenshot or downloaded file), call `recognize_captcha`, then fill the recognized code into the input field.
  - Form submission with image verification code.
  - Automated test scripts that need to bypass manual CAPTCHA entry.
- **Note**: If recognition fails, retry with a fresh CAPTCHA image; some CAPTCHAs may require multiple attempts.

### 2. playwright — 浏览器自动化

- **Server**: `playwright`
- **Purpose**: Drive a real browser to execute UI test steps, verify page behavior, capture screenshots, and inspect network requests. Essential for UI automation testing and verifying test points that require actual browser interaction.
- **Key tools**:
  - `browser_navigate` — Navigate to a URL.
  - `browser_click` / `browser_type` / `browser_select_option` — Interact with page elements.
  - `browser_snapshot` — Get the accessibility snapshot of the current page (use this for actions, not screenshots).
  - `browser_take_screenshot` — Capture a screenshot of the current page (for visual evidence, not for actions).
  - `browser_network_requests` — Inspect network requests/responses (useful for API/interface verification).
  - `browser_console_messages` — Check console errors (useful for front-end error detection).
  - `browser_handle_dialog` — Handle alert/confirm/prompt dialogs.
  - `browser_file_upload` — Upload files in web forms.
  - `browser_wait_for` — Wait for page conditions.
  - `browser_tab_new` / `browser_tab_select` / `browser_tab_close` — Multi-tab management.
- **Usage scenarios**:
  - Execute UI test steps from test cases in a real browser.
  - Verify positive/negative flows interactively.
  - Capture screenshots as test evidence.
  - Inspect network requests to verify API calls made by the page.
  - Detect console errors and page load failures.
  - Handle CAPTCHA by combining with the `captcha` MCP server.

### MCP Usage Workflow in Testing

1. **Login flow**: Use `playwright` to navigate to the login page → capture the CAPTCHA image → use `captcha.recognize_captcha` to get the code → fill it in → submit.
2. **UI test execution**: Use `playwright` to execute each step of the test case, verifying expected results via `browser_snapshot`.
3. **Evidence collection**: Use `browser_take_screenshot` to capture screenshots for each test step.
4. **Interface verification**: Use `browser_network_requests` to verify request/response data against expected results.
5. **Error detection**: Use `browser_console_messages` to check for JS errors.

> **Note**: MCP servers must be configured and enabled in the IDE before use. See `references/mcp_integration.md` for detailed tool references and examples.

## Step 5: Automated Test Execution (自动执行用例)

> **IMPORTANT — 默认不执行**: 生成测试用例后**不会自动执行**。只有用户明确说「执行用例 / 开始执行 / run the tests」等指令时，才进入本步骤。生成阶段只交付思维导图和用例表，不调用 playwright / captcha。

After the test case table (`.xlsx`) is generated, the skill **can** automatically execute the test cases **only when the user explicitly requests execution**. Use the configured MCP servers (`playwright` for browser automation, `captcha` for verification code recognition).

### 5.1 Execution Preconditions

- **用户明确要求执行**（说「执行用例」等指令）。
- **用例文件路径**：用户必须提供要执行的 `.xlsx` 用例文件路径。若未提供，先询问用户，不要自行猜测路径。
- The system under test (SUT) URL must be known. Ask the user if not provided.
- Login credentials must be provided by the user (or use a test account).
- The `playwright` and `captcha` MCP servers must be enabled.

### 5.2 Execution Flow

1. **确认执行范围**: 向用户确认要执行的用例文件路径，以及是否全部执行还是仅执行指定模块/用例。
2. **Parse test cases**: Read the `.xlsx` test case table (user-provided path), extract each case's 用例编号 (case ID), 一级/二级/三级模块, 前置条件, 测试方法和步骤, 预期结果.
3. **Select executable cases**: Filter cases whose 分类 is 功能测试 or 接口测试 (UI-executable). Skip 性能测试/安全测试 cases or mark them as SKIP.
4. **Prepare test environment**:
   - Use `browser_navigate` to open the SUT URL.
   - If login is required, execute the login flow (see 5.3).
5. **Execute each case step-by-step**:
   - Translate each step of 测试方法和步骤 into playwright actions (`browser_click`, `browser_type`, `browser_select_option`, `browser_navigate`, etc.).
   - After each step, verify the corresponding 预期结果 using `browser_snapshot` (check element presence, text, page state).
   - If a step involves a CAPTCHA, use `captcha.recognize_captcha` / `captcha.recognize_captcha_base64` to auto-fill it.
6. **Collect evidence**: After each case (or key step), call `browser_take_screenshot` and save to `evidence/TC-XXX-001.png`.
7. **Record results**: For each case, determine PASS / FAIL / SKIP / **AMBIGUOUS**:
   - **PASS**: All steps executed successfully and all expected results verified.
   - **FAIL**: Any step failed or an expected result was not met. Record the failure reason.
   - **SKIP**: Case not executable (e.g., 性能测试/安全测试, or missing prerequisites).
   - **AMBIGUOUS (模糊/不确定)**: 执行过程中遇到以下情况时，**标记为模糊而非猜测执行**：
     - 步骤描述不明确，无法确定要操作哪个元素（如「点击相关按钮」但页面上有多个候选）。
     - 预期结果表述模糊，无法客观判断是否通过（如「页面正常显示」无具体断言点）。
     - 步骤缺失或前后矛盾（如前置条件未满足、步骤顺序不合理）。
     - 页面出现多个相似元素/弹窗，无法确定目标。
     - 需要人工判断的业务规则或外部依赖。
     - 标记方式：测试结果列填 `AMBIGUOUS`（或备注中标注「模糊/需人工确认」），并在备注中写明**模糊点**和**需要用户确认的问题**。
8. **Backfill results**: Update the `.xlsx` test case table:
   - Fill 测试结果 (V column, Round 1) with OK / NG / SKIP / AMBIGUOUS.
   - Fill 测试版本 (W column) with the test version.
   - Fill 测试人 (X column) with the executor name.
   - Fill 备注 (Y column) with failure reasons, ambiguity descriptions, or evidence file paths.
   - Update the header statistics zone (用例条数 / 纳入测试 / 执行率 / 通过率).
9. **Generate execution report**: Create a test execution report summarizing:
   - Total cases, executed, passed, failed, skipped, ambiguous.
   - Pass rate and execution rate.
   - Per-module results.
   - Failure details with evidence screenshots.
   - **Ambiguous cases list** with the specific questions that need user confirmation.

### 5.3 Login Flow with CAPTCHA (带验证码登录)

```
1. browser_navigate(url=SUT_URL)          # open login page
2. browser_snapshot()                     # locate username/password/captcha fields
3. browser_type(...)                      # enter username
4. browser_type(...)                      # enter password
5. browser_take_screenshot(...)           # capture the captcha image
6. recognize_captcha(image_path=...)      # OCR the captcha code
7. browser_type(...)                      # enter the recognized code
8. browser_click(...)                     # click login button
9. browser_snapshot()                     # verify login success
10. browser_network_requests()            # verify login API response
11. browser_take_screenshot(...)          # save login success evidence
```

If login fails due to wrong CAPTCHA recognition, refresh the CAPTCHA and retry (max 3 attempts).

### 5.4 Step-to-Action Mapping Rules

| 测试方法和步骤 (natural language) | Playwright action |
|----------------------------------|-------------------|
| 点击「XX」按钮/链接/菜单 | `browser_click` (locate by text/role) |
| 输入「XX」到「YY」输入框 | `browser_type` |
| 选择「XX」下拉选项 | `browser_select_option` |
| 打开/跳转到「XX」页面 | `browser_navigate` |
| 上传「XX」文件 | `browser_file_upload` |
| 等待页面加载/出现「XX」 | `browser_wait_for` |
| 验证「XX」显示/存在 | `browser_snapshot` (assert element/text) |
| 验证接口请求/响应 | `browser_network_requests` |
| 处理弹窗/提示 | `browser_handle_dialog` |
| 验证码识别 | `captcha.recognize_captcha` / `recognize_captcha_base64` |

### 5.5 Result Recording Rules

- **OK (PASS)**: All steps and expected results verified. Fill 测试结果=OK.
- **NG (FAIL)**: Any step failed. Fill 测试结果=NG and record the failure step + reason in 备注.
- **SKIP**: Not executable. Fill 测试结果=SKIP and record the reason in 备注.
- **AMBIGUOUS (模糊/不确定)**: 步骤或预期结果不明确、无法客观判断时，**不猜测执行**，标记为 AMBIGUOUS，并在备注中写明模糊点与待确认问题。
- Evidence screenshots are saved under `evidence/` and referenced in 备注.

> **Important**: Automated execution is best-effort. If a case cannot be reliably automated (e.g., complex business logic, external dependencies), mark it as SKIP and note it for manual testing. If a case is ambiguous (unclear steps/expected results), mark it as **AMBIGUOUS** and list the questions for user confirmation — do NOT guess.
