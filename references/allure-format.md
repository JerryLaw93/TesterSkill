# Allure 报告格式约定

`scripts/gen_allure.py` 不需要 Java 也不需要 Allure CLI，纯 Python 生成 self-contained 的 `allure-report/` 目录。

## 输入

`execution_results.json` 形状：

```json
{
  "summary": { "total": 63, "passed": 60, "failed": 3, "stepShots": 142 },
  "results": [
    {
      "cid": "TC-LOG-001",
      "status": "passed",                       // passed | failed | skipped | broken
      "module1": "登录模块",                      // 一级分类（feature）
      "module2": "验证码",                        // 二级分类（story）
      "priority": "高",                           // severity
      "desc": "登录成功跳转到系统首页",             // title
      "precondition": "1、打开登录页",
      "steps": "1、...；2、...",                   // 步骤文本
      "expect": "1、...；2、...",                   // 预期
      "actual": "...",                            // 可选
      "note": "...",                              // 可选
      "steps_result": [                          // 每步结果
        { "idx": 1, "status": "passed", "shot": "TC-LOG-001-s1" },
        { "idx": 2, "status": "passed", "shot": "TC-LOG-001-s2" }
      ]
    }
  ]
}
```

## 输出

```
allure-report/
├── index.html
├── data/
│   ├── suites.json
│   ├── test-cases/<uuid>.json
│   └── categories.json
├── widgets/
│   ├── summary.json
│   ├── suites.json
│   ├── categories.json
│   ├── timeline.json
│   └── history.json
├── history/
│   └── history.json
└── export/
    └── prometheus.txt
```

`evidence/steps/<cid>-sN.jpg` 通过 `<img src="evidence/steps/<cid>-sN.jpg">` 引用。

## 启动服务

```bash
bash scripts/allure_serve.sh testcases/allure-report 8080
# http://localhost:8080/allure-report/index.html
```

## 自定义字段

如需扩展（`owner`、`epic`、`tag`），在 `results[]` 加字段，并在 `gen_allure.py` 的 `case_to_testcase()` 里映射到 `labels[]`。
