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
6. Both positive flows and
