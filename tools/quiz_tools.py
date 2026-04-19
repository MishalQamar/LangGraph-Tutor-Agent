from typing import Literal

from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field


class QuizQuestion(BaseModel):
    question: str
    options: list[str] = Field(
        description="Exactly 4 options, each prefixed 'A) ', 'B) ', 'C) ', or 'D) '."
    )
    correct_answer: Literal["A", "B", "C", "D"]
    explanation: str = Field(
        description="Short, student-friendly explanation of why the correct answer is right."
    )


class Quiz(BaseModel):
    topic: str
    difficulty: Literal["easy", "medium", "hard"]
    questions: list[QuizQuestion]


@tool
def generate_quiz(
    research_text: str,
    topic: str,
    difficulty: Literal["easy", "medium", "hard"],
    num_questions: int,
) -> dict:
    """Generate a structured multiple-choice quiz grounded in the provided research text.

    Args:
        research_text: Source material (e.g. web search output) to ground questions in.
        topic: The subject being tested.
        difficulty: "easy", "medium", or "hard".
        num_questions: How many questions to generate (clamped to 1-20).
    """
    num_questions = max(1, min(int(num_questions), 20))

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2).with_structured_output(Quiz)

    prompt = (
        "You are a quiz writer for secondary-school students (ages 13-17). "
        "Using ONLY the facts in the research text, create exactly "
        f"{num_questions} {difficulty}-difficulty multiple-choice questions about '{topic}'. "
        "Rules:\n"
        "- Each question must have exactly 4 options, prefixed 'A) ', 'B) ', 'C) ', 'D) '.\n"
        "- Exactly one option must be clearly correct.\n"
        "- Distractors should be plausible but wrong.\n"
        "- Explanations must be short (1-2 sentences) and age-appropriate.\n"
        "- Avoid trick questions and ambiguous wording.\n\n"
        f"Research text:\n{research_text}"
    )

    quiz = llm.invoke(prompt)
    return quiz.model_dump()
