# ICS GENERATOR TEMPLATE — used by /curriculum A4 and Flow K
#
# How to use:
#   1. Read this file.
#   2. Substitute the four variables below with real values from plan.md.
#   3. Write the filled-in script to a temp file and run it via Bash.
#   Never use the Write tool to create .ics files directly — use this script.
#
# Variables to substitute before running:
#   <YYYY>        — 4-digit year from plan.md created: date
#   <MM>          — 2-digit month
#   <DD>          — 2-digit day
#   <slug>        — curriculum slug (e.g. learn-ai-engineering)
#   <goal>        — full goal string for calendar name
#   [topics list] — Python list of day_label strings, one per day, verbatim from plan.md Topic column
#   <N>           — duration in minutes per session (derived from time_budget)
#   <vault>       — vault root path (the {{VAULT}} path patched by the installer)

from datetime import date, timedelta
import uuid

start = date(<YYYY>, <MM>, <DD>)   # plan created date
slug = "<slug>"
goal = "<goal>"
topics = [
    # one day_label string per day, verbatim from plan.md Topic (day_label) column
    # e.g. "Transformers and self-attention",
    # "Positional encoding basics",
]
duration_min = <N>   # e.g. 60
vault = "<vault>"    # substitute with your vault root path before running

lines = [
    "BEGIN:VCALENDAR", "VERSION:2.0",
    f"PRODID:-//{goal} Curriculum//EN",
    "CALSCALE:GREGORIAN", "METHOD:PUBLISH",
    f"X-WR-CALNAME:{goal} Curriculum",
]
for i, topic in enumerate(topics, start=1):
    d = start + timedelta(days=i - 1)
    nn = str(i).zfill(2)
    obs = f"obsidian://open?vault=llm-wiki-memory&file=curricula/{slug}/day-{nn}/concepts"
    # Note: for multi-note days the target file is concepts-01-<slug>.md, not concepts.md.
    # If the plan table's "# notes" column shows >1 for this day, replace 'concepts' above
    # with 'concepts-01-<topic-slug>' (the first concept note for that day).
    lines += [
        "BEGIN:VEVENT",
        f"UID:{slug}-day-{i}-{uuid.uuid4().hex[:8]}@curriculum",
        f"DTSTART;TZID=Asia/Kolkata:{d.strftime('%Y%m%d')}T080000",
        f"DURATION:PT{duration_min}M",
        f"SUMMARY:Day {i}: {topic} — {goal}",
        f"DESCRIPTION:{obs}",
        "STATUS:CONFIRMED", "END:VEVENT",
    ]
lines.append("END:VCALENDAR")

out_path = f"{vault}/curricula/{slug}/schedule.ics"
with open(out_path, "w") as f:
    f.write("\r\n".join(lines) + "\r\n")
print(f"Written {len(topics)} events to {out_path}")
