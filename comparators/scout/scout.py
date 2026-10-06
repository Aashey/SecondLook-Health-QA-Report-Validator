from pathlib import Path

from ..semantic import compare_report


REPORT_NAME = "Scout"
PROMPT = Path(__file__).with_name("prompt.txt").read_text(encoding="utf-8").strip()


def compare(question, expected_path, actual_path):
    if not question or not question.strip():
        raise ValueError(
            "Scout comparator requires the original Scout question."
        )

    prompt = "\n".join(
        [
            "SCOUT QUESTION",
            "================",
            question.strip(),
            "",
            PROMPT,
        ]
    )

    return compare_report(
        report_name=REPORT_NAME,
        prompt=prompt,
        expected_path=expected_path,
        actual_path=actual_path,
    )
