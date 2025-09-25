# Math Coach Telegram Bot (Question-First Tutoring)

A Telegram bot that helps students **learn to solve** math problems by guiding them
through a sequence of small questions. It **doesn't give the final answer** — the student
arrives at it by answering sub-questions. Built with **Python + aiogram v3**.

## What it does
- Student sends a problem like: `Solve: 2x + 5 = 17`
- Bot classifies topic (linear, fractions, quadratic, etc.)
- Bot starts a **coaching flow**:
  1) identifies key pieces (coefficients, denominators, etc.)
  2) asks scaffold questions (one step at a time)
  3) checks each answer and decides the next question
- Student types the **final answer** when ready (e.g., `x = 6`)

**No direct solutions** are shown. The bot keeps the student in "learn-by-doing" mode.

## Supported topics (prototype)
- Linear equations (ax + b = c)
- Addition of fractions (a/b + c/d)
- Quadratic equations ax² + bx + c = 0 (basic)
- Proportions (a:b = c:x)

You can easily add more in `bot/engine/skills.py`.

## Commands
- `/start` — greet + how to use
- `/help` — quick help & tips
- `/new` — start a new problem (resets current session)
- `/hint` — get a gentle hint for the **current step** (no solution spoilers)
- `/giveup` — show method outline (no numeric final answer)
- `/topics` — see supported types & examples

## Local run
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# paste your BOT_TOKEN
python -m bot.main
```

## Docker
```bash
cp .env.example .env && edit BOT_TOKEN=...
docker compose up --build
```

## Structure
```
math-tutor-bot/
├─ bot/
│  ├─ handlers/
│  │  ├─ start.py
│  │  ├─ tutor.py
│  │  └─ misc.py
│  ├─ engine/
│  │  ├─ session.py
│  │  ├─ classify.py
│  │  ├─ skills.py
│  │  └─ utils.py
│  ├─ config.py
│  └─ main.py
├─ requirements.txt
├─ .env.example
├─ Dockerfile
└─ docker-compose.yml
```

## Pedagogy choices
- **Socratic prompts**: always ask the smallest possible next question.
- **Three-tier hints**: nudge → strategy cue → formula reminder; never reveal the numeric result.
- **Error-specific feedback**: if a common mistake is detected, the bot points it out and asks a correcting question.
- **Mastery signals**: once student completes, bot reflects on the strategy used and offers similar practice.

---

### Add a new skill
Create a `Skill` with:
- `match(problem_text) -> score`
- `init(problem_text) -> Step` (first question)
- `next_step(state, user_answer) -> feedback, next Step or Finished`
See `skills.py` for examples.
