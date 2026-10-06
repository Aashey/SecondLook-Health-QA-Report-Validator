import shutil
import subprocess
import sys
from pathlib import Path

from comparators.medical_timeline import compare as compare_timeline
from comparators.soc import compare as compare_soc
from comparators.clinical_summary import compare as compare_clinical_summary
from comparators.case_management import compare as compare_case_management
from comparators.scout import compare as compare_scout
from comparators.segments import compare as compare_segments

from source_judge import build_source_validation


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

    "segments": (
        "Segments",
        "segments",
        compare_segments,
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

        raise RuntimeError(
            f"Claude Code failed:\n{error}"
        )

    output = result.stdout.strip()

    if not output:
        raise RuntimeError(
            "Claude Code returned an empty response."
        )

    return output


def next_report_path(reports_dir, report_type):
    report_number = 1

    while True:
        output_dir = (
            reports_dir
            / report_type
            / str(report_number)
        )

        if not output_dir.exists():
            output_dir.mkdir(
                parents=True,
                exist_ok=True,
            )

            return output_dir / "comparison.md"

        report_number += 1


def main():

    if len(sys.argv) != 2:
        print("Usage:")
        print("  python run_comparator.py timeline")
        print("  python run_comparator.py soc")
        print("  python run_comparator.py clinical_summary")
        print("  python run_comparator.py case_management")
        print("  python run_comparator.py scout")
        print("  python run_comparator.py segments")
        sys.exit(1)

    report_type = sys.argv[1].lower()

    if report_type not in COMPARATORS:
        print(f"Unknown comparator: {report_type}")

        print(
            "Available: timeline, soc, clinical_summary, "
            "case_management, scout, segments"
        )

        sys.exit(1)

    report_name, folder_name, comparator = COMPARATORS[
        report_type
    ]

    report_dir = BASE_DIR / folder_name

    expected_path = report_dir / "json1.json"
    actual_path = report_dir / "json2.json"

    if not expected_path.exists():
        print(
            f"ERROR: Expected JSON not found: "
            f"{expected_path}"
        )
        sys.exit(1)

    if not actual_path.exists():
        print(
            f"ERROR: Actual JSON not found: "
            f"{actual_path}"
        )
        sys.exit(1)

    # ----------------------------------------------------------
    # Scout requires the original question.
    # ----------------------------------------------------------

    question = None

    if report_type == "scout":

        question_path = report_dir / "question.txt"

        if not question_path.exists():
            print(
                f"ERROR: Scout question not found: "
                f"{question_path}"
            )

            print(
                "Create scout/question.txt containing the "
                "exact question asked to Scout."
            )

            sys.exit(1)

        question = question_path.read_text(
            encoding="utf-8"
        ).strip()

        if not question:
            print(
                f"ERROR: Scout question file is empty: "
                f"{question_path}"
            )
            sys.exit(1)

    # ----------------------------------------------------------
    # Start
    # ----------------------------------------------------------

    print(
        f"Running {report_name} comparison..."
    )

    if report_type == "scout":
        print(f"Question: {question}")

    print(f"Expected: {expected_path}")
    print(f"Actual:   {actual_path}")
    print()

    try:

        # ======================================================
        # STAGE 1
        # JSON1 vs JSON2 comparison
        # ======================================================

        if report_type == "scout":

            comparison_prompt = comparator(
                question,
                expected_path,
                actual_path,
            )

        else:

            comparison_prompt = comparator(
                expected_path,
                actual_path,
            )

        print(
            "Sending comparison to Claude Code..."
        )

        comparison_result = run_claude(
            comparison_prompt
        )

        print(
            "Initial comparison complete."
        )

        # ======================================================
        # SEGMENTS
        #
        # Segments do NOT use source.json.
        #
        # They only need:
        #
        # JSON1 → JSON2 → comparator → Claude → report
        #
        # No source validation.
        # ======================================================

        if report_type == "segments":

            output_path = next_report_path(
                BASE_DIR / "reports",
                folder_name,
            )

            output = (
                "# QA Report\n\n"
                "## JSON1 vs JSON2 Comparison\n\n"
                f"{comparison_result}\n"
            )

            output_path.write_text(
                output,
                encoding="utf-8",
            )

            print()
            print(
                "QA evaluation complete."
            )

            print(
                f"Report saved: {output_path}"
            )

            return

        # ======================================================
        # STAGE 2
        # Source-grounded validation
        #
        # Only non-segment comparators reach this section.
        # ======================================================

        print(
            "Searching source.json for relevant evidence..."
        )

        source_prompt, source_chunks = (
            build_source_validation(
                report_type=report_type,
                expected_path=expected_path,
                actual_path=actual_path,
                comparison=comparison_result,
                question=question,
                top_k=8,
            )
        )

        print(
            f"Retrieved {len(source_chunks)} "
            "relevant source chunks."
        )

        if source_chunks:

            print("Source evidence:")

            for chunk in source_chunks:

                print(
                    f"  - {chunk['file_name']} "
                    f"(PDF page {chunk['page_number']}, "
                    f"{chunk['chunk_id']})"
                )

        print()

        print(
            "Sending source-grounded validation to Claude Code..."
        )

        final_result = run_claude(
            source_prompt
        )

        # ======================================================
        # SAVE SOURCE-GROUNDED REPORT
        # ======================================================

        output_path = next_report_path(
            BASE_DIR / "reports",
            folder_name,
        )

        output = (
            "# Source-Grounded QA Report\n\n"
            "## Initial JSON1 vs JSON2 Comparison\n\n"
            f"{comparison_result}\n\n"
            "---\n\n"
            "## Source-Grounded Validation\n\n"
            f"{final_result}\n"
        )

        output_path.write_text(
            output,
            encoding="utf-8",
        )

        print()
        print(
            "Source-grounded QA evaluation complete."
        )

        print(
            f"Report saved: {output_path}"
        )

    except Exception as exc:

        print()
        print(f"ERROR: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()