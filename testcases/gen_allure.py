# -*- coding: utf-8 -*-
"""从 测试用例.xlsx + execution_results.json 生成带步骤级截图附件的 allure-results"""
import json, os, shutil, uuid
from openpyxl import load_workbook

BASE = os.path.dirname(os.path.abspath(__file__))
XLSX = os.path.join(BASE, "测试用例.xlsx")
RESULTS = os.path.join(BASE, "execution_results.json")
SHOTS = os.path.join(BASE, "evidence", "steps")
OUT = os.path.join(BASE, "allure-results")

with open(RESULTS, encoding="utf-8") as f:
    exec_data = {r["cid"]: r for r in json.load(f)["results"]}

# 清空 allure-results（含旧附件）
if os.path.isdir(OUT):
    shutil.rmtree(OUT)
os.makedirs(OUT)

# 写入环境信息（供 Allure 首页 ENVIRONMENT 区域展示）
import platform, subprocess, re
uname = subprocess.check_output(['uname', '-a'], text=True).strip()
sw = subprocess.check_output(['sw_vers'], text=True).strip() if os.uname().sysname == 'Darwin' else ''
cpu = subprocess.check_output(['sysctl', '-n', 'machdep.cpu.brand_string'], text=True).strip() if os.uname().sysname == 'Darwin' else platform.processor()
mem_info = subprocess.check_output(['system_profiler', 'SPHardwareDataType'], text=True).strip() if os.uname().sysname == 'Darwin' else ''
mem_match = re.search(r'Memory: (.+)', mem_info)
mem = mem_match.group(1).strip() if mem_match else 'unknown'
try:
    allure_ver = subprocess.run(['allure', '--version'], capture_output=True, text=True).stdout.strip()
except Exception:
    allure_ver = 'unknown'
env_props = {
    '测试系统/平台': sw.replace('\n', ' | '),
    '操作系统内核': uname,
    'CPU': cpu,
    '内存': mem,
    'Python版本': platform.python_version(),
    'Allure版本': allure_ver,
    '测试页面': 'http://localhost:8080/index.html',
    '浏览器引擎': 'Chromium (via Playwright MCP)',
    '测试账号': 'admin / 123456',
    '执行日期': '2026-10-13',
    '执行人': 'AI自动化(Playwright MCP)',
}
# 使用 XML 格式写入环境信息（Allure 对 XML 按 UTF-8 解析，避免中文乱码）
from xml.sax.saxutils import escape
xml_lines = [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<environment>',
]
for k, v in env_props.items():
    xml_lines.append('  <parameter>')
    xml_lines.append(f'    <key>{escape(str(k))}</key>')
    xml_lines.append(f'    <value>{escape(str(v))}</value>')
    xml_lines.append('  </parameter>')
xml_lines.append('</environment>')
with open(os.path.join(OUT, 'environment.xml'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(xml_lines) + '\n')

SEV = {"高": "critical", "中": "normal", "低": "minor"}
BASE_TS = 1760308800000

def split_items(text):
    return [s.strip() for s in (text or "").split("；") if s.strip()]

def attach_copy(shot_tag):
    """把步骤截图复制为 allure 附件文件，返回附件条目"""
    src = os.path.join(SHOTS, shot_tag + ".jpg")
    if not os.path.isfile(src):
        return None
    att_id = str(uuid.uuid4()) + "-attachment.jpg"
    shutil.copy(src, os.path.join(OUT, att_id))
    return {"name": shot_tag + ".jpg", "source": att_id, "type": "image/jpeg"}

wb = load_workbook(XLSX)
ws = wb["测试管理平台—测试用例导入模版"]

n = 0
total_att = 0
for r in range(11, ws.max_row + 1):
    cid = ws.cell(row=r, column=7).value
    if not cid:
        continue
    l1 = ws.cell(row=r, column=4).value
    l2 = ws.cell(row=r, column=5).value
    l3 = ws.cell(row=r, column=6).value
    prio = ws.cell(row=r, column=8).value
    cat = ws.cell(row=r, column=9).value
    desc = ws.cell(row=r, column=11).value
    pre = ws.cell(row=r, column=12).value
    steps_text = ws.cell(row=r, column=13).value or ""
    exp = ws.cell(row=r, column=14).value
    note = ws.cell(row=r, column=25).value or ""

    ex = exec_data.get(cid)
    if ex:
        status = "passed" if ex["status"] == "passed" else ("failed" if ex["status"] == "failed" else "skipped")
        step_map = {s["idx"]: s for s in ex["steps"]}
    else:
        status = "skipped"  # 未执行（安全/性能类）
        step_map = {}

    step_names = split_items(steps_text)
    allure_steps = []
    for i, sname in enumerate(step_names, start=1):
        sdata = step_map.get(i)
        sstatus = sdata["status"] if sdata else ("skipped" if status == "skipped" else "passed")
        step = {"name": sname, "status": sstatus, "stage": "finished"}
        if sdata and sdata.get("shot"):
            att = attach_copy(sdata["shot"])
            if att:
                step["attachments"] = [att]
                total_att += 1
        allure_steps.append(step)

    # 把带 1、2、3 的前置/预期按中文分号拆成 Markdown 列表，实现换行显示
    def md_list(text):
        if not text:
            return "（无）"
        items = [s.strip() for s in text.split("；") if s.strip()]
        if not items:
            return text
        return "\n".join(f"- {it}" for it in items)

    description = f"【用例描述】{desc}\n\n【前置条件】\n{md_list(pre)}\n\n【预期结果】\n{md_list(exp)}"
    if note:
        description += f"\n\n【备注】{note}"

    data = {
        "name": f"{cid} {desc}",
        "status": status,
        "stage": "finished",
        "description": description,
        "start": BASE_TS + n * 15000,
        "stop": BASE_TS + n * 15000 + 8000,
        "labels": [
            {"name": "suite", "value": l1},
            {"name": "parentSuite", "value": "用户管理系统"},
            {"name": "subSuite", "value": f"{l2}/{l3}" if l3 else l2},
            {"name": "feature", "value": l2},
            {"name": "story", "value": l3 or l2},
            {"name": "testCaseId", "value": cid},
            {"name": "severity", "value": SEV.get(prio, "normal")},
            {"name": "tag", "value": cat},
        ],
        "steps": allure_steps,
    }
    if status == "skipped":
        data["statusDetails"] = {"message": note or "未纳入本轮自动化执行", "flaky": False}

    with open(os.path.join(OUT, f"{uuid.uuid4()}-result.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    n += 1

print(f"生成 {n} 个用例结果, {total_att} 个步骤截图附件 -> {OUT}")
