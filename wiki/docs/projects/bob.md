# bob

A lightweight Slack bot backed by a local Ollama LLM running on Atlas (PowerEdge R720xd).

| Field | Value |
| --- | --- |
| Type | agent |
| Repo | https://github.com/DrewBeFree/bob |
| Local path | `agents/bob` |

## How It Works

Bob is a Slack bot backed by a local Ollama LLM running on Atlas. He responds to DMs and @mentions in channels using `llama3.2:1b` for fast local inference — no cloud API, no cost per message.

### Talking to Bob

- **DM Bob** directly in Slack — he'll respond in the thread
- **@mention Bob** in any channel — he'll reply in that channel
- Bob automatically knows today's date (injected into every system prompt)

### Running on Atlas

Bob runs as a systemd user service on Atlas. Common service commands:

```bash
# Check status
systemctl --user status bob.service

# Restart (e.g., after config changes)
systemctl --user restart bob.service

# View live logs
journalctl --user -u bob.service -f
```

### Initial Setup (one-time)

```bash
# On Atlas
python3 -m venv /home/drew/services/bob/venv
/home/drew/services/bob/venv/bin/pip install -r requirements.txt

cp bob.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now bob.service
```

### Configuration

Slack tokens and the Ollama model are set directly in `bot.py`:
- **`MODEL`** constant — change to use a different Ollama model (e.g., `llama3.2:3b`, `mistral`)
- Ollama must be running at `http://127.0.0.1:11434` on Atlas

### Changing the Model

Edit `bot.py`, update the `MODEL` constant, then restart the service:

```bash
systemctl --user restart bob.service
```
