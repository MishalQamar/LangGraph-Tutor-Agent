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


