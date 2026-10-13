# MCP Integration Reference (MCP 集成参考)

This document describes how the software-tester skill integrates with the configured MCP
servers to enhance automated testing capabilities.

## MCP Server Overview

| Server | Purpose | Tool Count |
|--------|---------|------------|
| `captcha` | 验证码识别 (CAPTCHA recognition) | 2 |
| `playwright` | 浏览器自动化 (Browser automation) | 24 |

Both servers are user-configured and must be enabled in the IDE before the skill can use them.

---

## MCP Configuration (MCP 配置方式)

### 配置文件位置

MCP 服务器通过 `mcp.json` 配置文件注册，常见位置：

- **IDE 全局配置**：`C:\Users\<用户名>\AppData\Roaming\Lingma\SharedClientCache\mcp.json`
- 也可在 IDE 的 MCP 设置界面中可视化配置（添加服务器 → 填写命令与参数）。

### 配置示例

以下是本 skill 依赖的两个 MCP 服务器的完整配置：

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": [
        "@playwright/mcp@0.0.31"
      ],
      "env": {
        "PLAYWRIGHT_BROWSER_PATH": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
      }
    },
    "captcha": {
      "command": "python",
      "args": [
        "D:/study/MCP/catpcha_mcp.py"
      ]
    }
  }
}
```

### 字段说明

| 字段 | 说明 |
|------|------|
| `command` | 启动 MCP 服务器的可执行命令（`npx` / `python` / `node` 等） |
| `args` | 传给命令的参数（如 npm 包名、脚本路径） |
| `env` | 可选，服务器运行所需的环境变量 |

### 关于 PLAYWRIGHT_BROWSER_PATH 的说明

`PLAYWRIGHT_BROWSER_PATH` 是 **Playwright 官方标准环境变量**（不是 @playwright/mcp 自定义的），用于指定浏览器可执行文件的路径。

**它是什么：**
- 它是 Playwright 框架本身支持的环境变量，用于覆盖默认的浏览器查找逻辑。
- 在 `mcp.json` 的 `env` 字段中配置后，仅对该 MCP 服务器进程生效，**不需要**在 Windows 系统环境变量中单独设置。

**为什么需要它：**
- 默认情况下，Playwright 会下载并使用自己内置的 Chromium 浏览器内核（体积较大，且国内网络下载可能较慢）。
- 设置该变量指向本机已安装的浏览器（如 Chrome），可以**复用现有浏览器，避免下载浏览器内核**。

**如何操作（Windows）：**

1. **找到本机浏览器可执行文件路径**，常见位置：
   - Chrome：`C:\Program Files\Google\Chrome\Application\chrome.exe`
   - Edge：`C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe`
   - 也可在浏览器地址栏输入 `chrome://version`（Chrome）或 `edge://version`（Edge）查看「可执行文件路径」。
2. **在 `mcp.json` 的 `env` 字段中填入该路径**（注意 JSON 中反斜杠需写为 `\\`）：
   ```json
   "env": {
     "PLAYWRIGHT_BROWSER_PATH": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
   }
   ```
3. **保存并重连**：保存 `mcp.json` 后，在 IDE 中刷新/重连 MCP 服务器使配置生效。

**不设置会怎样：**
- 不设置该变量也可以正常使用，Playwright 会自动下载内置浏览器内核（首次使用需等待下载）。
- 如果本机已有 Chrome/Edge，建议设置以加快启动速度并复用浏览器配置。

> **注意**：如果不想用环境变量，也可以改用 `--executable-path <path>` 命令行参数（`@playwright/mcp` 支持），效果相同。

### 配置步骤

1. **playwright（浏览器自动化）**：
   - 需要 Node.js 环境（`npx` 可用）。
   - 首次使用执行 `npx @playwright/mcp@0.0.31` 会自动下载依赖。
   - 可选：通过 `env.PLAYWRIGHT_BROWSER_PATH` 指定本机浏览器路径（如 Chrome），避免下载浏览器内核。
2. **captcha（验证码识别）**：
   - 需要 Python 环境，并安装依赖：`pip install fastmcp ddddocr`。
   - `args` 指向验证码识别脚本路径（如 `D:/study/MCP/catpcha_mcp.py`）。
3. **启用验证**：
   - 保存 `mcp.json` 后，在 IDE 中刷新/重连 MCP 服务器。
   - 确认两个服务器状态为「已连接」，工具列表中出现 `recognize_captcha`、`browser_navigate` 等工具。

> **注意**：不同机器上路径可能不同，请根据实际环境修改 `args` 和 `env` 中的路径。

---

## 1. captcha — 验证码识别

### Tools

#### recognize_captcha

- **Description**: Recognize CAPTCHA text from a local image file.
- **Parameters**:
  - `image_path` (string, required): Absolute path to the CAPTCHA image file.
- **Returns**: Recognized CAPTCHA text (string).
- **Example**:
  ```
  recognize_captcha(image_path="C:/temp/captcha.png")
  → "8x4K"
  ```

#### recognize_captcha_base64

- **Description**: Recognize CAPTCHA text from base64-encoded image bytes.
- **Parameters**:
  - `image_bytes` (string, required): Base64-encoded image bytes.
- **Returns**: Recognized CAPTCHA text (string).
- **Example**:
  ```
  recognize_captcha_base64(image_bytes="iVBORw0KGgoAAAANSUhEUg...")
  → "3f7Q"
  ```

### Usage Scenarios

1. **Login flow with CAPTCHA**:
   - Use `playwright` to navigate to the login page.
   - Locate the CAPTCHA image element; either download it to a local file or capture
     its base64 data from the network/attribute.
   - Call `recognize_captcha` or `recognize_captcha_base64` to get the code.
   - Fill the code into the input field and submit.

2. **Form submission with verification code**:
   - Same flow as above for any form that requires an image verification code.

3. **Retry strategy**:
   - If recognition fails (login rejected), refresh the CAPTCHA image and retry.
   - Some CAPTCHAs are case-sensitive; try both cases if needed.

---

## 2. playwright — 浏览器自动化

### Key Tools Reference

| Tool | Description | Typical Use |
|------|-------------|-------------|
| `browser_navigate` | Navigate to a URL | Open the system under test |
| `browser_click` | Click an element | Click buttons/menus/links |
| `browser_type` | Type text into an input | Fill forms, search boxes |
| `browser_select_option` | Select an option from a dropdown | Choose dropdown values |
| `browser_snapshot` | Get accessibility snapshot of the page | **Verify page state (use for actions)** |
| `browser_take_screenshot` | Capture a screenshot | **Collect visual evidence (not for actions)** |
| `browser_network_requests` | Inspect network requests/responses | Verify API calls and responses |
| `browser_console_messages` | Get console messages | Detect JS errors/warnings |
| `browser_handle_dialog` | Handle alert/confirm/prompt | Deal with JS dialogs |
| `browser_file_upload` | Upload a file | Test file upload features |
| `browser_wait_for` | Wait for a condition | Wait for page load/element |
| `browser_press_key` | Press a keyboard key | Enter/Escape/Tab etc. |
| `browser_hover` | Hover over an element | Trigger hover menus/tooltips |
| `browser_drag` | Drag an element | Test drag-and-drop |
| `browser_resize` | Resize the browser window | Responsive/UI testing |
| `browser_tab_new` | Open a new tab | Multi-tab scenarios |
| `browser_tab_select` | Switch to a tab | Multi-tab scenarios |
| `browser_tab_close` | Close a tab | Multi-tab scenarios |
| `browser_tab_list` | List open tabs | Multi-tab scenarios |
| `browser_navigate_back` | Go back | Navigation testing |
| `browser_navigate_forward` | Go forward | Navigation testing |
| `browser_install` | Install browser | First-time setup |
| `browser_close` | Close the browser | Cleanup |
| `browser_evaluate` | Run JS in the page | Advanced verification |

### Usage Scenarios

1. **Execute UI test steps**:
   - Translate each step of a test case into playwright actions
     (`browser_navigate` → `browser_click` → `browser_type` → ...).
   - Verify expected results using `browser_snapshot` (check element presence, text content).

2. **Collect test evidence**:
   - After each key step, call `browser_take_screenshot` and save the image as evidence.

3. **Interface verification**:
   - Use `browser_network_requests` to inspect the request/response of API calls made by
     the page, and compare against expected results in the test case.

4. **Front-end error detection**:
   - Use `browser_console_messages` to check for JavaScript errors after each action.

5. **Handle dialogs**:
   - Use `browser_handle_dialog` to accept/dismiss alert, confirm, and prompt dialogs.

6. **File upload testing**:
   - Use `browser_file_upload` to attach files to upload controls.

---

## Combined Workflow Example: Login with CAPTCHA

```
1. browser_navigate(url="https://example.com/login")
2. browser_snapshot()                          # locate username/password/captcha fields
3. browser_type(...)                           # enter username
4. browser_type(...)                           # enter password
5. browser_take_screenshot(...)                # capture captcha image
6. recognize_captcha(image_path="...")         # OCR the captcha
7. browser_type(...)                           # enter the recognized captcha code
8. browser_click(...)                          # click login button
9. browser_snapshot()                          # verify login success
10. browser_network_requests()                 # verify login API response
11. browser_take_screenshot(...)               # save login success evidence
```

---

## Notes

- MCP servers must be configured and enabled in the IDE environment before use.
- If a tool is unavailable, fall back to manual steps and note it in the test report.
- Screenshots should be saved with meaningful names, e.g., `evidence/TC-LOG-001_step3.png`.

---

## Automated Test Execution (自动执行用例)

> **IMPORTANT — 默认不执行**: 生成用例后**不会自动执行**。只有用户明确说「执行用例」等指令时才执行。
> 执行前必须确认用户提供的**用例文件路径**（`.xlsx`），未提供则先询问，不自行猜测。

After the test case table is generated, the skill **can** automatically execute the cases using
`playwright` + `captcha` **only when the user explicitly requests execution**. See `execution_workflow.md` for the full workflow.

### Execution Checklist

1. **确认用户明确要求执行**（说「执行用例」等指令）。
2. **确认用例文件路径**：用户提供 `.xlsx` 路径；未提供则询问。
3. Confirm the SUT URL and login credentials with the user.
4. Ensure `playwright` and `captcha` MCP servers are enabled.
5. Read the `.xlsx` test case table and extract executable cases.
6. Execute each case with playwright actions; use captcha for verification codes.
7. Save screenshots as evidence under `evidence/`.
8. Backfill results (OK/NG/SKIP/AMBIGUOUS) into the `.xlsx` table (V~Y columns).
9. Generate an execution report.

### Result Mapping

| Execution result | 测试结果 (V column) | Meaning |
|------------------|--------------------|---------|
| PASS | OK | All steps and expected results verified |
| FAIL | NG | A step failed or an expected result was not met |
| SKIP | SKIP | Not executable (性能/安全测试, missing prerequisites) |
| AMBIGUOUS | AMBIGUOUS | 步骤/预期结果不明确，无法客观判断，需人工确认 |

### Best Practices

- Always take a screenshot before and after each critical step.
- If CAPTCHA recognition fails, refresh and retry (max 3 attempts).
- Verify expected results with `browser_snapshot`, not screenshots.
- Use `browser_network_requests` to verify API-level expected results.
- Mark complex/unreliable cases as SKIP for manual testing.
- **不猜测执行**: 遇到模糊/不确定的步骤或预期结果，标记 AMBIGUOUS 并列出待确认问题。
