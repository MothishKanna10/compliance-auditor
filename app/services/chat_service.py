from __future__ import annotations

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from app.llm import get_llm
from app.schemas import ChatMessage


async def run_chat(
    report: str,
    messages: list[ChatMessage],
    question: str,
) -> str:
    llm = get_llm()

    system = SystemMessage(content=f"""You are a compliance audit assistant.
A compliance audit was run on a document and produced the following report:

{report}

Answer the user's questions about the findings, regulations, severity, and recommendations.
Only answer based on the report above. If something is not covered in the report, say so.
Keep answers concise and clear.""")

    history = []
    for msg in messages:
        if msg.role == "user":
            history.append(HumanMessage(content=msg.content))
        else:
            history.append(AIMessage(content=msg.content))

    history.append(HumanMessage(content=question))

    response = await llm.ainvoke([system] + history)
    return str(response.content)
