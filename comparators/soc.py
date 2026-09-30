from .semantic import compare_report


REPORT_NAME = "SoC"

FOCUS = """
Compare the Statement of Condition semantically.

Focus on:
- conditions
- diagnoses
- symptoms
- clinical findings
- severity
- progression
- treatments
- procedures
- medications
- relevant dates
- clinical assessment
- clinical conclusions
- relevant medical history
- supporting clinical information
- meaningful clinical narrative
- other information affecting correctness or meaning
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

Do not ignore differences that change clinical meaning.
"""


def compare(expected_path, actual_path):
    return compare_report(
        report_name=REPORT_NAME,
        focus=FOCUS,
        ignore=IGNORE,
        expected_path=expected_path,
        actual_path=actual_path,
    )
