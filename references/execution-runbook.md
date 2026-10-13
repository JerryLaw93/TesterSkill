# Playwright MCP 执行 Runbook

## 1. 工具集

- `browser_navigate` — 打开 URL
- `browser_snapshot` — 取 DOM 无障碍快照（拿到 ref）
- `browser_evaluate` — 跑一段 JS（同步 / 异步）
- `browser_run_code_unsafe` — 跑一段 Playwright + Node API 的脚本
- `browser_click` / `browser_fill_form` / `browser_type` — 简单交互
- `browser_take_screenshot` — 截图（按 target 元素或全页）
- `browser_handle_dialog` — 处理 alert/confirm/prompt
- `browser_console_messages` — 看 console
- `browser_drag` / `browser_select_option` / `browser_press_key` — 高级交互

## 2. 推荐执行模板

```js
// scripts/exec_xxx.js  (放到 testcases/ 下, 然后用 browser_run_code_unsafe 加载)
async (page) => {
  const OUT = '/abs/path/testcases/execution_results.json';
  const URL = 'http://localhost:8080/index.html';
  const T = 6000;
  const results = [];
  const dialogLog = [];
  let dialogAction = 'accept';
  // 关键：dialog 必须是 async handler
  page.on('dialog', async d => {
    dialogLog.push({ type: d.type(), message: d.message() });
    try { await d[dialogAction](); } catch (e) {}
  });
  // helpers
  const shot = async tag => { await page.screenshot({ path: '/abs/path/testcases/evidence/steps/' + tag + '.jpg', type: 'jpeg', quality: 80 }); return tag; };
  const visible = sel => page.waitForSelector(sel, { state: 'visible', timeout: T });
  const gone    = sel => page.waitForSelector(sel, { state: 'hidden',  timeout: T });
  const click   = sel => page.locator(sel).click();
  const fill    = (sel, v) => page.locator(sel).fill(v);
  const ev      = (fn, ...args) => page.evaluate(fn, ...args);
  const until   = (fn, arg) => page.waitForFunction(fn, arg, { timeout: T });
  const cap     = () => ev(() => window.captchaCode);
  const login = async (u, p, c) => { await fill('#username', u); await fill('#password', p); await fill('#captcha', c); await click('#loginForm button'); };
  // case
  await page.setViewportSize({ width: 1280, height: 900 });
  await page.goto(URL, { waitUntil: 'load' });
  await ev(() => { localStorage.clear(); sessionStorage.clear(); });
  await page.reload({ waitUntil: 'load' });
  await visible('#loginView');
  const cc = await cap();
  await login('admin', '123456', cc);
  await visible('#appView');
  const c = { cid: 'TC-LOG-001', status: 'passed', steps: [] };
  c.steps.push({ idx: 1, status: 'passed', shot: await shot('TC-LOG-001-s1') });
  results.push(c);
  // ... more cases ...
  require('fs').writeFileSync(OUT, JSON.stringify({ summary: { total: results.length, passed: results.filter(r => r.status === 'passed').length }, results }));
}
```

## 3. 截图命名规范

`evidence/steps/<cid>-s<N>.jpg`

- `cid` = 完整用例编号（与 xlsx 第 7 列一致）
- `sN` = 第 N 步，从 s1 起
- 失败用例可加 `fN`：`<cid>-f1.jpg`

## 4. 结果 JSON 格式

```json
{
  "summary": { "total": 63, "passed": 60, "failed": 3, "stepShots": 142 },
  "results": [
    {
      "cid": "TC-LOG-001",
      "status": "passed",
      "module1": "登录模块",
      "priority": "高",
      "expect": "1、登录成功；2、跳转首页；3、显示欢迎语",
      "steps": [
        { "idx": 1, "status": "passed", "shot": "TC-LOG-001-s1" },
        { "idx": 2, "status": "passed", "shot": "TC-LOG-001-s2" }
      ]
    }
  ]
}
```

`status ∈ {passed, failed, skipped, broken}`。

## 5. 常见坑

1. **dialog 句柄没用 async** — `page.on('dialog', d => d.accept())` 在 async runner 里会 hang，**必须** `async d => await d.accept()`。
2. **reload 后 state 还在** — 先 `localStorage.clear(); sessionStorage.clear();` 再 `page.reload`。
3. **验证码过期** — 截图后立即调 `getCaptchaCode()`，不要跨多个 await。
4. **填表单时 locator 拿到多个元素** — 限定到具体 view：`page.locator('#userView #username')`。
5. **截图不显示** — 路径要绝对，目录先 `mkdir -p`。
6. **写文件没生效** — Node 18+ 用 `require('fs')` 不行时，换 `await import('fs')`。
7. **localStorage 大小** — 截图不要 base64 塞进去；用 jpg 文件引用。
