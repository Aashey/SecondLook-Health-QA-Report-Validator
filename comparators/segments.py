import json


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
    Determine whether two segments likely represent
    the same logical event.

    Page numbers are intentionally NOT used here.
    """

    for field in COMPARE_FIELDS:
        if normalize(expected.get(field)) != normalize(actual.get(field)):
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
    Match segments based on logical event information,
    not array position or exact page range.
    """

    matches = []
    used_actual = set()

    for expected_index, expected_segment in enumerate(expected):
        candidates = []

        for actual_index, actual_segment in enumerate(actual):
            if actual_index in used_actual:
                continue

            if logical_match(expected_segment, actual_segment):
                candidates.append(
                    (
                        actual_index,
                        actual_segment,
                    )
                )

        if not candidates:
            continue

        # Prefer an overlapping page range.
        overlapping = [
            candidate
            for candidate in candidates
            if ranges_overlap(
                page_range(expected_segment),
                page_range(candidate[1]),
            )
        ]

        if overlapping:
            selected = overlapping[0]
        else:
            # If there is no overlap, still match the logical event.
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
    Detect when one expected segment appears to have been
    split into multiple actual segments.
    """

    findings = []
    used_actual = set()

    for expected_index, expected_segment in enumerate(expected):
        expected_range = page_range(expected_segment)

        candidates = []

        for actual_index, actual_segment in enumerate(actual):
            if not logical_match(
                expected_segment,
                actual_segment,
            ):
                continue

            actual_range = page_range(actual_segment)

            if not actual_range:
                continue

            if ranges_overlap(
                expected_range,
                actual_range,
            ) or ranges_touch(
                expected_range,
                actual_range,
            ):
                candidates.append(
                    (
                        actual_index,
                        actual_segment,
                    )
                )

        if len(candidates) > 1:
            for actual_index, _ in candidates:
                used_actual.add(actual_index)

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

    return findings, used_actual


def detect_merges(expected, actual):
    """
    Detect when multiple expected segments appear to have
    been combined into one actual segment.
    """

    findings = []
    used_expected = set()

    for actual_index, actual_segment in enumerate(actual):
        candidates = []

        for expected_index, expected_segment in enumerate(expected):
            if not logical_match(
                expected_segment,
                actual_segment,
            ):
                continue

            expected_range = page_range(expected_segment)
            actual_range = page_range(actual_segment)

            if not expected_range or not actual_range:
                continue

            if ranges_overlap(
                expected_range,
                actual_range,
            ) or ranges_touch(
                expected_range,
                actual_range,
            ):
                candidates.append(
                    (
                        expected_index,
                        expected_segment,
                    )
                )

        if len(candidates) > 1:
            for expected_index, _ in candidates:
                used_expected.add(expected_index)

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

    return findings, used_expected


def compare_segments(expected, actual):
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
    # 1. Compare logically matched segments
    # ---------------------------------------------------------

    for match in matches:
        expected_segment = match["expected"]
        actual_segment = match["actual"]

        expected_range = page_range(expected_segment)
        actual_range = page_range(actual_segment)

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
    # 2. Detect splits
    # ---------------------------------------------------------

    split_findings, split_actual_indices = detect_splits(
        expected,
        actual,
    )

    for finding in split_findings:
        findings.append(
            {
                "type": "POSSIBLE_SPLIT",
                **finding,
            }
        )

    # ---------------------------------------------------------
    # 3. Detect merges
    # ---------------------------------------------------------

    merge_findings, merge_expected_indices = detect_merges(
        expected,
        actual,
    )

    for finding in merge_findings:
        findings.append(
            {
                "type": "POSSIBLE_MERGE",
                **finding,
            }
        )

    # ---------------------------------------------------------
    # 4. Identify genuinely unmatched segments
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

    # ---------------------------------------------------------
    # 5. Build deterministic comparison
    # ---------------------------------------------------------

    lines = [
        f"Expected segment count: {expected_count}",
        f"Actual segment count: {actual_count}",
        "",
        f"Logical matches identified: {len(matches)}",
        f"Potential splits identified: {len(split_findings)}",
        f"Potential merges identified: {len(merge_findings)}",
        "",
    ]

    if not findings:
        lines.append(
            "No logical differences or page-boundary "
            "variations were detected."
        )
    else:
        lines.append("Findings:")

        for number, finding in enumerate(
            findings,
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
                    "Expected: "
                    + format_segment(
                        finding["expected"]
                    )
                )
                lines.append(
                    "Actual:   "
                    + format_segment(
                        finding["actual"]
                    )
                )

            elif finding_type == "POSSIBLE_SPLIT":
                lines.append(
                    "Expected segment:"
                )
                lines.append(
                    "  "
                    + format_segment(
                        finding["expected"]
                    )
                )
                lines.append(
                    "Actual segments:"
                )

                for segment in finding[
                    "actual_segments"
                ]:
                    lines.append(
                        "  "
                        + format_segment(segment)
                    )

            elif finding_type == "POSSIBLE_MERGE":
                lines.append(
                    "Expected segments:"
                )

                for segment in finding[
                    "expected_segments"
                ]:
                    lines.append(
                        "  "
                        + format_segment(segment)
                    )

                lines.append(
                    "Actual segment:"
                )
                lines.append(
                    "  "
                    + format_segment(
                        finding["actual"]
                    )
                )

            elif finding_type == "MISSING_ACTUAL_SEGMENT":
                lines.append(
                    "Expected segment:"
                )
                lines.append(
                    "  "
                    + format_segment(
                        finding["expected"]
                    )
                )

            elif finding_type == "EXTRA_ACTUAL_SEGMENT":
                lines.append(
                    "Actual segment:"
                )
                lines.append(
                    "  "
                    + format_segment(
                        finding["actual"]
                    )
                )

    return "\n".join(lines)


def compare(expected_path, actual_path):
    expected = load_json(expected_path)
    actual = load_json(actual_path)

    if not isinstance(expected, list):
        raise ValueError(
            "Expected JSON must be a list of segments."
        )

    if not isinstance(actual, list):
        raise ValueError(
            "Actual JSON must be a list of segments."
        )

    comparison = compare_segments(
        expected,
        actual,
    )

    return f"""
You are reviewing an LLM-generated medical document segmentation comparison.

The Python comparator has already performed the deterministic comparison.

IMPORTANT:

Do NOT compare segments strictly by array position.

Segments may legitimately differ between JSON1 and JSON2 because the LLM
may:

- choose slightly different page boundaries
- split one logical segment into multiple segments
- merge multiple logical segments into one segment
- represent the same event with slightly different page coverage

Your job is to turn the deterministic findings below into a clear QA report.

## Matching Logic

A segment is considered logically related primarily using:

- event
- event_date
- facility
- provider

Page numbers are secondary.

A page-range difference is NOT automatically a failure.

For example:

Expected:
Emergency Department Visit | pages 1-2

Actual:
Emergency Department Visit | pages 1-1

This should normally be reported as a page-boundary variation because the
logical event is the same and the page ranges overlap.

Likewise:

Expected:
Emergency Department Visit | pages 1-2

Actual:
Emergency Department Visit | pages 1-1
Emergency Department Visit | pages 2-2

This should be reported as a POSSIBLE SPLIT and should normally receive
REVIEW rather than FAIL.

Similarly:

Expected:
Event A | pages 1-1
Event B | pages 2-2

Actual:
Event A/Event B | pages 1-2

This may represent a POSSIBLE MERGE and should be reviewed by QA.

## Verdict Rules

Use exactly one overall verdict:

### PASS
Use PASS when the logical segmentation is consistent and differences are
limited to acceptable page-boundary variations.

### REVIEW
Use REVIEW when there are possible splits, merges, unusual page-range
differences, or other segmentation variations that require QA verification.

REVIEW means the validator detected a meaningful variation but cannot
determine from JSON alone whether the LLM output is actually incorrect.

### FAIL
Use FAIL when a meaningful logical segment is missing, an incorrect event
is produced, or the expected and actual segmentation are materially
different.

Do not fail solely because:

- array positions differ
- segment counts differ due to a possible split or merge
- page boundaries differ slightly
- one segment covers 1-2 while the other covers 1-1
- one logical event is represented by multiple adjacent segments

## QA Report Requirements

Clearly report:

1. Overall verdict: PASS, REVIEW, or FAIL.
2. Expected segment count.
3. Actual segment count.
4. Number of logical matches.
5. Page-boundary variations.
6. Possible splits.
7. Possible merges.
8. Missing logical segments.
9. Extra logical segments.
10. A concise QA conclusion explaining what QA should verify manually.

For every REVIEW or FAIL finding, show the relevant expected and actual
segments, including:

- event
- event_date
- facility
- provider
- start_page
- end_page

Do not invent values.

Do not use source documents.

Do not use source.json.

Do not perform source-grounded validation.

DETERMINISTIC COMPARISON
========================

{comparison}
""".strip()