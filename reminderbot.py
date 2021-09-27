import win32api, win32con
import winsound
import time
from datetime import datetime, timedelta
import json

filename = "reminders.json"
alert_note = (740, 300) # play F#5 for 300 ms


with open(filename, "r") as f:
    reminders = json.loads(f.read())

# Calculates the next time this reminder should happen
def calculate_next(reminder, use_offset=False):
    now = datetime.now()
    value = reminder["Interval"]
    if use_offset:
        value += reminder.get("Offset", 0)

    if reminder["Unit"] == "s":
        reminder["Next"] = now + timedelta(seconds=value)
    elif reminder["Unit"] == "m":
        reminder["Next"] = now + timedelta(minutes=value)
    elif reminder["Unit"] == "h":
        reminder["Next"] = now + timedelta(hours=value)

# Calculate next time for each reminder
for reminder in reminders:
    calculate_next(reminder, use_offset=True)
# Sort so next reminder is first in array
reminders.sort(key = lambda x: x["Next"])

print("Starting reminderbot...")
try:
    while True:
        next_reminder = reminders[0]
        now = datetime.now()
        if next_reminder["Next"] >= now:
            delay = (next_reminder["Next"] - now).seconds
            time.sleep(delay)
        winsound.Beep(*alert_note)
        win32api.MessageBox(
            0,
            next_reminder["Message"] + f"\n\n{now.strftime('%H:%M:%S')}",
            "Reminderbot",
            win32con.MB_OK
        )
        calculate_next(next_reminder)
        reminders.sort(key = lambda x: x["Next"])
except KeyboardInterrupt:
    print("Exiting reminderbot...")