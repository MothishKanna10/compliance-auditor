from __future__ import annotations

from typing import TypedDict

from app.llm import get_llm


class ChatMessage(TypedDict):
    role: str
    content: str


def build_compliance_chat_prompt(
    question: str,
    regulatory_context: str,
    chat_history: list[ChatMessage],
    latest_audit_result: str | None,
) -> str:
    history_text = "\n".join(
        f"{message['role'].upper()}: {message['content']}"
        for message in chat_history[-8:]
    )

    audit_context = latest_audit_result or "No uploaded document audit has been run yet."

    return f"""
You are an Australian Compliance Assistant.

You help users understand Australian privacy and complaints compliance.

Use ONLY:
1. The supplied regulatory context.
2. The latest audit result if available.
3. The conversation history.

Do NOT invent laws, penalties, or obligations.

If the user asks about their uploaded document, answer using the latest audit result.
If the user asks about regulations, answer using the regulatory context.

CONVERSATION HISTORY:
{history_text}

LATEST AUDIT RESULT:
{audit_context}

REGULATORY CONTEXT:
{regulatory_context}

USER QUESTION:
{question}

Return a clear, practical answer.
"""


def generate_compliance_chat_response(
    question: str,
    regulatory_context: str,
    chat_history: list[ChatMessage],
    latest_audit_result: str | None,
) -> str:
    llm = get_llm()

    prompt = build_compliance_chat_prompt(
        question=question,
        regulatory_context=regulatory_context,
        chat_history=chat_history,
        latest_audit_result=latest_audit_result,
    )

    response = llm.invoke(prompt)

    return str(response.content)