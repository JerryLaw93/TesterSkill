#!/usr/bin/env python3
"""Generate / extend test cases from a requirements doc into the 34-column xlsx.

Usage:
    python scripts/gen_testcases.py --xlsx testcases/测试用例.xlsx --requirements docs/需求.md
    python scripts/gen_testcases.py --xlsx testcases/测试用例.xlsx --json cases.json
    python scripts/gen_testcases.py --xlsx testcases/测试用例.xlsx --cases TC-LOG-007 TC-USER-005

The "generator" here is deliberately minimal: it accepts a list of case dicts
(either from --json or --cases inline) and appends them. A LLM step (or a
human) is responsible for producing the case dicts, since that requires
understanding the product.

Schema of one case (the fields understood by xlsx_helpers.append_case):

    {
        "cid": "TC-LOGIN-007",      # required, unique
        "module1": "登录模块",        # required
        "module2": "验证码",          # optional
        "module3": "大小写",          # optional
        "priority": "中",             # 高/中/低
        "category": "功能测试",        # 功能/性能/安全/兼容/易用性
        "reviewed": "否",             # 是/否
        "desc": "...",                # required
        "precondition": "1、...",     # optional but recommended
        "steps": "1、...；2、...",     # required, use ；
        "expect": "1、...；2、...",    # required
        "auto": "是",                 # 是/否
        "included": "是"              # 是/否
    }
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

# Allow `from scripts.xlsx_helpers import ...` when run from repo root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.xlsx_helpers import open_xlsx, append_case, append_cases, list_cases  # noqa: E402


def load_json_cases(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(data, list):
        raise SystemExit(f'{path} must contain a JSON list of case dicts')
    return data


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--xlsx', required=True, help='path to 测试用例.xlsx')
    src = ap.add_mutually_exclusive_group()
    src.add_argument('--requirements', help='read requirements doc and produce a draft (LLM-driven; here we just dump structure)')
    src.add_argument('--json', help='path to a JSON list of case dicts')
    src.add_argument('--cases', nargs='*', help='one or more case IDs to keep (filter existing)')
    args = ap.parse_args()

    wb, ws = open_xlsx(args.xlsx)

    if args.cases:
        keep = set(args.cases)
        kept = 0
        for r in range(11, ws.max_row + 1):
            cid = ws.cell(row=r, column=7).value
            if cid in keep:
                kept += 1
        print(f'{kept} matching cases in workbook (no mutation; this is a filter preview)')

    if args.json:
        cases = load_json_cases(Path(args.json))
        last = append_cases(ws, cases)
        wb.save(args.xlsx)
        print(f'appended {len(cases)} cases; last row = {last}')

    if args.requirements:
        # We do not try to "generate from requirements" automatically — that needs
        # the LLM. Instead, dump a checklist the LLM should fill in.
        print(json.dumps({
            'checklist': [
                'Login: success, wrong pwd, captcha refresh, captcha case-sensitivity, lockout',
                'Auth: session restore after reload, logout, token expire, multi-tab',
                'CRUD: create / read / update / delete with boundary values (空, 超长, 重复, 特殊字符)',
                'Permissions: page access per role, button access per role, default-role bootstrap',
                'Errors: network 500, validation messages, dialog cancels',
                'i18n: Chinese punctuation, full-width chars, emoji',
            ],
            'note': 'Have the LLM (or a human) turn each item into a case dict; pass via --json.',
        }, ensure_ascii=False, indent=2))

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
