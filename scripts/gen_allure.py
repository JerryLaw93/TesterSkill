#!/usr/bin/env python3
"""Generate a self-contained Allure-style HTML report from execution_results.json.

No Java / no Allure CLI required. Produces a static `allure-report/` directory
that can be served by any HTTP server (or opened via file:// in some browsers).

Usage:
    python scripts/gen_allure.py \
        --results testcases/execution_results.json \
        --out testcases/allure-report

Output layout:
    <out>/
    ├── index.html
    ├── data/{suites.json, test-cases/<uuid>.json, categories.json}
    ├── widgets/{summary.json, suites.json, categories.json, timeline.json, history.json}
    ├── history/history.json
    └── export/prometheus.txt
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

# --------------------------- HTML template -------------------------------- #

INDEX_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<title>Allure Report</title>
<style>
  :root { --bg:#0f1115; --card:#171a21; --text:#e6e8ec; --muted:#8b95a3; --ok:#22c55e; --fail:#ef4444; --skip:#eab308; --acc:#60a5fa; }
  * { box-sizing: border-box; }
  body { margin:0; font-family:-apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif; background:var(--bg); color:var(--text); }
  header { padding:20px 28px; background:#0a0c10; border-bottom:1px solid #232733; display:flex; align-items:center; gap:18px; }
  header h1 { margin:0; font-size:20px; font-weight:600; }
  .env { display:flex; gap:14px; flex-wrap:wrap; margin-left:auto; font-size:13px; color:var(--muted); }
  .env b { color:var(--text); margin-right:6px; }
  .grid { padding:20px 28px; display:grid; grid-template-columns:repeat(4,1fr); gap:14px; }
  .card { background:var(--card); padding:16px 18px; border-radius:10px; border:1px solid #232733; }
  .card .k { color:var(--muted); font-size:12px; text-transform:uppercase; letter-spacing:.5px; }
  .card .v { font-size:28px; font-weight:700; margin-top:6px; }
  .card.ok .v { color:var(--ok); } .card.fail .v { color:var(--fail); } .card.skip .v { color:var(--skip); } .card.dur .v { color:var(--acc); }
  .main { padding:0 28px 28px; display:grid; grid-template-columns: 280px 1fr; gap:18px; }
  .side { background:var(--card); border-radius:10px; border:1px solid #232733; padding:14px; }
  .side h3 { margin:6px 8px 10px; font-size:14px; color:var(--muted); text-transform:uppercase; letter-spacing:.5px; }
  .side .it { padding:8px 10px; border-radius:6px; cursor:pointer; font-size:13px; display:flex; justify-content:space-between; }
  .side .it:hover { background:#1f2330; }
  .side .it.active { background:#1f2330; border:1px solid var(--acc); }
  .side .it .badge { font-size:11px; padding:2px 8px; border-radius:10px; }
  .badge.passed { background:rgba(34,197,94,.15); color:var(--ok); }
  .badge.failed { background:rgba(239,68,68,.15); color:var(--fail); }
  .badge.skipped { background:rgba(234,179,8,.15); color:var(--skip); }
  .content { background:var(--card); border-radius:10px; border:1px solid #232733; padding:18px 22px; min-height:60vh; }
  .content h2 { margin:0 0 6px; font-size:20px; }
  .content .meta { color:var(--muted); font-size:13px; margin-bottom:14px; }
  .pill { display:inline-block; padding:3px 10px; border-radius:12px; font-size:12px; margin-right:6px; }
  .pill.ok { background:rgba(34,197,94,.15); color:var(--ok); }
  .pill.fail { background:rgba(239,68,68,.15); color:var(--fail); }
  .pill.skip { background:rgba(234,179,8,.15); color:var(--skip); }
  .section { margin-top:18px; }
  .section h4 { margin:0 0 8px; color:var(--muted); font-size:13px; text-transform:uppercase; letter-spacing:.5px; }
  .pre { white-space:pre-wrap; background:#0d0f14; border:1px solid #232733; border-radius:8px; padding:12px 14px; font-size:13px; line-height:1.6; }
  .shot { margin:8px 0; }
  .shot img { max-width:100%; border-radius:6px; border:1px solid #232733; }
  .shot .lbl { color:var(--muted); font-size:12px; margin-bottom:4px; }
  .empty { color:var(--muted); padding:30px; text-align:center; }
</style>
</head>
<body>
<header>
  <h1>Allure Report — __TITLE__</h1>
  <div class="env">
    <div><b>开始时间</b> __START__</div>
    <div><b>耗时</b> __DUR__ s</div>
    <div><b>环境</b> __ENV__</div>
  </div>
</header>
<div class="grid">
  <div class="card"><div class="k">用例总数</div><div class="v">__TOTAL__</div></div>
  <div class="card ok"><div class="k">通过</div><div class="v">__PASSED__</div></div>
  <div class="card fail"><div class="k">失败</div><div class="v">__FAILED__</div></div>
  <div class="card skip"><div class="k">跳过</div><div class="v">__SKIPPED__</div></div>
</div>
<div class="main">
  <div class="side">
    <h3>用例列表</h3>
    <div id="list"></div>
  </div>
  <div class="content" id="content">
    <div class="empty">请从左侧选择一条用例</div>
  </div>
</div>
<script>
const DATA = __DATA__;
const list = document.getElementById('list');
const content = document.getElementById('content');
function esc(s) { return (s || '').toString().replace(/[&<>]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;'}[c])); }
function pick(c) {
  document.querySelectorAll('.side .it').forEach(el => el.classList.remove('active'));
  event && event.currentTarget && event.currentTarget.classList.add('active');
  const stepsHtml = (c.steps_result || []).map(s => {
    const ok = s.status === 'passed';
    const lbl = s.shot ? `<div class="lbl">第 ${s.idx} 步 — ${s.status}${ok?'':'（失败）'}</div><img src="evidence/steps/${s.shot}.jpg">` : `<div class="lbl">第 ${s.idx} 步 — ${s.status}</div>`;
    return `<div class="shot">${lbl}</div>`;
  }).join('');
  const stepText = (c.steps || '').split(/[；;]/).map(x => x.trim()).filter(Boolean).map((x, i) => `<div>${i+1}、 ${esc(x)}</div>`).join('');
  const expectText = (c.expect || '').split(/[；;]/).map(x => x.trim()).filter(Boolean).map((x, i) => `<div>${i+1}、 ${esc(x)}</div>`).join('');
  content.innerHTML = `
    <h2>${esc(c.cid)} · ${esc(c.desc || '')}</h2>
    <div class="meta">${esc(c.module1||'')} / ${esc(c.module2||'')} · 优先级 ${esc(c.priority||'')}</div>
    <span class="pill ${c.status}">${esc(c.status)}</span>
    <div class="section"><h4>前置条件</h4><div class="pre">${esc(c.precondition || '—')}</div></div>
    <div class="section"><h4>测试步骤</h4><div class="pre">${stepText || '—'}</div></div>
    <div class="section"><h4>预期结果</h4><div class="pre">${expectText || '—'}</div></div>
    ${c.actual ? `<div class="section"><h4>实际结果</h4><div class="pre">${esc(c.actual)}</div></div>` : ''}
    <div class="section"><h4>执行截图</h4>${stepsHtml || '<div class="pre">—</div>'}</div>
  `;
}
DATA.forEach((c, i) => {
  const div = document.createElement('div');
  div.className = 'it';
  div.innerHTML = `<span>${i+1}. ${esc(c.cid)}</span><span class="badge ${c.status}">${esc(c.status)}</span>`;
  div.onclick = () => pick(c);
  list.appendChild(div);
});
if (DATA.length) pick(DATA[0]);
</script>
</body>
</html>
"""


# --------------------------- helpers -------------------------------------- #

def _case_to_record(c: dict[str, Any]) -> dict[str, Any]:
    """Normalize one result into a display record."""
    return {
        'cid': c.get('cid', ''),
        'desc': c.get('desc', ''),
        'module1': c.get('module1', ''),
        'module2': c.get('module2', ''),
        'priority': c.get('priority', ''),
        'status': c.get('status', 'unknown'),
        'precondition': c.get('precondition', ''),
        'steps': c.get('steps', ''),
        'expect': c.get('expect', ''),
        'actual': c.get('actual', ''),
        'note': c.get('note', ''),
        'steps_result': c.get('steps_result') or c.get('steps') or [],
    }


# --------------------------- main ----------------------------------------- #

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--results', required=True, help='execution_results.json path')
    ap.add_argument('--out', required=True, help='output directory (will be created/overwritten)')
    ap.add_argument('--title', default='Web 测试报告', help='report title')
    ap.add_argument('--env', default='Local / Chromium', help='environment string for header')
    args = ap.parse_args()

    results_path = Path(args.results)
    out_dir = Path(args.out)
    if not results_path.exists():
        print(f'results not found: {results_path}', file=sys.stderr)
        return 1
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)
    (out_dir / 'data' / 'test-cases').mkdir(parents=True)
    (out_dir / 'widgets').mkdir(parents=True)
    (out_dir / 'history').mkdir(parents=True)
    (out_dir / 'export').mkdir(parents=True)

    raw = json.loads(results_path.read_text(encoding='utf-8'))
    results = raw.get('results') or raw.get('cases') or []
    summary = raw.get('summary') or {}
    passed = sum(1 for c in results if c.get('status') == 'passed')
    failed = sum(1 for c in results if c.get('status') == 'failed')
    skipped = sum(1 for c in results if c.get('status') in ('skipped', 'broken'))
    total = len(results) or summary.get('total', 0)

    display = [_case_to_record(c) for c in results]
    start_ts = datetime.now().replace(microsecond=0).isoformat(sep=' ')

    # index.html
    html = (INDEX_HTML
            .replace('__TITLE__', args.title)
            .replace('__START__', start_ts)
            .replace('__DUR__', '—')
            .replace('__ENV__', args.env)
            .replace('__TOTAL__', str(total))
            .replace('__PASSED__', str(passed))
            .replace('__FAILED__', str(failed))
            .replace('__SKIPPED__', str(skipped))
            .replace('__DATA__', json.dumps(display, ensure_ascii=False)))
    (out_dir / 'index.html').write_text(html, encoding='utf-8')

    # data/suites.json
    suites_root = {
        'uid': 'root',
        'name': args.title,
        'children': [],
        'time': {'start': 0, 'stop': 0, 'duration': 0},
    }
    test_case_files = []
    for c in results:
        uid = str(uuid.uuid4())
        suite = {
            'uid': f'{uid}#suite',
            'name': c.get('module1') or '未分类',
            'children': [uid],
            'time': {'start': 0, 'stop': 0, 'duration': 0},
        }
        suites_root['children'].append(suite)
        tc = {
            'uid': uid,
            'name': f"{c.get('cid','')} {c.get('desc','')}".strip(),
            'fullName': c.get('cid', ''),
            'status': c.get('status', 'unknown'),
            'statusDetails': {},
            'time': {'start': 0, 'stop': 0, 'duration': 0},
            'description': '\n'.join(filter(None, [
                c.get('precondition') and f'前置条件：\n{c["precondition"]}',
                c.get('steps') and f'测试步骤：\n{c["steps"]}',
                c.get('expect') and f'预期结果：\n{c["expect"]}',
                c.get('actual') and f'实际结果：\n{c["actual"]}',
                c.get('note') and f'备注：\n{c["note"]}',
            ])),
            'labels': [
                {'name': 'feature', 'value': c.get('module1') or '未分类'},
                {'name': 'story', 'value': c.get('module2') or ''},
                {'name': 'severity', 'value': c.get('priority') or 'normal'},
            ],
            'steps': [],
            'attachments': [
                {'name': s.get('shot', f's{i}'),
                 'source': f'evidence/steps/{s.get("shot", f"s{i}")}.jpg',
                 'type': 'image/jpeg'}
                for i, s in enumerate(c.get('steps_result') or [])
                if s.get('shot')
            ],
        }
        (out_dir / 'data' / 'test-cases' / f'{uid}.json').write_text(
            json.dumps(tc, ensure_ascii=False), encoding='utf-8')
        test_case_files.append(uid)
    (out_dir / 'data' / 'suites.json').write_text(
        json.dumps({'suites': [suites_root]}, ensure_ascii=False), encoding='utf-8')

    # data/categories.json
    (out_dir / 'data' / 'categories.json').write_text(
        json.dumps({'categories': []}, ensure_ascii=False), encoding='utf-8')

    # widgets
    widgets_dir = out_dir / 'widgets'
    (widgets_dir / 'summary.json').write_text(json.dumps({
        'statistic': {'failed': failed, 'broken': 0, 'skipped': skipped, 'passed': passed, 'unknown': 0, 'total': total},
        'time': {'start': 0, 'stop': 0, 'duration': 0},
    }), encoding='utf-8')
    (widgets_dir / 'suites.json').write_text(json.dumps({
        'children': [{
            'uid': 'root', 'name': args.title,
            'children': [{'uid': c.get('cid'), 'name': c.get('cid'), 'status': c.get('status')} for c in results],
        }],
    }, ensure_ascii=False), encoding='utf-8')
    (widgets_dir / 'categories.json').write_text(json.dumps({'children': []}), encoding='utf-8')
    (widgets_dir / 'timeline.json').write_text(json.dumps({
        'children': [{'uid': c.get('cid'), 'title': c.get('cid'), 'status': c.get('status')} for c in results],
    }, ensure_ascii=False), encoding='utf-8')
    (widgets_dir / 'history.json').write_text(json.dumps({'children': []}), encoding='utf-8')

    # history
    (out_dir / 'history' / 'history.json').write_text(json.dumps([{
        'statistic': {'failed': failed, 'broken': 0, 'skipped': skipped, 'passed': passed, 'unknown': 0, 'total': total},
        'items': [{'reportName': args.title, 'statistic': {'failed': failed, 'broken': 0, 'skipped': skipped, 'passed': passed, 'unknown': 0, 'total': total}}],
    }]), encoding='utf-8')

    # export
    (out_dir / 'export' / 'prometheus.txt').write_text(
        f'# HELP allure_report_status Cases by status\n'
        f'# TYPE allure_report_status gauge\n'
        f'allure_report_status{{status="passed"}} {passed}\n'
        f'allure_report_status{{status="failed"}} {failed}\n'
        f'allure_report_status{{status="skipped"}} {skipped}\n',
        encoding='utf-8')

    print(f'Report generated at {out_dir}/index.html')
    print(f'  total={total} passed={passed} failed={failed} skipped={skipped}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
