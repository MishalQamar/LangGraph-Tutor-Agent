"""Entry point for the secondary-school study-buddy swarm.

Exports `graph` for langgraph-cli (`langgraph dev` picks it up via langgraph.json).
Running this file directly (`python main.py`) launches a simple REPL that persists
conversation state to a local SQLite file via the langgraph SQLite checkpointer.
"""

from __future__ import annotations

import os
import uuid

from dotenv import load_dotenv
from langgraph_swarm import create_swarm

from agents.classification_agent import classification_agent
from agents.feynman_agent import feynman_agent
from agents.quiz_agent import quiz_agent
from agents.teacher_agent import teacher_agent

load_dotenv()


def _build_workflow():
    """Build (but do not compile) the swarm workflow."""
    return create_swarm(
        agents=[classification_agent, teacher_agent, quiz_agent, feynman_agent],
        default_active_agent="classification_agent",
    )


graph = _build_workflow().compile()
graph.name = "tutor"


def _repl() -> None:
    """Minimal CLI chat loop with persistent SQLite checkpointing."""
    from langgraph.checkpoint.sqlite import SqliteSaver

    db_path = os.getenv("TUTOR_DB", "tutor_state.sqlite")
    thread_id = os.getenv("TUTOR_THREAD", str(uuid.uuid4()))

    print(f"[tutor] using checkpoint DB: {db_path}")
    print(f"[tutor] thread id: {thread_id}  (set TUTOR_THREAD to resume)")
    print("[tutor] type 'exit' to quit.\n")

    with SqliteSaver.from_conn_string(db_path) as checkpointer:
        app = _build_workflow().compile(checkpointer=checkpointer)
        config = {"configurable": {"thread_id": thread_id}}

        while True:
            try:
                user = input("you > ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break
            if not user:
                continue
            if user.lower() in {"exit", "quit", ":q"}:
                break

            result = app.invoke(
                {"messages": [{"role": "user", "content": user}]},
                config=config,
            )
            last = result["messages"][-1]
            speaker = getattr(last, "name", None) or "tutor"
            print(f"{speaker} > {getattr(last, 'content', last)}\n")


if __name__ == "__main__":
    _repl()
