"""
gemini_client.py
Gemini API interaction functions.
"""

import json
import os
import time
from dotenv import load_dotenv
from google import genai
import streamlit as st
from config import (
    FLASHCARD_PROMPT,
    FLASHCARD_SCHEMA,
    MODEL,
    NOTES_PROMPT,
    NOTES_SCHEMA,
    QUIZ_PROMPT,
    QUIZ_SCHEMA,
)


def get_client():
    """Initializes Gemini API client."""
    load_dotenv()
    key = None
    if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
        key = st.secrets["GEMINI_API_KEY"]
    else:
        key = os.getenv("GEMINI_API_KEY")

    if not key or not str(key).strip():
        return None
    return genai.Client(api_key=str(key).strip())


def video_part(youtube_link: str) -> dict:
    """Builds video item for Gemini input."""
    return {"type": "video", "uri": youtube_link}


def call_gemini(client, contents, log: list, step: str, schema: dict = None):
    """Unified caller for Gemini API with schema support and log tracking."""
    start_time = time.time()

    formatted_contents = []
    if isinstance(contents, list):
        for item in contents:
            if isinstance(item, dict) and item.get("type") == "video":
                from google.genai import types
                formatted_contents.append(
                    types.Part.from_uri(file_uri=item["uri"], mime_type="video/mp4")
                )
            elif isinstance(item, dict) and item.get("type") == "text":
                formatted_contents.append(item.get("text", ""))
            else:
                formatted_contents.append(item)
    else:
        formatted_contents = contents

    config = {}
    if schema is not None:
        config["response_mime_type"] = "application/json"
        config["response_schema"] = schema

    response = client.models.generate_content(
        model=MODEL,
        contents=formatted_contents,
        config=config if config else None
    )

    output_text = response.text
    usage = getattr(response, "usage_metadata", None)
    in_tokens = getattr(usage, "prompt_token_count", 0) if usage else 0
    out_tokens = getattr(usage, "candidates_token_count", 0) if usage else 0

    elapsed = round(time.time() - start_time, 2)

    log.append({
        "step": step,
        "seconds": elapsed,
        "input_tokens": in_tokens,
        "output_tokens": out_tokens
    })

    return json.loads(output_text) if schema is not None else output_text


def extract_notes(client, youtube_link: str, level: str, language: str, log: list) -> dict:
    prompt = NOTES_PROMPT.format(level=level, language=language)
    input_contents = [video_part(youtube_link), {"type": "text", "text": prompt}]
    return call_gemini(client, input_contents, log, "notes", NOTES_SCHEMA)


def make_flashcards(client, notes: dict, count: int, language: str, log: list) -> list:
    notes_json = json.dumps(notes, indent=2)
    prompt = FLASHCARD_PROMPT.format(count=count, language=language, notes=notes_json)
    result = call_gemini(client, prompt, log, "flashcards", FLASHCARD_SCHEMA)
    return result.get("cards", [])


def make_quiz(client, notes: dict, count: int, language: str, log: list) -> list:
    notes_json = json.dumps(notes, indent=2)
    prompt = QUIZ_PROMPT.format(count=count, language=language, notes=notes_json)
    result = call_gemini(client, prompt, log, "quiz", QUIZ_SCHEMA)
    return result.get("questions", [])
