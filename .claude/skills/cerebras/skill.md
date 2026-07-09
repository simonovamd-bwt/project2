---
name: cerebras
description: Cerebras inference. Use this to write code to call an LLM using LiteLLM and OpenRouter with the Cerebras inference provider. Triggers — "call an LLM", "cerebras", "openrouter", "gpt-oss", "structured output", "fast inference".
---

# Calling an LLM via Cerebras

These instructions let you write code to call an LLM with **Cerebras** specified
as the inference provider, through **OpenRouter** using **LiteLLM**. Cerebras is
chosen for speed: responses come back fast enough that streaming is unnecessary
— a single non-streaming call returns the whole answer at once.

## Setup

- Model: `openrouter/openai/gpt-oss-120b` (the open-source GPT-OSS 120B model).
- Provider routing: force **Cerebras** as the inference provider via OpenRouter's
  `provider` routing in `extra_body`.
- Auth: `OPENROUTER_API_KEY` from the `.env` file in the project root.
- No streaming. For structured document fields we want one call that returns the
  full result, so we can parse it and populate the legal document.

## Imports and constants

```python
import os

import litellm

MODEL = "openrouter/openai/gpt-oss-120b"

# Route the request through Cerebras specifically. OpenRouter would otherwise
# pick any provider that serves this model; we want Cerebras for its speed.
CEREBRAS_ROUTING = {"provider": {"order": ["Cerebras"], "allow_fallbacks": False}}

# LiteLLM reads OPENROUTER_API_KEY from the environment (loaded from .env).
```

## Code to call Cerebras

```python
def call_llm(system: str, user: str) -> str:
    """One non-streaming call to gpt-oss-120b via OpenRouter → Cerebras."""
    response = litellm.completion(
        model=MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        stream=False,
        extra_body=CEREBRAS_ROUTING,
    )
    return response.choices[0].message.content
```

## Code to call Cerebras for structured outputs

Ask for a JSON object matching a schema, so the reply can be parsed straight into
the document's fields. `response_format` with a JSON schema keeps the model on
contract; `extra_body` still forces Cerebras.

```python
import json


def call_llm_structured(system: str, user: str, schema: dict) -> dict:
    """Return a validated dict of extracted fields in a single Cerebras call.

    `schema` is a JSON Schema describing the fields to extract (e.g. the
    document's placeholder fields). The reply is JSON, ready to populate the
    legal document.
    """
    response = litellm.completion(
        model=MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        stream=False,
        response_format={
            "type": "json_schema",
            "json_schema": {"name": "document_fields", "schema": schema},
        },
        extra_body=CEREBRAS_ROUTING,
    )
    return json.loads(response.choices[0].message.content)
```

## Example

```python
schema = {
    "type": "object",
    "properties": {
        "reply": {"type": "string"},
        "disclosing_party": {"type": "string"},
        "receiving_party": {"type": "string"},
        "purpose": {"type": "string"},
        "term_months": {"type": "string"},
    },
    "required": ["reply"],
}

result = call_llm_structured(
    system="You are a legal drafting assistant. Ask one question at a time and "
    "extract any answers into the provided fields.",
    user="The disclosing party is Acme Inc.",
    schema=schema,
)
# result["reply"]  -> the chat text to show the user
# result["disclosing_party"] -> "Acme Inc"  (populate the document)
```

## Notes

- Keep it non-streaming: Cerebras is fast enough that the first chunk is
  effectively the whole answer.
- One structured call returns both the chat reply and the extracted fields, so
  the frontend can drive the conversation and the live preview from one response.
- If `OPENROUTER_API_KEY` is missing, fail clearly rather than silently — the
  caller should know the key must be set in `.env`.
