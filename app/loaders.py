from pathlib import Path
import pandas as pd

DATA_DIR = Path("data")


def load_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_csv_file(path: Path) -> str:
    df = pd.read_csv(path)
    return df.to_csv(index=False)


def load_all_documents():
    documents = []

    for dept_folder in DATA_DIR.iterdir():
        if not dept_folder.is_dir():
            continue

        department = dept_folder.name

        for file_path in dept_folder.iterdir():
            if file_path.suffix.lower() in [".md", ".txt"]:
                content = load_text_file(file_path)
            elif file_path.suffix.lower() == ".csv":
                content = load_csv_file(file_path)
            else:
                continue

            documents.append({
                "content": content,
                "metadata": {
                    "department": department,
                    "source": file_path.name
                }
            })

    return documents