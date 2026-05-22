# AI DOG TRAINER

`ai-dog-trainer`

AI-powered dog training chatbot. Drew — a positive-reinforcement trainer — coaches you through live sessions with your dog using Claude.

| Field | Value |
| --- | --- |
| Type | app |
| Version | v0.1.0 |
| Updated | 2026-05-22 |
| Status | active |
| Repo | https://github.com/DrewBeFree/ai-dog-trainer |
| Local path | `apps/ai-dog-trainer` |

## How to Use

AI Dog Trainer is an interactive training session tool powered by Claude. "Drew" — an enthusiastic positive-reinforcement trainer — coaches you through a session with your dog in real time.

### First Launch

On first load, you'll be prompted to enter your **Anthropic API key**. This is stored in your browser's localStorage — it is never sent to any server other than Anthropic's API directly.

### Starting a Session

1. Open the app and the trainer will greet you
2. Drew asks for your dog's **name, breed, and age** — provide these to get a personalized session
3. Once Drew has that info, the training session begins

### During a Session

Drew speaks directly to your dog (commands are in ALL CAPS) and gives you coaching tips in parentheses.

**Example response:**
> "Buddy, SIT! ... Good boy!! Yes!! (Give the treat immediately — timing is everything) Now, Buddy, STAY... stay... good. (Hold two fingers up as a visual cue) COME!"

Type your responses to tell Drew how the dog is responding — for example:
- "He sat but got up when I said stay"
- "She nailed it, treat given"
- "He's distracted by the other dog"

Drew will adapt the session based on how your dog is performing.

### Conversation History

Your conversation history is saved in localStorage — you can close and reopen the app and pick up where you left off. Click **Clear History** to start a fresh session.

### Tips

- Short sessions (10–15 min) work better than long ones — dogs fatigue quickly
- Have treats ready before you start
- Train in a low-distraction environment for new commands; add distractions as the dog improves
- Tell Drew specifically what's happening ("she's whining", "he keeps lying down") for better coaching
