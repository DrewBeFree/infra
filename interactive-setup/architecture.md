# Dashboard System Architecture

## Core
PowerEdge = brain  
Python = backend logic  
HTML = frontend UI  

## Clients
- iPad → interactive (/control)
- Small monitor → passive (/status)

## Routes
/control → tasks, notes, actions  
/status → time, system health, glance info  

## Principles
- local-first
- minimal UI
- separate control vs display
- no cloud dependency

## Stack
- Python (Flask or simple server)
- Static HTML/JS frontend
- Optional Grafana embeds (read-only)