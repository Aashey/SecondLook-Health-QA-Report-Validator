import json
from pathlib import Path


def load_json(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    try:
        with path.open("r", encoding="utf-8-sig") as file:
            return json.load(file)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {path}: {exc}") from exc


def compare_report(
    report_name,
    focus,
    ignore,
    expected_path,
    actual_path,
):
    expected = load_json(expected_path)
    actual = load_json(actual_path)

    prompt = f"""
You are an expert QA evaluator validating a {report_name}.

JSON 1 = EXPECTED RESULT / SOURCE OF TRUTH
JSON 2 = ACTUAL RESULT / SYSTEM OUTPUT

Your task is semantic QA comparison.

Do NOT require JSON1 and JSON2 to be textually identical.

The expected result is the source of truth. Determine whether the
actual result conveys the same required information and meaning.

REPORT-SPECIFIC FOCUS:
{focus}

DIFFERENCES TO IGNORE WHEN THEY DO NOT CHANGE MEANING:
{ignore}

GENERAL COMPARISON RULES:
- Compare nested objects, arrays, sections, and individual fields.
- Do not assume array position means object identity unless ordering
  is explicitly meaningful.
- Match corresponding objects semantically.
- Equivalent wording is acceptable when the underlying meaning is the same.
- Report missing information.
- Report unexpected information when it changes or adds meaningful content.
- Report contradictions.
- Verify meaningful dates and functional values.
- Do not invent expected information.
- Distinguish harmless formatting differences from meaningful differences.

SEVERITY:
Critical = materially changes correctness, meaning, or a critical functional result.
Major = meaningful difference affecting report accuracy, interpretation, or functionality.
Minor = limited-impact difference.
Acceptable = textual/structural difference where the underlying meaning remains equivalent.

OUTPUT FORMAT:

# {report_name} QA Comparison

## Result
Overall Result: PASS or FAIL

## Summary
Expected objects/items:
Actual objects/items:
Meaningful Differences:
Critical:
Major:
Minor:
Acceptable:

## Missing / Changed Information
For every meaningful difference:
Expected:
Actual:
Location/Field:
Difference:
Severity:
Explanation:

## Additional Information
List unexpected information that is meaningfully different from expected.

## Final Summary
Explain whether JSON2 matches JSON1 semantically and why.

Do not fail merely because:
- wording differs
- formatting differs
- JSON key order differs
- harmless whitespace differs
- equivalent Markdown differs
- semantically irrelevant metadata differs

EXPECTED JSON:
{json.dumps(expected, indent=2, ensure_ascii=False)}

ACTUAL JSON:
{json.dumps(actual, indent=2, ensure_ascii=False)}
"""
    return prompt
