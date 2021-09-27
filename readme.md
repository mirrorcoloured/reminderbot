Configure reminders in the reminders.json file. Example:
```
{
    "Message": "Switch sit/stand",
    "Interval": 1,
    "Unit": "h",
    "Offset": 0.25
}
```

* Message is what appears in the message box
* Interval is the amount of time that should pass between each reminder (decimals are okay)
* Unit is the unit that the interval uses (use "h", "m", or "s")
* Offset is optional, and is added to the first interval only (uses the same unit as the Interval)
