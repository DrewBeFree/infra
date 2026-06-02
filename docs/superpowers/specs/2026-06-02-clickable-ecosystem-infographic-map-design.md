# Clickable Ecosystem Infographic Map Design

## Context

The internal portal map currently behaves like an accordion sitemap. It is useful for scanning categories, but it does not feel like an infographic of the running ecosystem. The approved direction is a hybrid of the metro / flow map and topology board concepts.

## Approved Direction

Build a clickable hybrid map that shows:

- A flow from source of truth and GitHub repositories into launch surfaces and Atlas-hosted operations.
- Topology zones for public edge, Atlas core, Alienware local compute, docs/planning, and sensitive/control surfaces.
- Inline visibility and type badges on each clickable node.
- Existing drawer behavior on node click, so the map becomes a launcher and details surface.
- Existing global search and filter behavior across all portal streams.

## Alienware Placement

Alienware should be visible in the map as a local compute / workstation node, not hidden inside generic Homelab. It should connect to local AI services such as Ollama, Open WebUI, and OpenClaw, plus local-dev work such as Lead Gen Agent and LLM Debate Union.

## Interaction Model

- Clicking a map node opens the existing details drawer for that item.
- Clicking a zone header can focus related nodes by opening the drawer for the best representative resource when one exists.
- Search and filters should reduce the visible nodes and update the map summary.
- Empty zones should remain visible with a compact empty state so the map structure does not collapse unpredictably.

## Visual Model

Use a full-width infographic board with:

- Zone cards arranged as a responsive grid.
- A central Atlas node.
- Distinct Alienware node in the local compute zone.
- Thin connection rails between source, Atlas, public edge, docs/planning, local compute, and sensitive controls.
- Compact chips for child resources.
- Subtle fade/slide-in motion, respecting reduced-motion preferences.
