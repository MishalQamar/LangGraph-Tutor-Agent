# LangGraph Tutor Agent

A multi-agent **study buddy for secondary-school students (ages 13-17)** built on
[LangGraph](https://github.com/langchain-ai/langgraph) and
[`langgraph-swarm`](https://github.com/langchain-ai/langgraph-swarm).

## What it does

A small swarm of specialised agents hand off to each other based on what the
student needs:

| Agent                  | Role                                                                |
| ---------------------- | ------------------------------------------------------------------- |
| `classification_agent` | Intake. Figures out the subject + goal in 1-2 short questions.      |
| `teacher_agent`        | Explains topics one small step at a time with school-life examples. |
| `quiz_agent`           | Researches the topic, builds a short MCQ quiz, gives feedback.      |
| `feynman_agent`        | Makes the student prove understanding by explaining in plain words. |

Conversation starts with `classification_agent`; it transfers to a specialist,
and specialists can transfer to each other as the session evolves.

## Requirements

- Python **3.13+**
- [`uv`](https://docs.astral.sh/uv/) (recommended) or pip
- API keys:
  - `OPENAI_API_KEY` - for the agent LLMs and quiz generation
  - `FIRECRAWL_API_KEY` - for `web_search_tool`

## Setup

```bash
git clone <this repo>
cd LangGraph-Tutor-Agent

uv sync

cp .env.example .env   # or create .env manually, see below
```

Create a `.env` file at the project root:

```env
OPENAI_API_KEY=sk-...
FIRECRAWL_API_KEY=fc-...
```

## Run

### Option 1 — LangGraph Studio (recommended for development)

```bash
uv run langgraph dev
```

Opens LangGraph Studio in the browser; the graph is exported as `tutor` in
`langgraph.json`.

### Option 2 — Local CLI chat

```bash
uv run python main.py
```

This uses a local SQLite checkpointer so conversations persist across runs.

- `TUTOR_DB` (default `tutor_state.sqlite`) — path to the checkpoint DB.
- `TUTOR_THREAD` — thread id to resume; set this to the id printed on first run
  to continue a previous session.

Type `exit` (or Ctrl-D) to quit.

## Project layout

```
.
├── main.py                       # swarm graph + CLI REPL
├── langgraph.json                # LangGraph CLI config
├── agents/
│   ├── classification_agent.py   # intake + routing
│   ├── teacher_agent.py          # explanations
│   ├── quiz_agent.py             # quizzes
│   └── feynman_agent.py          # explain-it-back
└── tools/
    ├── shared_tools.py           # web_search_tool (Firecrawl)
    └── quiz_tools.py             # generate_quiz (structured output)
```

## Design notes

- **Swarm, not supervisor.** Agents stay active across multiple user turns and
  hand off peer-to-peer via `langgraph_swarm.create_handoff_tool`. This keeps
  conversations contextual and avoids an extra LLM call per turn.
- **Named nodes.** Every agent is registered with an explicit `name=` so
  handoff tool names (`transfer_to_teacher_agent`, etc.) resolve to real nodes.
- **Grounded quizzes.** `quiz_agent` must call `web_search_tool` before
  `generate_quiz`, and `generate_quiz` uses structured output (Pydantic) so the
  quiz shape is enforced.
- **Homework honesty.** The teacher prompt forbids giving final answers to
  pasted homework problems; it guides the student to the next step instead.

## Next steps (roadmap)

- [ ] Homework Helper agent with explicit scaffolding rules.
- [ ] Subject presets (Math / Science / English / History / CS) with tailored
      examples and notation.
- [ ] Session recap at the end of each thread (persisted via checkpointer).
- [ ] Lightweight per-topic confidence tracking.
- [ ] Guardrails for off-topic / distress language.
