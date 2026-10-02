import shutil
import subprocess
import sys
from pathlib import Path

from comparators.medical_timeline import compare as compare_timeline
from comparators.soc import compare as compare_soc
from comparators.clinical_summary import compare as compare_clinical_summary
from comparators.case_management import compare as compare_case_management
from comparators.scout import compare as compare_scout


BASE_DIR = Path(__file__).resolve().parent


COMPARATORS = {
    "timeline": (
        "Medical Timeline",
        "medical_timeline",
        compare_timeline,
    ),
    "medical_timeline": (
        "Medical Timeline",
        "medical_timeline",
        compare_timeline,
    ),
    "soc": (
        "SoC",
        "soc",
        compare_soc,
    ),
    "clinical_summary": (
        "Clinical Summary",
        "clinical_summary",
        compare_clinical_summary,
    ),
    "case_management": (
        "Case Management",
        "case_management",
        compare_case_management,
    ),
    "scout": (
        "Scout",
        "scout",
        compare_scout,
    ),
}


def run_claude(prompt):
    claude_path = shutil.which("claude")

    if claude_path is None:
        raise RuntimeError(
            "Claude Code CLI was not found. "
            "Make sure `claude` works in PowerShell."
        )

    command = [claude_path, "-p"]

    use_shell = (
        sys.platform == "win32"
        and Path(claude_path).suffix.lower() in {".cmd", ".bat"}
    )

    if use_shell:
        command = f'"{claude_path}" -p'

    try:
        result = subprocess.run(
            command,
            input=prompt,
            text=True,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            shell=use_shell,
        )
    except FileNotFoundError:
        raise RuntimeError(
            "Claude Code CLI was not found. "
            "Make sure `claude` works in PowerShell."
        )

    if result.returncode != 0:
        error = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"Claude Code failed:\n{error}")

    output = result.stdout.strip()

    if not output:
        raise RuntimeError("Claude Code returned an empty response.")

    return output


def next_report_path(report_dir, folder_name):
    report_number = 1

    while True:
        output_path = report_dir / (
            f"{folder_name}-comparison{report_number}.md"
        )
        if not output_path.exists():
            return output_path
        report_number += 1


def main():
    if len(sys.argv) != 2:
        print("Usage:")
        print("  python run_comparator.py timeline")
        print("  python run_comparator.py soc")
        print("  python run_comparator.py clinical_summary")
        print("  python run_comparator.py case_management")
        print("  python run_comparator.py scout")
        sys.exit(1)

    report_type = sys.argv[1].lower()

    if report_type not in COMPARATORS:
        print(f"Unknown comparator: {report_type}")
        print(
            "Available: timeline, soc, clinical_summary, "
            "case_management, scout"
        )
        sys.exit(1)

    report_name, folder_name, comparator = COMPARATORS[report_type]

    report_dir = BASE_DIR / folder_name

    expected_path = report_dir / "json1.json"
    actual_path = report_dir / "json2.json"

    if not expected_path.exists():
        print(f"ERROR: Expected JSON not found: {expected_path}")
        sys.exit(1)

    if not actual_path.exists():
        print(f"ERROR: Actual JSON not found: {actual_path}")
        sys.exit(1)

    # Scout requires the original question.
    question = None

    if report_type == "scout":
        question_path = report_dir / "question.txt"

        if not question_path.exists():
            print(f"ERROR: Scout question not found: {question_path}")
            print(
                "Create scout/question.txt containing the exact "
                "question asked to Scout."
            )
            sys.exit(1)

        question = question_path.read_text(
            encoding="utf-8"
        ).strip()

        if not question:
            print(f"ERROR: Scout question file is empty: {question_path}")
            sys.exit(1)

    print(f"Running {report_name} comparison...")
    
    if report_type == "scout":
        print(f"Question: {question}")

    print(f"Expected: {expected_path}")
    print(f"Actual:   {actual_path}")
    print()

    try:
        # Scout is the only comparator that requires an additional
        # question/context argument.
        if report_type == "scout":
            prompt = comparator(
                question,
                expected_path,
                actual_path,
            )
        else:
            prompt = comparator(
                expected_path,
                actual_path,
            )

        print("Sending comparison to Claude Code...")

        result = run_claude(prompt)

        output_path = next_report_path(report_dir, folder_name)

        output_path.write_text(
            result + "\n",
            encoding="utf-8",
        )

        print()
        print("Claude evaluation complete.")
        print(f"Report saved: {output_path}")

    except Exception as exc:
        print()
        print(f"ERROR: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()