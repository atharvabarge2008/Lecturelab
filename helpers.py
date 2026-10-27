"""
helpers.py
Utility functions for validation, grading, error handling, and usage tracking.
"""


def youtube_id(url: str):
    """Extracts unique 11-character video ID from YouTube URL formats."""
    if not url or not isinstance(url, str):
        return None

    cleaned = url.strip()
    markers = ["watch?v=", "youtu.be/", "/shorts/"]

    found_marker = None
    for m in markers:
        if m in cleaned:
            found_marker = m
            break

    if not found_marker:
        return None

    parts = cleaned.split(found_marker)
    if len(parts) < 2:
        return None

    candidate = parts[1][:11]
    return candidate if len(candidate) == 11 else None


def validate_quiz(questions: list):
    """Filters out broken or invalid AI quiz questions."""
    good_questions = []
    problems = []

    if not isinstance(questions, list):
        return (good_questions, ["Quiz response was not a valid list."])

    for i, q in enumerate(questions, start=1):
        if not isinstance(q, dict):
            problems.append(f"Q{i}: Question payload is invalid.")
            continue

        options = q.get("options", [])
        if not isinstance(options, list) or len(options) != 4:
            problems.append(f"Q{i}: has {len(options) if isinstance(options, list) else 0} options (expected 4)")
            continue

        correct_idx = q.get("correct_index")
        if not isinstance(correct_idx, int) or correct_idx not in [0, 1, 2, 3]:
            problems.append(f"Q{i}: correct_index {correct_idx} is out of range")
            continue

        normalized = [str(opt).strip().lower() for opt in options]
        if len(set(normalized)) < 4:
            problems.append(f"Q{i}: duplicate options")
            continue

        good_questions.append(q)

    return (good_questions, problems)


def grade_quiz(questions: list, answers: list):
    """Grades user answers against answer keys."""
    score = 0
    results = []

    for q, chosen in zip(questions, answers):
        correct_idx = q["correct_index"]
        correct_answer = q["options"][correct_idx]

        is_correct = (chosen == correct_answer)
        if is_correct:
            score += 1

        results.append({
            "chosen": chosen,
            "correct": correct_answer,
            "is_correct": is_correct
        })

    return (score, results)


def friendly_error(error: Exception) -> str:
    """Converts raw errors to user-friendly messages."""
    err_text = str(error).lower()

    if any(term in err_text for term in ["429", "quota", "resource_exhausted"]):
        return "Too many requests. Wait a minute and try again."

    if any(term in err_text for term in ["private", "unlisted", "permission", "not found", "400"]):
        return "Couldn't read this video. Make sure it's a public YouTube video."

    return f"Something went wrong: {error}"


def summarize_log(log: list):
    """Aggregates total API usage metrics."""
    if not log:
        return (0, 0, 0.0)

    total_calls = len(log)
    total_tokens = sum(entry.get("input_tokens", 0) + entry.get("output_tokens", 0) for entry in log)
    total_seconds = round(sum(entry.get("seconds", 0.0) for entry in log), 1)

    return (total_calls, total_tokens, total_seconds)
