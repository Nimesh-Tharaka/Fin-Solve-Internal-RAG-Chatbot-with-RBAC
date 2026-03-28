BLOCKED_PATTERNS = [
    "ignore previous instructions",
    "ignore all instructions",
    "bypass role",
    "bypass rbac",
    "show confidential data",
    "reveal hidden data",
    "show all documents",
    "give me everything",
    "override access control",
]

OUT_OF_SCOPE_HINTS = [
    "cricket",
    "football",
    "weather",
    "movie",
    "song",
    "celebrity",
    "capital of",
    "who won",
]


def check_guardrails(question: str):
    q = question.lower().strip()

    for pattern in BLOCKED_PATTERNS:
        if pattern in q:
            return {
                "blocked": True,
                "reason": "Security policy violation detected."
            }

    for pattern in OUT_OF_SCOPE_HINTS:
        if pattern in q:
            return {
                "blocked": True,
                "reason": "Out-of-scope question. This assistant only answers FinSolve internal document questions."
            }

    return {
        "blocked": False,
        "reason": None
    }