"""LLM client: Ollama (default) or OpenAI when OPENAI_API_KEY is set."""

import os
from typing import Any

# Lazy imports so backend starts without langchain if only using /health


def get_llm():
    """Return ChatOllama or ChatOpenAI based on env."""
    if os.getenv("OPENAI_API_KEY"):
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model="gpt-4o-mini", temperature=0)
    from langchain_community.chat_models import ChatOllama
    base_url = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    return ChatOllama(model=os.getenv("OLLAMA_MODEL", "llama3"), base_url=base_url)


def parse_invoice_with_llm(raw_text: str) -> dict[str, Any]:
    """Use LLM to parse raw OCR text into structured invoice JSON."""
    if not raw_text or not raw_text.strip():
        return {"date": None, "amount": None, "vendor": None, "items": []}
    llm = get_llm()
    prompt = """You are an expert at extracting structured data from invoice text.
Extract the following fields from the text below. Respond with valid JSON only, no markdown.
Use this exact structure:
{"date": "YYYY-MM-DD or null", "amount": number or null, "vendor": "string or null", "items": [{"description": "...", "quantity": number, "unit_price": number, "total": number}]}
If a field is not found use null. For date use ISO date. For amount use the total/grand total.
Invoice text:
"""
    prompt += raw_text[:12000]
    import json as _json
    for attempt in range(2):
        try:
            response = llm.invoke(prompt)
            text = response.content if hasattr(response, "content") else str(response)
            text = (text or "").strip()
            if "```" in text:
                start = text.find("{")
                end = text.rfind("}") + 1
                if start >= 0 and end > start:
                    text = text[start:end]
            return _json.loads(text)
        except Exception as e:
            if attempt == 1:
                return {
                    "date": None,
                    "amount": None,
                    "vendor": None,
                    "items": [],
                    "_error": str(e),
                }
    return {"date": None, "amount": None, "vendor": None, "items": []}
