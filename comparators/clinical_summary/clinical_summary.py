from pathlib import Path

from ..semantic import compare_report


REPORT_NAME = 'Clinical Summary'
PROMPT = Path(__file__).with_name("prompt.txt").read_text(encoding="utf-8").strip()


def compare(expected_path, actual_path):
    return compare_report(
        report_name=REPORT_NAME,
        prompt=PROMPT,
        expected_path=expected_path,
        actual_path=actual_path,
    )
