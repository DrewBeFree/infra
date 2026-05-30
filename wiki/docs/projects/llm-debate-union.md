# llm-debate-union

A stunning, premium multi-agent cognitive arena where different AI models (Antigravity, ChatGPT, Grok, Gemini, Codex, Ollama) debate structured motions using the Oxford-style debate format.

| Field | Value |
| --- | --- |
| Type | app |
| Local path | `apps/llm-debate-union` |

# Oxford LLM Debate Union — User Manual

Welcome to the **Oxford LLM Debate Union**, a multi-agent cognitive arena. This application is a client-side Progressive Web App (PWA) that allows you to orchestrate structured debates between various artificial intelligence agents (Antigravity, ChatGPT, Claude, Grok, Gemini, Codex, Ollama).

---

## 📖 Key Concepts & Terminology

### 1. What is a "Motion"?
In formal parliamentary and academic debate, the **Motion** is the central proposal or topic under discussion. It is framed as a statement (e.g., *"This House believes Artificial General Intelligence will be achieved before 2030"*).
- The **Proposition** team defends the motion as true.
- The **Opposition** team attacks the motion and argues it is false.

### 2. What is "Audience Profile"?
The **Audience Profile** determines the baseline distribution of audience opinion before the debate starts, as well as how they respond to arguments:
- **Neutral Public**: An even 33% split between Pro, Con, and Undecided. They shift dynamically in response to solid points.
- **Hardened Tech Skeptics**: Highly biased toward the Opposition (Con) at the start. They require rigorous evidence to sway.
- **Transhumanist Tech-Bro Enthusiasts**: Highly biased toward the Proposition (Pro) at the start. They shift easily to supporting statements.
- **Conservative Academics**: Highly critical of quick claims and have a larger share of "Undecided" voters at the start.

### 3. What is "Swing Shift"?
Under the standard Oxford-style debate rules, the winner is **NOT** the team with the most total votes at the end. Instead, victory is decided by the **Swing Shift** (net change in votes from baseline):
$$\text{Swing Shift} = \text{Post-Debate Vote} - \text{Pre-Debate Vote}$$
Whichever team shifts a higher percentage of voters to their side wins. This means if the Proposition starts at 20% and ends at 35% (+15%), they beat an Opposition that starts at 50% and ends at 55% (+5%), even though the Opposition has a higher final percentage.

---

## ⚖️ Chamber Modes: Debate vs. Assembly

You can switch the operating style of the session using the **Chamber Mode** dropdown:

### 1. Parliamentary Debate Mode (Adversarial)
* **Goal**: Determine the rhetorical victor of a public policy or philosophical resolution (e.g. *"AGI before 2030"*).
* **Role Mappings**:
  * **Proposition**: Defends the Motion.
  * **Opposition**: Opposes the Motion.
  * **Moderator**: Chairs the debate and enforces strict parliamentary structure.
* **Success Metric**: Measured by **Audience Opinion Swing Shift**. Whichever team shifts the highest percentage of undecided/opposing voters wins.

### 2. Engineering Assembly Mode (Collaborative)
* **Goal**: Build consensus around a high-fidelity system design and compile a downloadable technical blueprint document for a local app or new project (e.g. `apps/ai-dog-trainer` or custom targets).
* **Role Mappings**:
  * **System Architects (Pro 1 & 2)**: Propose modular layout structures, computation offloading (Web Workers), and offline state engines.
  * **Security & Quality Auditors (Con 1 & 2)**: Stress-test proposals against thermal limits, BLE replay vectors, database locks, and runtime error boundaries.
  * **Assembly Chair (Moderator)**: Synthesizes technical consensus, poses architectural questions, and steers the team toward consensus.
* **Success Metric**: Measured by **Stakeholder Alignment / Consensus level**. As architects and auditors address edge cases, unaligned stakeholder consensus migrates toward full alignment.
* **Outputs**: At the final phase, you can download a complete Markdown **Technical Architecture Blueprint** specifying files, schemas, and immediate next steps.

---

## 🔄 The Oxford Session Cycle (14 Steps)

Both modes execute a structured 14-step state machine across 6 visual phases on the timeline:

1. **🗳️ Phase 1: Pre-Vote / Pre-Align (Step 0)**
   * Moderator/Chair introduces the motion or target application.
   * Establish initial audience opinion or stakeholder consensus baseline.
2. **🎤 Phase 2: Openings (Steps 1–4)**
   * **Step 1**: Speaker 1 Pro (Proposition Opening / Architect Core Design Proposal)
   * **Step 2**: Speaker 1 Con (Opposition Opening / Auditor Initial Audit critique)
   * **Step 3**: Speaker 2 Pro (Proposition Opening / Architect Supporting Design Details)
   * **Step 4**: Speaker 2 Con (Opposition Opening / Auditor Secondary Vulnerability analysis)
3. **⚡ Phase 3: Rebuttals / Audit Iteration (Steps 5–9)**
   * **Step 5**: Moderator calls for rebuttals/audit feedback.
   * **Steps 6–9**: Pro and Con speakers exchange rebuttals or propose architectural mitigations (e.g., ring-buffer database queues, WebGPU acceleration, Web Crypto APIs).
4. **🙋 Phase 4: Interrogation (Step 10)**
   * The Moderator poses a direct, challenging question to the floor, testing the robustness of the debate logic or design boundaries.
5. **📜 Phase 5: Closings (Steps 11–12)**
   * **Step 11**: Opposition Speaker 2 Closing (Auditor final sign-off parameters).
   * **Step 12**: Proposition Speaker 2 Closing (Architect final proposal synthesis).
6. **🏆 Phase 6: Verdict & Blueprint (Step 13)**
   * **Debate Mode**: The Moderator conducts the post-debate poll swing audit and declares the winner.
   * **Assembly Mode**: The Chair summarizes the consensus, outputs the actionable next steps ("Where to Go From Here"), and generates the downloadable `.md` Technical Architecture Blueprint.

---

## 💻 Codebase Context Input
In **Engineering Assembly Mode**, an optional **App Context / Source Code** textarea is enabled in the sidebar. You can paste:
- Class interfaces, REST or GraphQL API structures, or configuration files.
- Specific layout plans or performance concerns.
- Active agent models will parse this context input during live queries (Ollama/Hybrid modes) to construct highly targeted code blocks and blueprint specifications.

---

## ⚙️ Operating Modes & API Configuration

Click the **⚙️ API CONFIG** button in the header to select your execution environment:

### A. High-Fidelity Simulation Mode
* **Requires**: No API keys, no local server, no internet connection.
* **How it works**: Uses a pre-programmed high-fidelity database of stylized debates written specifically to highlight the model personas for core topics (e.g., AGI 2030, CSS vs Tailwind, AI replacing devs, and the **AI Dog Trainer App** assembly). If you choose a custom motion, it will generate procedural, persona-guided template speeches offline.

### B. Ollama Only Mode
* **Requires**: A local Ollama server running on your machine or network.
* **Host URL**: Default is `http://localhost:11434`.
* **CORS Setup**: Start Ollama from your command line with:
  ```bash
  OLLAMA_ORIGINS="*" ollama serve
  ```
* **How it works**: The app queries your local Ollama tags, detects your installed models (e.g., Llama, Mistral), and prompts them to play all debate or assembly roles dynamically.

### C. Live Hybrid Mode
* **Requires**: Direct API Keys for cloud platforms (OpenAI, Gemini, Grok, Anthropic/Claude).
* **How it works**: Routes active speakers to their respective cloud models using your stored credentials.
* **Local Security**: API keys are saved strictly within your browser's private `localStorage` and never transmitted to external third-party servers.

---

## 🤖 The 7 Model Personas

Each agent is governed by a distinct persona style injected into its system prompt:
1. **Antigravity**: Agentic, objective-based, systematic. Speaks in state transitions and uses code-block analogies.
2. **ChatGPT**: Professional, highly structured, balanced. Frequently uses clear markdown lists.
3. **Claude**: Nuanced, reflective, deeply intellectual. Focuses on systemic trade-offs, safety, and ethics.
4. **Grok**: Witty, sarcastic, bold, and energetic. Pokes fun at academic styles.
5. **Gemini**: Academic, societal, comprehensive. Looks at global and societal implications.
6. **Codex**: Syntax-centric, concise, and dry. Argues in pseudo-code flowcharts and logic compilers.
7. **Ollama**: Local-first, practical, open-source enthusiast. Autonomy-centric and developer-focused.

### Customizing Persona System Prompts

Click the **🎭 PERSONAS** button in the header to customize the system prompt for any of the 6 debate personas. This allows you to:

- **Override default prompts** — Write your own system instructions for how a persona should argue
- **Save per-session** — Custom prompts are stored in your browser's localStorage (`custom_prompt_[persona_name]`)
- **Reset to defaults** — Each persona has a "View Default" button to see the original prompt
- **Reset all prompts** — Bulk reset all custom prompts back to defaults

Custom prompts are automatically applied to all debates in your session. This is useful for tuning debate styles, testing different argument approaches, or specializing personas for specific topics.

## Infrastructure Plan

- [Atlas + PocketBase deployment workflow](../workflows/llm-debate-union-atlas-pocketbase.md)
