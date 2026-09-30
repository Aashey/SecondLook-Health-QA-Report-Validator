from .semantic import compare_report


REPORT_NAME = "Scout"

FOCUS = """
Compare Scout output semantically.

Focus on:
- identified medical information
- findings
- diagnoses
- conditions
- symptoms
- procedures
- treatments
- relevant dates
- extracted entities
- classifications
- clinical findings
- supporting information
- generated summaries
- clinically meaningful narrative
- other information affecting correctness

Pay particular attention to:
- missing findings
- additional findings
- changed findings
- contradictory findings
- incorrect classifications
- incorrect dates
- missing clinically relevant information
- unsupported information
- meaningful changes in generated content
"""

IGNORE = """
Ignore differences caused only by:
- generated object IDs
- array ordering when order has no semantic meaning
- JSON key ordering
- whitespace
- line breaks
- capitalization
- punctuation
- formatting
- equivalent wording
- equivalent sentence structure
- harmless Markdown differences
- non-semantic metadata

Do not ignore wording changes when they change clinical meaning, add
unsupported information, remove meaningful information, or introduce
contradictions.
"""


def compare(expected_path, actual_path):
    return compare_report(
        report_name=REPORT_NAME,
        focus=FOCUS,
        ignore=IGNORE,
        expected_path=expected_path,
        actual_path=actual_path,
    )
