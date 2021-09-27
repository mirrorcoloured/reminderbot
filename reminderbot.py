import win32api, win32con
import winsound
import time
from datetime import datetime, timedelta
import json
import hashlib
from string import Template

filename = "reminders.json"
note_duration = 300
verbose = True

with open(filename, "r") as f:
    reminders = json.loads(f.read())


# Calculates the next time this reminder should happen
def calculate_next(reminder, use_offset=False):
    value = reminder["Interval"]
    if use_offset:
        value += reminder.get("Offset", 0)

    if reminder["Unit"] == "s":
        reminder["Next"] += timedelta(seconds=value)
    elif reminder["Unit"] == "m":
        reminder["Next"] += timedelta(minutes=value)
    elif reminder["Unit"] == "h":
        reminder["Next"] += timedelta(hours=value)


# Formats a datetime or timedelta object
def just_time(dt, format='%H:%M:%S'):
    if type(dt) is timedelta:
        class DeltaTemplate(Template):
            delimiter = "%"

        def strfdelta(tdelta, fmt):
            d = {"D": tdelta.days}
            hours, rem = divmod(tdelta.seconds, 3600)
            minutes, seconds = divmod(rem, 60)
            d["H"] = '{:02d}'.format(hours)
            d["M"] = '{:02d}'.format(minutes)
            d["S"] = '{:02d}'.format(seconds)
            t = DeltaTemplate(fmt)
            return t.substitute(**d)
        return strfdelta(dt, format)
    return dt.strftime(format)


# Generates a note frequency based on a message hash
def message_to_note(message, octaves=2, root=440):
    step = 2 * (12 ** 0.5)
    options = [r - (octaves * 12) for r in range((octaves * 24) + 1)]
    m = int(hashlib.sha256(bytes(message, 'utf-8')).hexdigest(), 16)
    steps = options[m % len(options)]
    return int(root + step * steps)


def list_reminders():
    now = datetime.now()
    print(f"* {just_time(now)}")
    print("Upcoming:")
    for r in reminders:
        print(f"+ {just_time(r['Next'])} {r['Message']}")
    print("")

# Calculate next time for each reminder
now = datetime.now()
for reminder in reminders:
    reminder["Next"] = now
    calculate_next(reminder, use_offset=True)
# Sort so next reminder is first in array
reminders.sort(key = lambda x: x["Next"])
if verbose: list_reminders()


print(f"Found {len(reminders)} reminders. Starting reminderbot...")
try:
    while True:
        next_reminder = reminders[0]
        now = datetime.now()
        # print(f"Next reminder at {just_time(next_reminder['Next'])} ({next_reminder['Message']})")
        late = 0
        if next_reminder["Next"] >= now:
            delay = (next_reminder["Next"] - now).seconds
            time.sleep(delay)
        else:
            late = now - next_reminder["Next"]
        winsound.Beep(message_to_note(next_reminder["Message"]), note_duration)
        if verbose: print(f"Reminding: {next_reminder['Message']} | {just_time(next_reminder['Next'])}",)
        message = (f"{next_reminder['Message']}" + f"\n\n{just_time(next_reminder['Next'])}")
        if late != 0:
            message += f" (late by {just_time(late)})"
        win32api.MessageBox(
            0,
            message,
            "Reminderbot",
            win32con.MB_OK
        )
        calculate_next(next_reminder)
        reminders.sort(key = lambda x: x["Next"])
        
        if verbose: list_reminders()
except KeyboardInterrupt:
    print("Exiting reminderbot...")