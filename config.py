"""
config.py
Constants, prompts, and JSON schemas for LectureLab.
"""

MODEL = "gemini-2.5-flash"

LANGUAGES = ["English", "Hindi", "Hinglish"]
LEVELS = ["Beginner", "Intermediate", "Advanced"]

NOTES_PROMPT = """You are an expert educational content creator and academic note-taker.
Watch the provided lecture video thoroughly, analyzing both spoken audio and visual content (slides, code, diagrams, whiteboard).

Generate detailed study notes tailored for a {level} student level in {language}.

Requirements:
1. Provide a concise overall summary of the lecture.
2. Divide the video into chronological chapters with real start times (MM:SS or HH:MM:SS), headings, and 3-6 short key points.
3. Extract key terms with concise one-line definitions.
4. Include strictly what is in the video.
"""

FLASHCARD_PROMPT = """Create a deck of {count} revision flashcards based on the provided lecture notes.
Language: {language}

Requirements:
- Front: A short, clear question or concept prompt.
- Back: A concise 1-2 sentence direct answer.

Lecture Notes:
{notes}
"""

QUIZ_PROMPT = """Create an auto-gradable practice quiz with {count} multiple-choice questions based on the provided lecture notes.
Language: {language}

Requirements:
1. Exactly 4 plausible options per question.
2. 0-based index (0, 1, 2, or 3) for correct_index.
3. Realistic wrong choices (distractors).
4. Concise 1-2 sentence explanation.

Lecture Notes:
{notes}
"""

NOTES_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "summary": {"type": "string"},
        "chapters": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "start": {"type": "string"},
                    "heading": {"type": "string"},
                    "key_points": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["start", "heading", "key_points"]
            }
        },
        "key_terms": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "term": {"type": "string"},
                    "definition": {"type": "string"}
                },
                "required": ["term", "definition"]
            }
        }
    },
    "required": ["title", "summary", "chapters", "key_terms"]
}

FLASHCARD_SCHEMA = {
    "type": "object",
    "properties": {
        "cards": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "front": {"type": "string"},
                    "back": {"type": "string"}
                },
                "required": ["front", "back"]
            }
        }
    },
    "required": ["cards"]
}

QUIZ_SCHEMA = {
    "type": "object",
    "properties": {
        "questions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "question": {"type": "string"},
                    "options": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "correct_index": {"type": "integer"},
                    "explanation": {"type": "string"}
                },
                "required": ["question", "options", "correct_index", "explanation"]
            }
        }
    },
    "required": ["questions"]
}
