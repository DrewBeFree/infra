# POKER NIGHT

![POKER NIGHT](https://poker.drewbefree.com/icons/poker-192.png)

`poker`

Full session manager for No-Limit Hold'em cash games. Timer, rounds, buy-ins, rebuys, mid-game cashouts, and end-of-night payout balancer.

| Field | Value |
| --- | --- |
| Type | app |
| Version | v0.7.0 |
| Updated | 2026-05-29 |
| Status | active |
| Live | https://poker.drewbefree.com |
| Repo | https://github.com/DrewBeFree/poker |
| Local path | `apps/poker` |

## How to Use

Poker Night manages a No-Limit Hold'em cash game from start to payout.

### Starting a Game

1. Open [poker.drewbefree.com](https://poker.drewbefree.com)
2. Enter each player's name and starting buy-in amount
3. Click **Add Player** for each participant
4. Set the starting blinds and round duration in the **Blinds** panel
5. Click **Start Game** — the blinds timer begins automatically

### During the Game

**Rebuys** — when a player busts and wants to continue, click their name and enter the rebuy amount. This adds to their total buy-in.

**Cashouts** — when a player leaves early, click **Cash Out**, enter how many chips they're cashing out, and they're removed from active play. Their result is locked in.

**Blinds timer** — the timer panel shows the current blind level and counts down to the next increase. Pause or skip levels from the host panel.

### Ending the Game

1. Click **End Game** from the host panel
2. Each remaining player enters their chip count
3. The **Payout Balancer** calculates who owes whom — it minimizes the number of transactions
4. Review the settlement list and collect/pay accordingly

### Host Controls

The host panel is accessible to the game creator. From here you can:
- Add/remove players mid-game
- Adjust the blinds schedule
- Pause the timer
- Force-end the game

### Tips

- All game state is saved to Supabase — refreshing the page won't lose progress
- Players can open the same URL on their phone to follow along
- The payout balancer handles odd-cent amounts automatically
