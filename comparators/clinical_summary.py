from .semantic import compare_report


REPORT_NAME = "Clinical Summary"

FOCUS = """
Compare all meaningful Clinical Summary information, including:
- diagnoses
- conditions
- symptoms
- medical history
- clinical findings
- procedures
- treatments
- medications
- outcomes
- clinically meaningful dates
- providers when clinically meaningful
- facilities when clinically meaningful
- assessments
- clinically relevant narrative
- any information affecting correctness or meaning
"""

IGNORE = """
Ignore differences caused only by:
- generated object IDs
- JSON key ordering
- array ordering when order has no semantic meaning
- whitespace
- line breaks
- capitalization when meaning is unchanged
- punctuation
- formatting
- harmless Markdown differences
- equivalent wording
- equivalent sentence structure
- non-semantic metadata

Do not ignore a difference when it changes clinical meaning or removes/adds
meaningful information.
"""


def compare(expected_path, actual_path):
    return compare_report(
        report_name=REPORT_NAME,
        focus=FOCUS,
        ignore=IGNORE,
        expected_path=expected_path,
        actual_path=actual_path,
    )
