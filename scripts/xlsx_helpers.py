"""Helpers for reading and writing the standard 34-column 测试用例 xlsx.

The template is the import format of 测试管理平台. Column layout (1-indexed):

    1  序号 (case_index, integer)
    2  (空) - auto
    3  (空) - auto
    4  一级模块
    5  二级模块
    6  三级模块
    7  用例编号 (cid, e.g. TC-LOGIN-001)
    8  优先级 (高/中/低)
    9  分类 (功能测试/性能测试/...)
   10  是否已评审 (是/否)
   11  用例描述
   12  前置条件
   13  测试方法和步骤
   14  预期结果
   15  已自动化 (是/否)
   16  实际结果
   17  是否通过
   18  备注
   19  创建人
   20  创建时间
   21  纳入测试 (是/否)
   22-34 预留/可忽略

Counter cell: row 5, column 3 holds the running case count.
First data row: 11.
"""
from __future__ import annotations
from pathlib import Path
from typing import Any, Iterable

from openpyxl import Workbook, load_workbook
from openpyxl.worksheet.worksheet import Worksheet

DEFAULT_SHEET = '测试管理平台—测试用例导入模版'
FIRST_DATA_ROW = 11
COUNTER_CELL = (5, 3)


def open_xlsx(path: str | Path, sheet: str = DEFAULT_SHEET):
    """Load the test-case xlsx and return (wb, ws)."""
    wb = load_workbook(path)
    if sheet not in wb.sheetnames:
        raise ValueError(f'Sheet {sheet!r} not in {path}; found {wb.sheetnames}')
    return wb, wb[sheet]


def new_workbook(path: str | Path):
    """Create a fresh 34-column xlsx with header rows + counter."""
    wb = Workbook()
    ws = wb.active
    ws.title = DEFAULT_SHEET
    ws.cell(row=5, column=3, value=0)
    wb.save(path)
    return open_xlsx(path)


def _row_from_dict(d: dict) -> list:
    """Map a friendly dict to a 21-element row list (cols 1..21)."""
    def g(k, default=''):
        v = d.get(k, default)
        return default if v is None else v
    return [
        g('index', 0),
        '',
        '',
        g('module1'),
        g('module2'),
        g('module3'),
        g('cid'),
        g('priority', '中'),
        g('category', '功能测试'),
        g('reviewed', '否'),
        g('desc'),
        g('precondition', ''),
        g('steps'),
        g('expect'),
        g('auto', '否'),
        g('actual', ''),
        g('passed', ''),
        g('note', ''),
        g('author', ''),
        g('created', ''),
        g('included', '是'),
    ]


def append_case(ws: Worksheet, case: dict) -> int:
    """Append a single case dict to ws, auto-incrementing index. Returns row written."""
    if ws.max_row < FIRST_DATA_ROW - 1:
        row = FIRST_DATA_ROW
    else:
        row = ws.max_row + 1
    if case.get('index') is None:
        prev = ws.cell(row=row - 1, column=1).value or 0
        try:
            case = {**case, 'index': int(prev) + 1}
        except (TypeError, ValueError):
            case = {**case, 'index': row - FIRST_DATA_ROW + 1}
    values = _row_from_dict(case)
    for col, val in enumerate(values, start=1):
        ws.cell(row=row, column=col, value=val)
    total = (ws.cell(row=COUNTER_CELL[0], column=COUNTER_CELL[1]).value or 0) + 1
    ws.cell(row=COUNTER_CELL[0], column=COUNTER_CELL[1], value=total)
    return row


def append_cases(ws: Worksheet, cases: Iterable[dict]) -> int:
    last = 0
    for c in cases:
        last = append_case(ws, c)
    return last


def set_cell(ws: Worksheet, row: int, col: int, value: Any) -> None:
    ws.cell(row=row, column=col, value=value)


def update_counter(ws: Worksheet, delta: int = 1) -> None:
    """Bump the counter cell at (row 5, col 3) by `delta`."""
    r, c = COUNTER_CELL
    cur = ws.cell(row=r, column=c).value or 0
    try:
        cur = int(cur)
    except (TypeError, ValueError):
        cur = 0
    ws.cell(row=r, column=c, value=cur + delta)


def list_cases(ws: Worksheet) -> list[dict]:
    """Return a list of {row, cid, desc, expect, ...} for every data row."""
    out = []
    for r in range(FIRST_DATA_ROW, ws.max_row + 1):
        if ws.cell(row=r, column=7).value is None:
            continue
        out.append({
            'row': r,
            'cid': ws.cell(row=r, column=7).value,
            'module1': ws.cell(row=r, column=4).value,
            'priority': ws.cell(row=r, column=8).value,
            'desc': ws.cell(row=r, column=11).value,
            'precondition': ws.cell(row=r, column=12).value,
            'steps': ws.cell(row=r, column=13).value,
            'expect': ws.cell(row=r, column=14).value,
        })
    return out


if __name__ == '__main__':  # smoke test
    import sys
    if len(sys.argv) < 2:
        print('Usage: xlsx_helpers.py <xlsx>')
        sys.exit(1)
    _, ws = open_xlsx(sys.argv[1])
    print(f'{len(list_cases(ws))} cases')
    for c in list_cases(ws)[:5]:
        print(c['row'], c['cid'], c['desc'])
