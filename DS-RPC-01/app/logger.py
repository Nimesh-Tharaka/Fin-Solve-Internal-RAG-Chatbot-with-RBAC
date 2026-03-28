import csv
import os
from datetime import datetime

LOG_FILE = "chat_logs.csv"


def log_chat(username: str, role: str, question: str, answer: str, sources: list, status: str):
    file_exists = os.path.exists(LOG_FILE)

    with open(LOG_FILE, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow([
                "timestamp",
                "username",
                "role",
                "question",
                "answer",
                "sources",
                "status"
            ])

        writer.writerow([
            datetime.now().isoformat(),
            username,
            role,
            question,
            answer,
            ", ".join(sources),
            status
        ])