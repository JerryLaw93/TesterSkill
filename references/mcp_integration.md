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
