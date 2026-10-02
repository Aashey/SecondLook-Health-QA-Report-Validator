from .semantic import compare_report


REPORT_NAME = "Scout"


FOCUS = """
You are comparing two JSON outputs produced by Scout.

INPUTS
- QUESTION: the exact question Scout was asked.
- EXPECTED: the reference output and source of truth.
- ACTUAL: the output under test.

Your task is to determine whether ACTUAL is a semantically correct response
to QUESTION, using EXPECTED as the primary reference and any evidence, quote,
source, or provenance fields inside either JSON as supporting evidence.

IMPORTANT
- Evaluate only information relevant to QUESTION.
- Compare meaning, not textual similarity.
- Do not require identical wording, structure, ordering, or IDs.
- EXPECTED is the reference truth, but ACTUAL may contain valid information
  not present in EXPECTED if it is clearly supported by evidence in ACTUAL.
- If a difference appears potentially valid but cannot be confidently
  determined from the available evidence, classify it as needs_review.
- Never invent evidence that is not present in either JSON.

CLINICAL INTERPRETATION

When QUESTION involves diagnoses or diagnosed conditions, distinguish
DIAGNOSED from DISCOVERED.

DIAGNOSED:
A condition is diagnosed only when the JSON provides evidence that a clinician
such as a physician, NP, PA, or other licensed provider diagnosed, assessed,
or listed the condition as a diagnosis, including an assessment/plan,
problem list, or discharge diagnosis.

DISCOVERED:
A condition or finding is discovered when it is merely reported, observed, or
mentioned without clinician diagnosis. This includes symptoms, abnormal labs,
imaging findings, pathology findings, patient-reported history, nursing notes,
and findings described as noted, found, identified, detected, consistent with,
or suggestive of.

DIAGNOSIS RULES
- Findings and observations are not automatically diagnoses.
- Imaging, laboratory, or pathology findings are not diagnoses unless a
  clinician explicitly diagnoses or assesses the condition.
- Patient-reported conditions are not diagnoses unless a clinician confirms them.
- possible, probable, likely, suspected, rule out, cannot exclude, concerning
  for, consistent with, and differential are not confirmed diagnoses.
- Negated or excluded conditions are not current diagnoses.
- no evidence of, denied, ruled out, and negative for must not be treated as
  active diagnoses.
- Family history, past history, and resolved conditions must not be treated
  as current active diagnoses.
- A medication, order, procedure, or referral does not by itself prove a diagnosis.
- An abnormal value alone does not establish a diagnosis.
- A diagnosis attributed only to a patient, family member, unlicensed staff,
  or the AI itself is unsupported.
- Do not promote a discovered finding into a diagnosis without supporting
  clinician evidence.
- Do not downgrade a clearly documented clinician diagnosis into merely a finding.

WHEN RELEVANT TO QUESTION, ALSO COMPARE
- clinical findings and symptoms
- diagnoses and status
- procedures
- treatments and medications
- dates
- classifications and coding
- severity
- extracted entities
- supporting evidence and provenance
- clinically meaningful summaries or narrative

MEANINGFUL ERRORS
Treat these as errors when relevant to QUESTION:
- missing information
- unsupported additional information
- incorrect diagnosis status
- discovered vs diagnosed misclassification
- incorrect date or person
- incorrect classification, coding, or severity
- contradictions
- hallucinated information
- clinically meaningful omissions
- information that changes the answer to QUESTION
"""


IGNORE = """
Ignore differences that do not change meaning:

- generated object IDs
- JSON key ordering
- array ordering when order has no semantic meaning
- whitespace and line breaks
- capitalization
- punctuation
- harmless Markdown differences
- equivalent wording or sentence structure
- formatting differences
- non-semantic metadata

Do NOT ignore wording changes when they alter:
- clinical meaning
- diagnosis status
- discovered vs diagnosed classification
- negation
- certainty
- date
- person
- severity
- classification or coding
- evidence/support
- the answer to QUESTION
"""


METRICS = """
Score ACTUAL against EXPECTED using information relevant to QUESTION.

Use values from 0.0 to 1.0.

accuracy:
How accurately does ACTUAL represent the clinically relevant information
in EXPECTED and the available supporting evidence?

completeness:
How much clinically relevant information required to answer QUESTION and
present in EXPECTED is present in ACTUAL?

precision:
How much information returned by ACTUAL is relevant to QUESTION and either
present in EXPECTED or clearly supported by evidence in ACTUAL?

hallucination:
How much clinically relevant information in ACTUAL is unsupported by EXPECTED
and unsupported by evidence contained in ACTUAL?

Use:
0.0 = no meaningful unsupported content
1.0 = substantial unsupported content

consistency:
Is ACTUAL internally consistent, including diagnosis status, dates,
classifications, evidence, and narrative?

clinical_safety:
Assess the severity of clinically meaningful errors:
none, minor, major, or critical.

Use critical only when the difference could plausibly cause severe patient
harm or a materially dangerous misunderstanding.

clarity:
Is ACTUAL clear, coherent, and clinically sensible for QUESTION?

Do not lower scores for harmless formatting or equivalent wording.
"""


OUTPUT_FORMAT = """
Return JSON only. Do not include Markdown or text outside the JSON.

{
  "verdict": "equivalent | minor_differences | meaningful_differences",
  "differences": [
    {
      "category": "discovered | diagnosed | procedure | treatment | date | summary | other",
      "type": "missing | additional | changed | contradictory | misclassified | unsupported | needs_review",
      "expected": "...",
      "actual": "...",
      "clinical_impact": "none | minor | major | critical",
      "explanation": "Brief explanation of the semantic difference and why it matters to QUESTION."
    }
  ],
  "metrics": {
    "accuracy": 0.0,
    "completeness": 0.0,
    "precision": 0.0,
    "hallucination": 0.0,
    "consistency": 0.0,
    "clinical_safety": "none | minor | major | critical",
    "clarity": 0.0
  },
  "overall_assessment": "Short summary of how ACTUAL compares with EXPECTED for QUESTION."
}

VERDICT RULES

equivalent:
ACTUAL conveys the same clinically relevant answer as EXPECTED and contains
no meaningful unsupported or contradictory information.

minor_differences:
ACTUAL has limited differences that do not materially change the answer to
QUESTION and have only minor clinical impact.

meaningful_differences:
ACTUAL contains a clinically meaningful omission, addition, contradiction,
misclassification, unsupported claim, incorrect date/status, or other
difference that changes the answer to QUESTION.

needs_review:
Use this difference type when the available evidence is insufficient to
confidently determine whether the difference is correct.

Do not create difference entries for harmless formatting or equivalent wording.
"""


def compare(question, expected_path, actual_path):
    """
    Compare Scout EXPECTED and ACTUAL outputs using the original Scout question
    as task context.
    """

    if not question or not question.strip():
        raise ValueError(
            "Scout comparator requires the original Scout question."
        )

    full_focus = "\n".join(
        [
            "SCOUT QUESTION",
            "================",
            question.strip(),
            "",
            FOCUS,
            METRICS,
            OUTPUT_FORMAT,
        ]
    )

    return compare_report(
        report_name=REPORT_NAME,
        focus=full_focus,
        ignore=IGNORE,
        expected_path=expected_path,
        actual_path=actual_path,
    )