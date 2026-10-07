import json
from pathlib import Path

from source_retriever import (
    build_query,
    format_chunks_for_judge,
    retrieve_relevant_chunks,
)


REPORT_DESCRIPTIONS = {
    "medical_timeline": "Medical Timeline",
    "timeline": "Medical Timeline",
    "soc": "Statement of Condition",
    "clinical_summary": "Clinical Summary",
    "case_management": "Case Management",
    "scout": "Scout",
}


def load_json(path: Path):
    if not path.exists():
        raise FileNotFoundError(
            f"File not found: {path}"
        )

    try:
        with path.open("r", encoding="utf-8-sig") as file:
            return json.load(file)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Invalid JSON in {path}: {exc}"
        ) from exc


def build_source_grounded_prompt(
    report_type,
    expected,
    actual,
    comparison,
    source_chunks,
    question=None,
):
    report_name = REPORT_DESCRIPTIONS.get(
        report_type,
        report_type,
    )

    question_section = ""

    if question:
        question_section = f"""
SCOUT QUESTION
==============

{question}

The source-grounded evaluation must consider whether ACTUAL correctly
answers this exact question.
"""

    evidence = format_chunks_for_judge(source_chunks)

    return f"""
You are the final QA adjudicator for a {report_name} generated from
medical source documents.

This is a SOURCE-GROUNDED VALIDATION.

The source documents are the ultimate ground truth.

JSON1 and JSON2 are system outputs.

JSON1:
- represents the previous/reference expected output
- is useful for identifying what changed
- is NOT automatically correct

JSON2:
- represents the output under test
- is NOT automatically incorrect when it differs from JSON1

Your job is to determine whether the differences identified by the
existing comparison are actually correct or incorrect when checked
against the source evidence.

{question_section}

==================================================
CORE PRINCIPLE
==================================================

DIFFERENCE DOES NOT EQUAL DEFECT.

An ACTUAL result must NOT fail merely because it differs from EXPECTED.

If ACTUAL contains information that differs from EXPECTED but is supported
by the source documents, ACTUAL may be correct and should not be marked
as a defect.

If EXPECTED contains information that is contradicted by the source and
ACTUAL correctly reflects the source, prefer ACTUAL.

If both JSON1 and JSON2 are supported by the source and differ only in
valid interpretation or equivalent wording, classify the difference as
acceptable.

If neither output is supported by the source, identify the incorrect
output.

If the available source evidence is insufficient to determine correctness,
do not invent an answer. Mark the issue as INSUFFICIENT_EVIDENCE.

==================================================
SOURCE EVIDENCE RULES
==================================================

Only use the provided source evidence as source-of-truth evidence.

Do not invent source content.

Do not assume that something is true merely because it appears in JSON1.

Do not assume that something is false merely because it differs from JSON1.

A source statement must support the conclusion.

Pay attention to:

- dates
- diagnoses
- symptoms
- procedures
- treatments
- medications
- clinical findings
- outcomes
- provider information
- facility information
- patient identity
- status
- severity
- classification
- negation
- certainty
- historical vs active conditions
- clinically meaningful narrative
- functional case information

For Scout, also consider whether the source evidence supports the answer
to the original question.

==================================================
DIFFERENCE ADJUDICATION
==================================================

For every meaningful difference identified in the existing comparison,
determine which of the following applies:

ACTUAL_CORRECT
----------------
ACTUAL is supported by the source and EXPECTED is incorrect or less accurate.

EXPECTED_CORRECT
----------------
EXPECTED is supported by the source and ACTUAL is incorrect.

BOTH_SUPPORTED
--------------
Both outputs are supported by the source and the difference is acceptable.

BOTH_INCORRECT
--------------
Neither output is correctly supported by the source.

INSUFFICIENT_EVIDENCE
---------------------
The provided source evidence does not establish which output is correct.

NO_MEANINGFUL_DIFFERENCE
------------------------
The existing comparison identified a difference, but source validation
shows that it does not materially affect correctness or meaning.

==================================================
ADDITIONAL ACTUAL INFORMATION
==================================================

Pay special attention to information present in ACTUAL but absent from
EXPECTED.

Do NOT call it hallucination simply because EXPECTED does not contain it.

Determine whether the additional information is supported by the source.

If supported:
- classify it as ACTUAL_CORRECT or BOTH_SUPPORTED where appropriate.

If unsupported:
- identify it as unsupported information.

If the source evidence is insufficient:
- classify it as INSUFFICIENT_EVIDENCE.

==================================================
SOURCE EVIDENCE
==================================================

{evidence}

==================================================
EXPECTED JSON
==================================================

{json.dumps(expected, indent=2, ensure_ascii=False)}

==================================================
ACTUAL JSON
==================================================

{json.dumps(actual, indent=2, ensure_ascii=False)}

==================================================
EXISTING COMPARISON
==================================================

{comparison}

==================================================
OUTPUT FORMAT
==================================================

Return Markdown only.

Do not return JSON.

Do not return a Markdown code fence.

Do not provide chain-of-thought or hidden reasoning.

Use exactly these sections:

# Source-Grounded QA Validation

## Final Result

State exactly one:

**Result:** PASS

**Result:** PASS with Notable Differences

**Result:** FAIL

Then state:

**Verdict:** ...

Possible verdicts:

- equivalent
- actual_correct
- expected_correct
- both_supported
- both_incorrect
- insufficient_evidence
- meaningful_differences

The overall result must be based on the source evidence, not merely on
whether JSON1 and JSON2 differ.

## Source Validation Summary

Explain briefly whether ACTUAL is supported by the source documents.

Explicitly state whether the source evidence changed the conclusion
from the original JSON1-vs-JSON2 comparison.

## Adjudicated Differences

For each meaningful difference:

### 1. [VERDICT] — Short Description

- **Expected:** ...
- **Actual:** ...
- **Source Evidence:** ...
- **Source:** [document filename, PDF page]
- **Assessment:** ...
- **QA Impact:** ...

Use one of:

ACTUAL_CORRECT
EXPECTED_CORRECT
BOTH_SUPPORTED
BOTH_INCORRECT
INSUFFICIENT_EVIDENCE
NO_MEANINGFUL_DIFFERENCE

Do not list harmless differences.

## Additional Actual Information

Identify meaningful information present in ACTUAL but absent from EXPECTED.

For each:

- **Actual Information:** ...
- **Source Support:** Supported / Unsupported / Insufficient Evidence
- **Source:** ...
- **Assessment:** ...

If none:

No meaningful additional information requiring source validation was
identified.

## Final Summary

Explain:

1. What the original comparison found.
2. What the source documents establish.
3. Whether ACTUAL is correct.
4. Whether EXPECTED was actually incorrect where applicable.
5. Whether the QA decision changed because of source validation.

The final line must be exactly:

**Final Verdict:** equivalent

OR

**Final Verdict:** actual_correct

OR

**Final Verdict:** expected_correct

OR

**Final Verdict:** both_supported

OR

**Final Verdict:** both_incorrect

OR

**Final Verdict:** insufficient_evidence

OR

**Final Verdict:** meaningful_differences
""".strip()


def build_source_validation(
    report_type,
    expected_path,
    actual_path,
    comparison,
    question=None,
    top_k=8,
):
    """
    Retrieve relevant source evidence and construct the second-stage
    source-grounded Claude prompt.
    """

    expected = load_json(expected_path)
    actual = load_json(actual_path)

    expected_text = json.dumps(
        expected,
        ensure_ascii=False,
    )

    actual_text = json.dumps(
        actual,
        ensure_ascii=False,
    )

    query = build_query(
        comparison_text=comparison,
        expected_text=expected_text,
        actual_text=actual_text,
    )

    source_chunks = retrieve_relevant_chunks(
        query=query,
        top_k=top_k,
    )

    prompt = build_source_grounded_prompt(
        report_type=report_type,
        expected=expected,
        actual=actual,
        comparison=comparison,
        source_chunks=source_chunks,
        question=question,
    )

    return prompt, source_chunks