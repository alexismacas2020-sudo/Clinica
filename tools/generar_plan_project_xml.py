from __future__ import annotations

import re
from datetime import datetime, timedelta
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, ElementTree, register_namespace

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tools" / "generar_plan_project.ps1"
OUT = ROOT / "output" / "Plan_Maestro_Clinica_Reina_del_Cisne.xml"
NS = "http://schemas.microsoft.com/project"
register_namespace("", NS)


def q(name: str) -> str:
    return f"{{{NS}}}{name}"


def add(parent, name, value):
    node = SubElement(parent, q(name))
    node.text = str(value)
    return node


def parse_list(raw: str) -> list[str]:
    return re.findall(r"'([^']+)'", raw)


phase_re = re.compile(r"Add-Phase\s+'([^']+)'\s+'([^']+)'")
task_re = re.compile(
    r"Add-PlanTask\s+'([^']+)'\s+'([^']+)'\s+'([^']+)'\s+"
    r"(@\([^\)]*\))\s+(\d+)\s+(@\([^\)]*\))"
)

items = []
for line in SOURCE.read_text(encoding="utf-8").splitlines():
    match = phase_re.search(line)
    if match:
        items.append({"kind": "phase", "code": match.group(1), "name": match.group(2)})
        continue
    match = task_re.search(line)
    if match:
        duration = int(match.group(3).removesuffix("d"))
        items.append(
            {
                "kind": "task",
                "code": match.group(1),
                "name": match.group(2),
                "duration": duration,
                "owners": parse_list(match.group(4)),
                "percent": int(match.group(5)),
                "pred_codes": parse_list(match.group(6)),
            }
        )

if len(items) < 70:
    raise RuntimeError(f"Se esperaban al menos 70 filas y solo se encontraron {len(items)}")

for uid, item in enumerate(items, 1):
    item["uid"] = uid
    item["id"] = uid

code_map = {item["code"]: item for item in items}
project_start = datetime(2026, 7, 1, 8, 0, 0)


def next_work_start(value: datetime) -> datetime:
    value = value.replace(hour=8, minute=0, second=0, microsecond=0)
    while value.weekday() >= 5:
        value += timedelta(days=1)
    return value


def add_workdays(start: datetime, days: int) -> datetime:
    if days == 0:
        return start
    current = start
    remaining = days
    while remaining:
        if current.weekday() < 5:
            remaining -= 1
            if remaining == 0:
                return current.replace(hour=17)
        current = (current + timedelta(days=1)).replace(hour=8)
    return current


last_finish = project_start
for item in items:
    if item["kind"] == "phase":
        continue
    predecessors = [code_map[c] for c in item["pred_codes"] if c in code_map]
    if predecessors:
        candidate = max(pred["finish"] for pred in predecessors)
        start = next_work_start(candidate + timedelta(days=1))
    else:
        start = next_work_start(last_finish)
    finish = add_workdays(start, item["duration"])
    item["start"], item["finish"] = start, finish
    last_finish = max(last_finish, finish)

for index, item in enumerate(items):
    if item["kind"] != "phase":
        continue
    children = []
    for later in items[index + 1 :]:
        if later["kind"] == "phase":
            break
        children.append(later)
    item["children"] = children
    item["start"] = min((c["start"] for c in children), default=project_start)
    item["finish"] = max((c["finish"] for c in children), default=project_start)
    item["percent"] = round(sum(c["percent"] for c in children) / len(children)) if children else 0
    item["duration"] = 0

project_finish = max(item["finish"] for item in items)

project = Element(q("Project"))
for name, value in [
    ("SaveVersion", 14),
    ("Name", OUT.name),
    ("Title", "Plan Maestro - Clínica Reina del Cisne"),
    ("Subject", "Desarrollo, validación, despliegue y mantenimiento del sistema clínico"),
    ("Category", "Sistema clínico Django"),
    ("Company", "Clínica Reina del Cisne"),
    ("Manager", "Jefe de proyecto"),
    ("ScheduleFromStart", 1),
    ("StartDate", project_start.isoformat()),
    ("FinishDate", project_finish.isoformat()),
    ("FYStartDate", 1),
    ("CriticalSlackLimit", 0),
    ("CurrencyDigits", 2),
    ("CurrencySymbol", "$"),
    ("CurrencyCode", "USD"),
    ("DefaultStartTime", "08:00:00"),
    ("DefaultFinishTime", "17:00:00"),
    ("MinutesPerDay", 480),
    ("MinutesPerWeek", 2400),
    ("DaysPerMonth", 20),
    ("DefaultTaskType", 0),
    ("DefaultFixedCostAccrual", 3),
    ("NewTasksEffortDriven", 0),
    ("NewTasksEstimated", 0),
    ("AutoAddNewResourcesAndTasks", 1),
    ("CurrentDate", "2026-08-21T08:00:00"),
    ("StatusDate", "2026-08-21T17:00:00"),
    ("CalendarUID", 1),
]:
    add(project, name, value)

calendars = SubElement(project, q("Calendars"))
calendar = SubElement(calendars, q("Calendar"))
add(calendar, "UID", 1); add(calendar, "Name", "Estándar"); add(calendar, "IsBaseCalendar", 1); add(calendar, "BaseCalendarUID", -1)
weekdays = SubElement(calendar, q("WeekDays"))
for day_type in range(1, 8):
    wd = SubElement(weekdays, q("WeekDay")); add(wd, "DayType", day_type)
    working = 2 <= day_type <= 6
    add(wd, "DayWorking", 1 if working else 0)
    if working:
        times = SubElement(wd, q("WorkingTimes"))
        for start, end in (("08:00:00", "12:00:00"), ("13:00:00", "17:00:00")):
            wt = SubElement(times, q("WorkingTime")); add(wt, "FromTime", start); add(wt, "ToTime", end)

tasks = SubElement(project, q("Tasks"))
root_task = SubElement(tasks, q("Task"))
for name, value in [("UID",0),("ID",0),("Name","Plan Maestro - Clínica Reina del Cisne"),("Type",1),("IsNull",0),("WBS","0"),("OutlineNumber","0"),("OutlineLevel",0),("Summary",1),("Start",project_start.isoformat()),("Finish",project_finish.isoformat()),("Duration",f"PT{max(8, int((project_finish-project_start).total_seconds()/3600))}H0M0S"),("DurationFormat",7),("PercentComplete",72),("CalendarUID",1)]:
    add(root_task, name, value)

phase_number = 0
child_number = 0
for item in items:
    if item["kind"] == "phase":
        phase_number += 1; child_number = 0
        outline = str(phase_number); level = 1; summary = 1
    else:
        child_number += 1
        outline = f"{phase_number}.{child_number}"; level = 2; summary = 0
    task = SubElement(tasks, q("Task"))
    values = [
        ("UID", item["uid"]), ("ID", item["id"]), ("Name", item["name"]),
        ("Type", 1), ("IsNull", 0), ("CreateDate", "2026-08-21T12:00:00"),
        ("WBS", outline), ("OutlineNumber", outline), ("OutlineLevel", level),
        ("Priority", 500), ("Start", item["start"].isoformat()), ("Finish", item["finish"].isoformat()),
        ("Duration", f"PT{item['duration'] * 8}H0M0S"), ("DurationFormat", 7),
        ("Work", f"PT{item['duration'] * 8}H0M0S"), ("Milestone", 1 if item.get("duration") == 0 and item["kind"] == "task" else 0),
        ("Summary", summary), ("PercentComplete", item.get("percent", 0)),
        ("PercentWorkComplete", item.get("percent", 0)), ("ConstraintType", 0),
        ("CalendarUID", -1), ("IgnoreResourceCalendar", 0),
    ]
    for name, value in values:
        add(task, name, value)
    if item["kind"] == "task":
        add(task, "Notes", f"Código WBS funcional: {item['code']}. Responsables: {', '.join(item['owners'])}.")
        for pred_code in item["pred_codes"]:
            if pred_code not in code_map:
                continue
            link = SubElement(task, q("PredecessorLink"))
            add(link, "PredecessorUID", code_map[pred_code]["uid"])
            add(link, "Type", 1); add(link, "CrossProject", 0); add(link, "LinkLag", 0); add(link, "LagFormat", 7)

resource_names = []
for item in items:
    for owner in item.get("owners", []):
        if owner not in resource_names:
            resource_names.append(owner)
resources = SubElement(project, q("Resources"))
resource_uid = {}
for uid, name in enumerate(resource_names, 1):
    resource_uid[name] = uid
    resource = SubElement(resources, q("Resource"))
    for field, value in [("UID",uid),("ID",uid),("Name",name),("Type",1),("IsNull",0),("Initials",''.join(p[0] for p in name.split())[:4].upper()),("MaxUnits",1),("PeakUnits",1),("CanLevel",1),("AccrueAt",3),("CalendarUID",1)]:
        add(resource, field, value)

assignments = SubElement(project, q("Assignments"))
assignment_uid = 0
for item in items:
    if item["kind"] != "task":
        continue
    for owner in item["owners"]:
        assignment_uid += 1
        assignment = SubElement(assignments, q("Assignment"))
        for field, value in [("UID",assignment_uid),("TaskUID",item["uid"]),("ResourceUID",resource_uid[owner]),("PercentWorkComplete",item["percent"]),("Units",1),("Work",f"PT{item['duration'] * 8}H0M0S"),("Start",item["start"].isoformat()),("Finish",item["finish"].isoformat())]:
            add(assignment, field, value)

OUT.parent.mkdir(exist_ok=True)
ElementTree(project).write(OUT, encoding="utf-8", xml_declaration=True)
print(f"{OUT}|tasks={len(items)}|resources={len(resource_names)}|assignments={assignment_uid}")
