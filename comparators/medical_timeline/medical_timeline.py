import json
from pathlib import Path


REPORT_NAME = "Medical Timeline"
PROMPT = Path(__file__).with_name("prompt.txt").read_text(encoding="utf-8").strip()


def load_json(path):
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    try:
        with path.open("r", encoding="utf-8-sig") as file:
            return json.load(file)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {path}: {exc}") from exc


def extract_timeline(data):
    value = data.get("value", {})
    dated = value.get("dated", [])
    undated = value.get("undated", [])

    def simplify(item, classification):
        summary = item.get("Summary", "")
        synopsis = ""

        if isinstance(summary, str) and "4.**Synopsis:**" in summary:
            synopsis = summary.split("4.**Synopsis:**", 1)[1].strip()

        return {
            "classification": classification,
            "event": item.get("Event", ""),
            "date": item.get("Date", ""),
            "title": item.get("Title", ""),
            "category": item.get("Category", ""),
            "synopsis": synopsis,
        }

    return {
        "dated": [simplify(item, "dated") for item in dated],
        "undated": [simplify(item, "undated") for item in undated],
    }

def compare(expected_path, actual_path):
    expected_raw = load_json(expected_path)
    actual_raw = load_json(actual_path)

    expected = extract_timeline(expected_raw)
    actual = extract_timeline(actual_raw)

    return (
        PROMPT.replace(
            "{{EXPECTED_TIMELINE}}",
            json.dumps(expected, indent=2, ensure_ascii=False),
        )
        .replace(
            "{{ACTUAL_TIMELINE}}",
            json.dumps(actual, indent=2, ensure_ascii=False),
        )
        .strip()
    )
