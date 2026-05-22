# DAILY PLANNER

![DAILY PLANNER](https://tasks.drewbefree.com/icons/planner-192.png)

`daily-planner`

Personal daily-driver for tasks, grocery lists, and trip packing lists. Supabase-backed persistence, auto-prints each morning via Windows Task Scheduler.

| Field | Value |
| --- | --- |
| Type | app |
| Version | v0.9.5 |
| Updated | 2026-05-16 |
| Status | active |
| Live | https://tasks.drewbefree.com |
| Repo | https://github.com/DrewBeFree/daily-planner |
| Local path | `apps/daily-planner` |

## How to Use

Daily Planner is a personal productivity app with three tabs: Tasks, Groceries, and Trips.

### Tasks Tab

The Tasks tab is your daily to-do list.

- **Add a task** — type in the input box and press Enter or click Add
- **Complete a task** — click the checkbox; completed tasks move to the bottom
- **Archive** — archived tasks are hidden but preserved; use the Archive toggle to review them
- **Print** — the app auto-prints each morning via Windows Task Scheduler; manually trigger with the Print button

### Groceries Tab

Manage multiple grocery lists (one per store or trip).

- **Create a list** — click **New List**, enter a store name
- **Add items** — type an item and press Enter
- **Check off items** — tap/click to mark as purchased; checked items stay visible until you clear them
- **Clear checked** — removes all checked items from the active list
- **Switch lists** — use the list selector at the top to jump between stores

### Trips Tab

Packing lists for upcoming trips.

- **Create a trip** — click **New Trip**, enter a trip name and dates
- **Add packing items** — type items you need to pack
- **Check off as you pack** — mark items done as you add them to your bag
- **Archive a trip** — once the trip is over, archive it to keep your list clean without losing the history

### Data Sync

All data saves to Supabase in real time — open the app on any device and your lists are current.

### Tips

- The auto-print runs every morning so you start the day with a fresh paper list
- Keep separate grocery lists for Costco, Publix, etc. rather than one combined list
- Archive old tasks at the end of the week to start fresh
