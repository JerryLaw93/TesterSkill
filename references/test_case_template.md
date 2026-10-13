# Test Case Import Template Specification (测试用例导入模版规范)

## Overview

This document specifies the exact format for test case tables that can be directly imported
into test management platforms via Excel.

**Authoritative reference: `IEnvs_V1.0.9_测试用例demo.xls`** (测试管理平台—测试用例导入模版).
The generated Excel MUST match this demo's header layout exactly.

## Sheet Layout (Rows)

| Row | Content | Notes |
|-----|---------|-------|
| Row 0 | (blank) | Top spacing row, always empty |
| Row 1 | Title "测试用例" | Merged across B~S (columns 2~20) |
| Row 2 | (blank) | Spacing row, always empty |
| Row 3 | Round grouping row: "第1轮" / "第2轮" / "第N轮" | Merged: 第1轮=V~Y, 第2轮=Z~AC, 第N轮=AD~AG |
| Row 4~8 | Per-round statistics zone (用例条数 / 纳入测试 / 执行率 / 通过率 + values OK/NG/SKIP) | 5 rows of stats |
| Row 9 | **Header row** (actual column headers) | 34 columns |
| Row 10+ | Data rows | Start from column B |

> **IMPORTANT**: The real column headers are located at **Row 9** (1-indexed). Rows 1~8 above it
> are title / grouping / statistics rows. The header row is NOT at row 1.

## Complete Column Specification (34 Columns, A~AH)

| Col | Excel Col | Field Name (CN) | Required | Description |
|-----|-----------|-----------------|----------|-------------|
| 0 | A | (空列) | No | Placeholder column, always blank |
| 1 | B | 序号 | Yes | Sequential from 1 |
| 2 | C | 模块编号 | No | Module identifier code |
| 3 | D | 一级模块 | Yes | Top-level module name |
| 4 | E | 二级模块 | Yes | Second-level module name |
| 5 | F | 三级模块 | No | Third-level module name |
| 6 | G | 用例编号 | Yes | Format: TC-{Abbr}-{3DigitNum} |
| 7 | H | 优先级 | Yes | High/Medium/Low (高/中/低) |
| 8 | I | 分类 | Yes | 功能测试/接口测试/性能测试/安全测试 |
| 9 | J | 是否已评审 | No | Yes/No (是/否) |
| 10 | K | 用例描述 | Yes | Concise test objective |
| 11 | L | 前置条件 | Yes | Numbered list, same-line, separated by `；` (see Format section) |
| 12 | M | 测试方法和步骤 | Yes | Numbered list, same-line, separated by `；` |
| 13 | N | 预期结果 | Yes | Numbered list, same-line, separated by `；`, one-to-one with steps |
| 14 | O | 已自动化 | No | Yes/No (是/否) |
| 15 | P | 自动化脚本名称 | No | Script file name |
| 16 | Q | 自动化脚本设计人员姓名 | No | Person who wrote automation |
| 17 | R | 验证过程 | No | Verification details |
| 18 | S | 测试工具 | No | Tool used for testing |
| 19 | T | 修订状态 | No | Revision status |
| 20 | U | 纳入测试 | No | Whether included in testing (单列，无轮次后缀) |
| 21 | V | 测试结果 | No | OK/NG/SKIP (Round 1, filled after execution) |
| 22 | W | 测试版本 | No | Round 1 test version |
| 23 | X | 测试人 | No | Round 1 tester name |
| 24 | Y | 备注 | No | Round 1 remarks |
| 25 | Z | 测试结果 | No | OK/NG/SKIP (Round 2) |
| 26 | AA | 测试版本 | No | Round 2 test version |
| 27 | AB | 测试人 | No | Round 2 tester name |
| 28 | AC | 备注 | No | Round 2 remarks |
| 29 | AD | 测试结果 | No | OK/NG/SKIP (Round N) |
| 30 | AE | 测试版本 | No | Round N test version |
| 31 | AF | 测试人 | No | Round N tester name |
| 32 | AG | 备注 | No | Round N remarks |
| 33 | AH | (空列) | No | Trailing placeholder column, always blank |

> **Note on round columns**: In the header row (Row 9), the test-result block columns are written
> WITHOUT a round suffix — i.e. four identical groups each with "测试结果 / 测试版本 / 测试人 / 备注".
> The round (第1轮/第2轮/第N轮) is shown in the grouping row (Row 3) as a merged header spanning
> each 4-column block (V~Y, Z~AC, AD~AG). The "纳入测试" column (U) is a standalone column and is NOT
> part of any round block.

## Column Width Reference (from demo)

Suggested widths (match the demo visually):
A=2, B=6, C=10, D=16, E=16, F=16, G=18, H=8, I=12, J=10, K=40, L=35, M=45, N=45,
O=10, P=16, Q=16, R=16, S=14, T=12, U=12, V=12, W=12, X=12, Y=12, Z~AG=12, AH=2.

## Case ID Naming Convention

Format: `TC-{ModuleAbbreviation}-{3DigitNumber}`

Examples:
- `TC-TAG-001` — Tag management, case 1
- `TC-CLS-002` — Cluster management, case 2
- `TC-DEP-001` — Deployment management, case 1
- `TC-ENV-003` — Environment management, case 3

Abbreviation rules:
- Use 2-4 uppercase letters from the English module name
- Must be unique across the project
- Document the abbreviation mapping at the top of the case table

## Priority Definitions

| Priority | Criteria |
|----------|----------|
| 高 (High) | Core business features, must-pass scenarios, high-risk areas |
| 中 (Medium) | Important but not critical features, common usage scenarios |
| 低 (Low) | Edge cases, rarely used features, cosmetic issues |

## Category Definitions

| Category | Scope |
|----------|-------|
| 功能测试 | UI interaction, business logic, data validation |
| 接口测试 | API endpoints, request/response validation, HTTP status codes |
| 性能测试 | Response time, concurrency, resource usage |
| 安全测试 | Authentication, authorization, data encryption, injection attacks |

## Preconditions/Steps/Expected Results Format

**CRITICAL: 前置条件 / 测试方法和步骤 / 预期结果 一律不使用换行。**

三个字段统一采用「单行、用中文分号 `；` 分隔」的编号列表格式：
- 编号形式：`1、` `2、` `3、`（中文顿号后接内容）
- 各条之间用中文分号 `；` 分隔
- 整段内容**不包含任何换行符**（不使用 `\n`、`<br/>` 等）
- 预期结果条目与测试方法和步骤的条目一一对应

示例（前置条件）：
```
1、用户已登录系统；2、用户具有管理员权限；3、系统中至少存在一个集群
```

示例（测试方法和步骤）：
```
1、点击左侧导航"DevOps管理"；2、点击"集群管理"；3、点击"添加集群"按钮
```

示例（预期结果，与步骤一一对应）：
```
1、导航菜单高亮正确；2、集群列表页正常加载；3、弹出添加集群对话框且字段完整
```

## Header Statistics Zone (Rows 4~8)

Rows 4~8 replicate the per-round statistics blocks shown in the demo. Each round block
occupies the same 5 columns (V~Y for round 1, Z~AC for round 2, AD~AG for round N):

| Row | Col1 (metric name) | Col2 (value) | Col3 | Col4 (value) |
|-----|--------------------|--------------|------|--------------|
| Row 4 | 用例条数 | <count> | OK | <count> |
| Row 5 | 纳入测试 | <count> | POK | <count> |
| Row 6 | 执行率 | <rate> | NG | <count> |
| Row 7 | 通过率 | <rate> | SKIP | <count> |
| Row 8 | NT | <count> | 队列中 | <count> |

Values may be left blank/0 in generated files; structure must be preserved.

Additionally, Row 7 also contains the 测试标识/产品/系统/设计人员/可用标签 block
in columns D~H (测试标识=TC, 产品=IEnv, 系统=IEnvs, 设计人员=<name>, 可用标签=blank).
Row 8 holds the values for that block: (TC / IEnv / IEnvs / <designer name>).

## Output Format Decision Tree

```
User request format?
├── Markdown → Output core columns (B, D-N, Y) in markdown table
├── Excel (.xls/.xlsx) → Output all 34 columns, generate .xlsx file
└── "导入测试平台" / "import to platform" → Output all 34 columns in Excel format
```

## Markdown Table Example (Core Columns Only)

```markdown
| 序号 | 一级模块 | 二级模块 | 三级模块 | 用例编号 | 优先级 | 分类 | 用例描述 | 前置条件 | 测试方法和步骤 | 预期结果 |
|------|----------|----------|----------|----------|--------|------|----------|----------|---------------|----------|
| 1 | DevOps管理 | 集群管理 | 标签管理 | TC-TAG-001 | 高 | 功能测试 | 验证可通过正确路径进入标签列表页 | 1、用户已登录；2、具有管理员权限 | 1、点击"DevOps管理"；2、展开"集群管理"；3、点击"标签管理" | 1、页面正常加载；2、显示标签列表；3、列表含标签名称、集群数、操作按钮 |
| 2 | DevOps管理 | 集群管理 | 标签管理 | TC-TAG-002 | 高 | 功能测试 | 验证新增标签功能正常 | 1、用户已登录；2、进入标签管理页面 | 1、点击"新增标签"按钮；2、输入标签名称；3、点击"确定" | 1、弹出新增对话框；2、标签名称合法；3、新增成功，列表刷新 |
```
