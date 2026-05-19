# 🤖 Bob System Architecture

## 🧠 Core Principle
PowerEdge is the brain and router.  
All requests hit PowerEdge first.

---

## 🏗️ Components

### PowerEdge (Primary)
- Slack bot host (Bob)
- Router / decision engine
- Memory store (ChromaDB, files, logs)
- Dashboard backend (Python + HTML)
- Job queue manager

---

### Alienware (GPU Compute)
- Runs local LLMs (Ollama / LM Studio)
- Handles:
  - private AI queries
  - RAG synthesis
  - fast local inference
- Used only when:
  - online
  - not busy (e.g. gaming)

---

### Claude API (Cloud AI)
- Handles:
  - complex reasoning
  - coding tasks
  - high-quality writing
- Used when:
  - quality matters
  - Alienware unavailable or busy

---

### K80 (Background Worker)
- Handles:
  - embedding generation
  - batch summarization
  - re-indexing jobs
- Never used for real-time responses
- Optional (not required for system success)

---

## 🔁 Request Flow


Slack → PowerEdge (Bob) → Router → Destination → Response → Slack


---

## 🧭 Router Decision Logic

### Local / PowerEdge
Use when the answer is deterministic or already stored.

Examples:
- “Is the server up?”
- “What jobs are running?”
- “Search my notes for VLAN”
- “Show today’s dashboard status”


PowerEdge → local processing → Slack


---

### Alienware (GPU)

Use when:
- Requires reasoning on private/local data
- Needs fast local AI
- Alienware is online AND idle

Examples:
- “Summarize my VLAN notes”
- “Answer from my private knowledge base”
- “Draft internal explanation”


PowerEdge → Alienware → PowerEdge → Slack


---

### Claude API

Use when:
- High-quality reasoning or writing required
- Alienware is busy or offline
- Output is not sensitive

Examples:
- “Write a technical memo”
- “Design this system”
- “Rewrite for a client”


PowerEdge → Claude → PowerEdge → Slack


---

### K80 / Background Jobs

Use only for non-urgent batch processing.

Examples:
- “Process 100 PDFs”
- “Re-index transcripts”
- “Generate embeddings”


PowerEdge → Job Queue → K80/CPU Worker → Store Results


---

## 🎮 Alienware State Handling

### Alienware ON + Idle
- Use normally for AI requests

---

### Alienware ON + Busy (Gaming / High Load)

Routing behavior:

- Simple → PowerEdge
- Private AI → Queue OR fallback CPU/K80
- High-quality → Claude
- Heavy non-urgent → Queue

Optional response:
> “Alienware is busy. Want me to use Claude or wait?”

---

### Alienware OFF

Routing behavior:

- Simple → PowerEdge
- High-quality → Claude
- Private → CPU fallback
- Heavy → Queue

---

## 📊 Decision Table

| Request Type            | Alienware Idle | Alienware Busy | Alienware Off |
|------------------------|----------------|----------------|----------------|
| Status / simple        | PowerEdge      | PowerEdge      | PowerEdge      |
| KB lookup              | PowerEdge      | PowerEdge      | PowerEdge      |
| Private AI             | Alienware      | CPU/K80        | CPU fallback   |
| High-quality reasoning | Alienware/Claude | Claude       | Claude         |
| Bulk processing        | K80/CPU        | K80/CPU        | K80/CPU        |

---

## 💰 Cost Controls

- Default to local processing first
- Use Claude only for high-value tasks
- Set token budgets per request type
- If Claude budget exceeded:
  - fallback to Alienware
  - or queue request
- Batch expensive jobs off-hours

---

## ⚙️ K80 Strategy

K80 is optional.

Use only after:
- successful installation
- stable drivers
- proven performance gain

Otherwise:
- use PowerEdge CPU for batch jobs
- use Alienware for AI
- use Claude for quality

---

## 🧩 Architecture Diagram


Slack
↓
PowerEdge (Bob)
├─ Router
├─ Memory (ChromaDB / files)
├─ Job Queue
├─ Claude API
├─ Alienware API
└─ K80/CPU Worker


---

## 🧠 Key Rules

- PowerEdge always answers first
- Alienware is optional acceleration
- Claude is premium fallback
- K80 is background only
- System must degrade gracefully

---

## 🎯 Summary

PowerEdge = brain + router  
Alienware = fast local AI  
Claude = high-quality AI  
K80 = background processing  

Bob always responds regardless of system state.