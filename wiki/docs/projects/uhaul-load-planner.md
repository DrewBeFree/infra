# UHAUL PLANNER

`uhaul-load-planner`

Interactive overhead floor plan for a 26' U-Haul. Drag-and-drop items to scale, track floor usage in real time, auto-saves layout across visits.

| Field | Value |
| --- | --- |
| Type | app |
| Version | v0.9.2 |
| Updated | 2026-05-10 |
| Status | active |
| Live | https://uhaul.drewbefree.com |
| Repo | https://github.com/DrewBeFree/uhaul-load-planner |
| Local path | `apps/uhaul-load-planner` |

## How to Use

UHaul Planner helps you visually plan how to pack a 26' U-Haul truck before moving day.

### The Floor Plan

The canvas shows a to-scale overhead view of the truck floor:
- **Main floor:** 23'6" × 8'1" (~190 sq ft) — the primary loading area
- **Mom's Attic:** 2'7" × 8'1" — the raised shelf above the cab

A real-time counter shows square footage used and remaining.

### Adding Items

1. Click **Add Item** to create a new piece of furniture or box
2. Enter a label (e.g., "Queen Bed Frame"), width, and depth in feet/inches
3. Choose a color to visually group items (e.g., blue for bedroom, green for kitchen)
4. Click **Place** — the item appears on the canvas

### Arranging the Layout

- **Drag** items anywhere on the floor plan
- **Rotate** items 90° using the rotate handle
- **Snap to grid** keeps items aligned to the 1 ft grid
- **Resize** by dragging item edges (if enabled)
- **Delete** an item by selecting it and pressing Delete, or clicking the × button

### Saving Your Layout

Your layout saves automatically to Supabase — you can close the tab and return later without losing anything. Multiple devices can view the same plan.

### Truck Specs Reference

| Spec | Measurement |
| --- | --- |
| Main floor | 23'6" × 8'1" |
| Mom's Attic | 2'7" × 8'1" |
| Door opening | 7'9" W × 6'10" H |
| Max load weight | 9,010 lbs |

### Tips

- Plan heavy items (furniture, appliances) first along the sides and front
- Leave a path to the door for items you'll need to access first
- Use the color groups to mentally separate rooms — makes unloading faster
