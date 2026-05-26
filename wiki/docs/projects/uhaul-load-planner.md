# UHAUL PLANNER

![UHAUL PLANNER](https://uhaul.drewbefree.com/icons/uhaul-192.png)

`uhaul-load-planner`

Interactive overhead floor plan for a 26' U-Haul. Drag-and-drop items to scale, track floor usage in real time, auto-saves layout across visits.

| Field | Value |
| --- | --- |
| Type | app |
| Version | v0.13.1 |
| Updated | 2026-05-26 |
| Status | active |
| Live | https://uhaul.drewbefree.com |
| Repo | https://github.com/DrewBeFree/uhaul-load-planner |
| Local path | `apps/uhaul-load-planner` |

## How to Use

UHaul Planner helps you visually plan how to pack a U-Haul truck (or multiple trucks) before moving day. It supports both a 2D overhead view and a 3D scene for visualizing stacking and depth.

### The Floor Plan

The canvas shows a to-scale overhead view of the truck floor:
- **Main floor:** 23'6" × 8'1" (~190 sq ft) — the primary loading area
- **Mom's Attic:** 2'7" × 8'1" — the raised shelf above the cab

A real-time counter shows square footage used and remaining.

### Multi-Truck Support

If your move requires more than one truck, you can add additional trucks and plan each one independently. Switch between trucks using the truck selector. Each truck has its own floor plan and item list, all saved to your layout. The truck size is persisted per layout.

### Adding Items

1. Click **Add Item** to create a new piece of furniture or box
2. Enter a label (e.g., "Queen Bed Frame"), width, and depth in feet/inches
3. Choose a color to visually group items (e.g., blue for bedroom, green for kitchen)
4. Click **Place** — the item appears on the canvas

You can also pick from the **Furniture Preset Catalog** (26 common items) to auto-fill dimensions.

### 2D View — Arranging the Layout

- **Drag** items anywhere on the floor plan
- **Rotate** items 90° using the rotate handle
- **Snap to grid** keeps items aligned to the 1 ft grid
- **Delete** an item by selecting it and pressing Delete, or clicking the × button
- The sidebar collapses automatically on mobile

### 3D View — Scene Controls

The 3D scene renders items as physical boxes in the truck at their actual heights and stacking positions, with dynamically generated proportional models for the entire U-Haul fleet (Cargo Van, 10', 15', 20', 26'):
- **Drag** items to reposition them on the truck floor
- **Double-Click** an item to open the Edit Properties modal directly from the 3D view
- **Re-center Button (⌖)** in the top right instantly smoothly resets the camera to the default orbit position
- Items stack physically — the list order determines which items sit on top, and physics calculations automatically route items around internal truck wheel wells
- Labels are dynamically wrapped and rendered flush onto the physical sides of each item

### Door Fit Check

When you place an item, the app checks whether it fits through the truck's door opening (7'9" W × 6'10" H). Items that won't fit are flagged so you can plan accordingly.

### Weight / Payload Indicator

A color-coded progress bar tracks the total weight of your items against the truck's 9,010 lb payload limit. It turns yellow as you approach the limit and red if you exceed it.

### Layout Management

Layouts are named and saved to Supabase — create multiple layouts (e.g., "First Load", "Second Load") and switch between them from the layout menu. Each layout saves independently. Creating a new layout prompts for a truck size selection. The selected truck size is persisted with the layout and restored on load.

### Saving Your Layout

Your layout saves automatically — you can close the tab and return later without losing anything. Multiple devices can view the same plan.

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
- Use the 3D view to visualize stacking and verify tall items fit under the truck ceiling

### Data Model

Each item carries a full set of 3D-native fields in addition to its 2D footprint: `hIn` (height), `weightLbs`, `fragility` (1–5 scale), `z` (vertical stacking position), and `rotation`. Old saved layouts are automatically migrated on load with sensible defaults.

### Tech Stack

The app is built with **Vite + Svelte 5 + Threlte** (Three.js wrapper for Svelte). The 2D canvas uses a Svelte component; the 3D scene uses Threlte's `<Canvas>`, `<Mesh>`, and `<T>` primitives with `interactivity()` for pointer events.

Run `npm run dev` for local development, `npm run build` to produce a static bundle deployed via GitHub Actions to GitHub Pages.
