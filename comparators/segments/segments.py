import json
from pathlib import Path


PROMPT = Path(__file__).with_name("prompt.txt").read_text(
    encoding="utf-8"
).strip()


COMPARE_FIELDS = [
    "event_date",
    "event",
    "facility",
    "provider",
]


def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def normalize(value):
    if value is None:
        return None

    if isinstance(value, str):
        value = value.strip().lower()
        return value if value else None

    return value


def logical_match(expected, actual):
    """
    Determine whether two segments represent
    the same logical event.

    Page numbers are intentionally ignored here.
    """

    for field in COMPARE_FIELDS:
        if normalize(expected.get(field)) != normalize(
            actual.get(field)
        ):
            return False

    return True


def page_range(segment):
    start = segment.get("start_page")
    end = segment.get("end_page")

    if start is None or end is None:
        return None

    return int(start), int(end)


def ranges_overlap(range1, range2):
    if not range1 or not range2:
        return False

    start1, end1 = range1
    start2, end2 = range2

    return max(start1, start2) <= min(end1, end2)


def ranges_touch(range1, range2):
    if not range1 or not range2:
        return False

    start1, end1 = range1
    start2, end2 = range2

    return (
        end1 + 1 >= start2
        and end2 + 1 >= start1
    )


def format_range(segment):
    start = segment.get("start_page")
    end = segment.get("end_page")

    if start is None and end is None:
        return "unknown"

    if start == end:
        return str(start)

    return f"{start}-{end}"


def format_segment(segment):
    return (
        f"event={segment.get('event')!r}, "
        f"date={segment.get('event_date')!r}, "
        f"facility={segment.get('facility')!r}, "
        f"provider={segment.get('provider')!r}, "
        f"pages={format_range(segment)}"
    )


def find_logical_matches(expected, actual):
    """
    Match segments based on logical identity rather than
    array position.

    If multiple logical matches exist, prefer the one
    whose page range overlaps the expected segment.
    """

    matches = []
    used_actual = set()

    for expected_index, expected_segment in enumerate(
        expected
    ):
        candidates = []

        for actual_index, actual_segment in enumerate(
            actual
        ):
            if actual_index in used_actual:
                continue

            if logical_match(
                expected_segment,
                actual_segment,
            ):
                candidates.append(
                    (
                        actual_index,
                        actual_segment,
                    )
                )

        if not candidates:
            continue

        expected_range = page_range(
            expected_segment
        )

        overlapping = [
            candidate
            for candidate in candidates
            if ranges_overlap(
                expected_range,
                page_range(candidate[1]),
            )
        ]

        if overlapping:
            selected = overlapping[0]
        else:
            selected = candidates[0]

        actual_index, actual_segment = selected

        matches.append(
            {
                "expected_index": expected_index,
                "actual_index": actual_index,
                "expected": expected_segment,
                "actual": actual_segment,
            }
        )

        used_actual.add(actual_index)

    return matches


def detect_splits(expected, actual):
    """
    Detect when one expected logical segment appears
    as multiple actual segments.

    Example:

    Expected:
        Event A | pages 1-2

    Actual:
        Event A | pages 1-1
        Event A | pages 2-2
    """

    findings = []
    used_actual_indices = set()

    for expected_index, expected_segment in enumerate(
        expected
    ):
        expected_range = page_range(
            expected_segment
        )

        candidates = []

        for actual_index, actual_segment in enumerate(
            actual
        ):
            if not logical_match(
                expected_segment,
                actual_segment,
            ):
                continue

            actual_range = page_range(
                actual_segment
            )

            if not actual_range:
                continue

            if (
                ranges_overlap(
                    expected_range,
                    actual_range,
                )
                or ranges_touch(
                    expected_range,
                    actual_range,
                )
            ):
                candidates.append(
                    (
                        actual_index,
                        actual_segment,
                    )
                )

        if len(candidates) > 1:
            for actual_index, _ in candidates:
                used_actual_indices.add(
                    actual_index
                )

            findings.append(
                {
                    "expected_index": expected_index,
                    "expected": expected_segment,
                    "actual_segments": [
                        segment
                        for _, segment in candidates
                    ],
                }
            )

    return findings, used_actual_indices


def detect_merges(expected, actual):
    """
    Detect when multiple expected segments appear
    to have been combined into one actual segment.
    """

    findings = []
    used_expected_indices = set()

    for actual_index, actual_segment in enumerate(
        actual
    ):
        candidates = []

        for expected_index, expected_segment in enumerate(
            expected
        ):
            if not logical_match(
                expected_segment,
                actual_segment,
            ):
                continue

            expected_range = page_range(
                expected_segment
            )

            actual_range = page_range(
                actual_segment
            )

            if not expected_range or not actual_range:
                continue

            if (
                ranges_overlap(
                    expected_range,
                    actual_range,
                )
                or ranges_touch(
                    expected_range,
                    actual_range,
                )
            ):
                candidates.append(
                    (
                        expected_index,
                        expected_segment,
                    )
                )

        if len(candidates) > 1:
            for expected_index, _ in candidates:
                used_expected_indices.add(
                    expected_index
                )

            findings.append(
                {
                    "actual_index": actual_index,
                    "actual": actual_segment,
                    "expected_segments": [
                        segment
                        for _, segment in candidates
                    ],
                }
            )

    return findings, used_expected_indices


def compare_file_segments(
    file_name,
    expected,
    actual,
):
    """
    Compare segments for one specific PDF file.
    """

    findings = []

    expected_count = len(expected)
    actual_count = len(actual)

    matches = find_logical_matches(
        expected,
        actual,
    )

    matched_expected = {
        match["expected_index"]
        for match in matches
    }

    matched_actual = {
        match["actual_index"]
        for match in matches
    }

    # ---------------------------------------------------------
    # Page-boundary differences
    # ---------------------------------------------------------

    for match in matches:
        expected_segment = match["expected"]
        actual_segment = match["actual"]

        expected_range = page_range(
            expected_segment
        )

        actual_range = page_range(
            actual_segment
        )

        if expected_range != actual_range:

            if ranges_overlap(
                expected_range,
                actual_range,
            ):
                findings.append(
                    {
                        "type": "PAGE_BOUNDARY_VARIATION",
                        "expected": expected_segment,
                        "actual": actual_segment,
                    }
                )
            else:
                findings.append(
                    {
                        "type": "PAGE_RANGE_DIFFERENCE",
                        "expected": expected_segment,
                        "actual": actual_segment,
                    }
                )

    # ---------------------------------------------------------
    # Possible splits
    # ---------------------------------------------------------

    split_findings, split_actual_indices = (
        detect_splits(
            expected,
            actual,
        )
    )

    for finding in split_findings:
        findings.append(
            {
                "type": "POSSIBLE_SPLIT",
                **finding,
            }
        )

    # ---------------------------------------------------------
    # Possible merges
    # ---------------------------------------------------------

    merge_findings, merge_expected_indices = (
        detect_merges(
            expected,
            actual,
        )
    )

    for finding in merge_findings:
        findings.append(
            {
                "type": "POSSIBLE_MERGE",
                **finding,
            }
        )

    # ---------------------------------------------------------
    # Missing expected segments
    # ---------------------------------------------------------

    for index, segment in enumerate(expected):

        if index in matched_expected:
            continue

        if index in merge_expected_indices:
            continue

        findings.append(
            {
                "type": "MISSING_ACTUAL_SEGMENT",
                "expected": segment,
            }
        )

    # ---------------------------------------------------------
    # Extra actual segments
    # ---------------------------------------------------------

    for index, segment in enumerate(actual):

        if index in matched_actual:
            continue

        if index in split_actual_indices:
            continue

        findings.append(
            {
                "type": "EXTRA_ACTUAL_SEGMENT",
                "actual": segment,
            }
        )

    return {
        "file_name": file_name,
        "expected_count": expected_count,
        "actual_count": actual_count,
        "logical_matches": len(matches),
        "split_count": len(split_findings),
        "merge_count": len(merge_findings),
        "findings": findings,
    }


def compare_documents(expected_data, actual_data):
    """
    Compare JSON1 and JSON2 file-by-file.
    """

    findings = []

    expected_files = set(expected_data.keys())
    actual_files = set(actual_data.keys())

    # ---------------------------------------------------------
    # Missing files
    # ---------------------------------------------------------

    for file_name in sorted(
        expected_files - actual_files
    ):
        findings.append(
            {
                "type": "MISSING_FILE",
                "file_name": file_name,
            }
        )

    # ---------------------------------------------------------
    # Extra files
    # ---------------------------------------------------------

    for file_name in sorted(
        actual_files - expected_files
    ):
        findings.append(
            {
                "type": "EXTRA_FILE",
                "file_name": file_name,
            }
        )

    # ---------------------------------------------------------
    # Compare common files
    # ---------------------------------------------------------

    file_results = []

    for file_name in sorted(
        expected_files & actual_files
    ):
        expected_segments = expected_data[
            file_name
        ]

        actual_segments = actual_data[
            file_name
        ]

        result = compare_file_segments(
            file_name,
            expected_segments,
            actual_segments,
        )

        file_results.append(result)

    return findings, file_results


def build_deterministic_comparison(
    expected_data,
    actual_data,
):
    file_findings, file_results = (
        compare_documents(
            expected_data,
            actual_data,
        )
    )

    lines = []

    lines.append(
        "FILE-LEVEL COMPARISON"
    )
    lines.append(
        "====================="
    )
    lines.append(
        f"Expected files: {len(expected_data)}"
    )
    lines.append(
        f"Actual files:   {len(actual_data)}"
    )
    lines.append("")

    if file_findings:
        lines.append(
            "File-level findings:"
        )

        for finding in file_findings:
            if finding["type"] == "MISSING_FILE":
                lines.append(
                    f"- MISSING FILE: "
                    f"{finding['file_name']}"
                )

            elif finding["type"] == "EXTRA_FILE":
                lines.append(
                    f"- EXTRA FILE: "
                    f"{finding['file_name']}"
                )

        lines.append("")

    lines.append(
        "FILE-BY-FILE SEGMENT COMPARISON"
    )
    lines.append(
        "==============================="
    )

    for result in file_results:
        lines.append("")
        lines.append(
            f"FILE: {result['file_name']}"
        )
        lines.append(
            f"Expected segments: "
            f"{result['expected_count']}"
        )
        lines.append(
            f"Actual segments:   "
            f"{result['actual_count']}"
        )
        lines.append(
            f"Logical matches:   "
            f"{result['logical_matches']}"
        )
        lines.append(
            f"Possible splits:   "
            f"{result['split_count']}"
        )
        lines.append(
            f"Possible merges:   "
            f"{result['merge_count']}"
        )

        if not result["findings"]:
            lines.append(
                "Findings: None"
            )
            continue

        lines.append("Findings:")

        for number, finding in enumerate(
            result["findings"],
            start=1,
        ):
            finding_type = finding["type"]

            lines.append("")
            lines.append(
                f"{number}. {finding_type}"
            )

            if finding_type in {
                "PAGE_BOUNDARY_VARIATION",
                "PAGE_RANGE_DIFFERENCE",
            }:
                lines.append(
                    "   Expected: "
                    + format_segment(
                        finding["expected"]
                    )
                )
                lines.append(
                    "   Actual:   "
                    + format_segment(
                        finding["actual"]
                    )
                )

            elif finding_type == "POSSIBLE_SPLIT":
                lines.append(
                    "   Expected segment:"
                )
                lines.append(
                    "     "
                    + format_segment(
                        finding["expected"]
                    )
                )
                lines.append(
                    "   Actual segments:"
                )

                for segment in finding[
                    "actual_segments"
                ]:
                    lines.append(
                        "     "
                        + format_segment(segment)
                    )

            elif finding_type == "POSSIBLE_MERGE":
                lines.append(
                    "   Expected segments:"
                )

                for segment in finding[
                    "expected_segments"
                ]:
                    lines.append(
                        "     "
                        + format_segment(segment)
                    )

                lines.append(
                    "   Actual segment:"
                )
                lines.append(
                    "     "
                    + format_segment(
                        finding["actual"]
                    )
                )

            elif finding_type == "MISSING_ACTUAL_SEGMENT":
                lines.append(
                    "   Expected segment:"
                )
                lines.append(
                    "     "
                    + format_segment(
                        finding["expected"]
                    )
                )

            elif finding_type == "EXTRA_ACTUAL_SEGMENT":
                lines.append(
                    "   Actual segment:"
                )
                lines.append(
                    "     "
                    + format_segment(
                        finding["actual"]
                    )
                )

    return "\n".join(lines)


def compare(expected_path, actual_path):
    expected_data = load_json(
        expected_path
    )

    actual_data = load_json(
        actual_path
    )

    if not isinstance(expected_data, dict):
        raise ValueError(
            "Expected JSON must be an object containing "
            "file names and segment lists."
        )

    if not isinstance(actual_data, dict):
        raise ValueError(
            "Actual JSON must be an object containing "
            "file names and segment lists."
        )

    comparison = build_deterministic_comparison(
        expected_data,
        actual_data,
    )

    return PROMPT.replace("{{comparison}}", comparison).strip()
