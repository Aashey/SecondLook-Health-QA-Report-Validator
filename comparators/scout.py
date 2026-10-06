from .semantic import compare_report


REPORT_NAME = "Scout"


FOCUS = """
You are a QA comparison engine for two JSON outputs produced by Scout.

INPUTS
- QUESTION: the exact question Scout was asked.
- EXPECTED: the reference Scout output and primary source of truth.
- ACTUAL: the Scout output under test.

Your task is to determine whether ACTUAL provides a semantically correct,
clinically appropriate answer to QUESTION.

EXPECTED is the primary reference. However, ACTUAL may contain valid
information that is not present in EXPECTED when that information is clearly
supported by evidence, source text, quotes, provenance, or other supporting
fields contained in EXPECTED or ACTUAL.

Never invent evidence.

==================================================
CORE COMPARISON RULES
==================================================

1. Evaluate only information relevant to QUESTION.

2. Compare semantic meaning, not textual similarity.

3. Do not require:
   - identical wording
   - identical sentence structure
   - identical JSON structure
   - identical field ordering
   - identical array ordering when order is not meaningful
   - identical IDs
   - identical formatting

4. Treat equivalent wording as equivalent.

5. Do not report a difference merely because ACTUAL:
   - uses different wording
   - presents information in a different order
   - contains additional supported detail
   - uses a different but equivalent clinical phrase
   - has different generated IDs or metadata

6. Report a difference only when it changes or potentially changes the
   meaning, correctness, completeness, safety, or answer to QUESTION.

7. If a difference appears potentially valid but cannot be confidently
   determined from the available evidence, classify it as NEEDS REVIEW
   rather than declaring it incorrect.

8. Never invent evidence, diagnoses, dates, relationships, or clinical facts.

==================================================
CLINICAL INTERPRETATION
==================================================

When QUESTION involves diagnoses or diagnosed conditions, explicitly
distinguish between DIAGNOSED and DISCOVERED.

DIAGNOSED:
A condition is diagnosed only when the available JSON provides evidence that
a clinician such as a physician, NP, PA, or other licensed provider diagnosed,
assessed, or listed the condition as a diagnosis.

Valid diagnostic evidence may include:
- assessment/plan
- diagnosis list
- problem list
- discharge diagnosis
- explicit clinician diagnosis
- explicit clinician assessment of the condition

DISCOVERED:
A condition or finding is discovered when it is merely reported, observed,
identified, or mentioned without sufficient evidence of clinician diagnosis.

Examples include:
- symptoms
- abnormal laboratory values
- imaging findings
- pathology findings
- patient-reported history
- nursing documentation
- findings described as noted, found, identified, detected, consistent with,
  or suggestive of

DIAGNOSIS RULES:

- Findings and observations are not automatically diagnoses.
- Imaging findings are not diagnoses unless supported by clinician diagnosis
  or assessment.
- Laboratory abnormalities are not diagnoses unless supported by clinician
  diagnosis or assessment.
- Pathology findings are not diagnoses unless supported by clinician diagnosis
  or assessment.
- Patient-reported conditions are not diagnoses unless a clinician confirms
  or diagnoses them.
- possible, probable, likely, suspected, rule out, cannot exclude,
  concerning for, consistent with, and differential do not establish a
  confirmed diagnosis by themselves.
- Negated or excluded conditions are not active diagnoses.
- "no evidence of", "denied", "ruled out", and "negative for" must not be
  interpreted as active diagnoses.
- Family history must not be interpreted as a current diagnosis.
- Past or resolved conditions must not be interpreted as current active
  diagnoses unless QUESTION specifically asks about historical conditions.
- A medication, order, procedure, or referral does not by itself prove a
  diagnosis.
- An abnormal value alone does not establish a diagnosis.
- A diagnosis attributed only to a patient, family member, unlicensed staff,
  or the AI is not sufficient evidence of a clinician diagnosis.
- Do not promote a discovered finding into a diagnosis without supporting
  clinician evidence.
- Do not downgrade a clearly documented clinician diagnosis into merely a
  finding.

When diagnosis status is relevant, compare:
- diagnosis name
- diagnosed vs discovered status
- confirmed vs suspected status
- active vs historical/resolved status
- supporting clinician evidence
- negation
- certainty

==================================================
OTHER CLINICALLY MEANINGFUL COMPARISONS
==================================================

When relevant to QUESTION, compare:

- clinical findings
- symptoms
- diagnoses
- diagnosis status
- procedures
- treatments
- medications
- dates
- persons/patients
- classifications
- coding
- severity
- extracted entities
- supporting evidence
- provenance
- clinically meaningful summaries
- narrative conclusions

A difference is meaningful when it changes the answer to QUESTION or could
materially affect interpretation.

==================================================
MEANINGFUL ERRORS
==================================================

Treat the following as meaningful when relevant to QUESTION:

- missing required information
- unsupported information
- incorrect diagnosis status
- diagnosed vs discovered misclassification
- incorrect date
- incorrect person
- incorrect classification
- incorrect coding
- incorrect severity
- contradiction
- clinically meaningful hallucination
- clinically meaningful omission
- incorrect negation
- incorrect certainty
- incorrect interpretation
- unsupported clinical conclusion
- any difference that changes the answer to QUESTION

==================================================
IGNORED DIFFERENCES
==================================================

Ignore differences that do not change meaning:

- generated object IDs
- generated database IDs
- JSON key ordering
- array ordering when order has no semantic meaning
- whitespace
- line breaks
- capitalization
- punctuation
- harmless Markdown differences
- equivalent wording
- equivalent sentence structure
- formatting
- non-semantic metadata

Do NOT ignore wording or formatting when it changes:

- clinical meaning
- diagnosis status
- diagnosed vs discovered classification
- negation
- certainty
- date
- person
- severity
- classification
- coding
- evidence/support
- answer to QUESTION

==================================================
SEVERITY RULES
==================================================

Classify each meaningful difference as exactly one of:

CRITICAL
A difference that could plausibly cause severe patient harm or a materially
dangerous clinical misunderstanding.

MAJOR
A difference that materially changes the answer to QUESTION, introduces a
meaningful incorrect clinical fact, omits an important required fact, or
misclassifies clinically important information.

MINOR
A real but non-critical difference that does not materially change the main
answer to QUESTION.

NEEDS REVIEW
A potentially meaningful difference whose correctness cannot be confidently
determined from the available evidence.

Do not use CRITICAL unless there is a plausible serious safety consequence.

Do not count harmless differences as MINOR.

==================================================
RESULT DETERMINATION
==================================================

Choose exactly one result and one verdict.

PASS
Verdict: equivalent

Use when ACTUAL correctly answers QUESTION and there are no meaningful
differences.

PASS with Notable Differences
Verdict: minor_differences

Use when ACTUAL still correctly answers QUESTION but contains only minor
differences, limited omissions, or additional information that does not
materially affect correctness.

FAIL
Verdict: meaningful_differences

Use when ACTUAL contains a MAJOR or CRITICAL difference, or otherwise fails
to correctly answer QUESTION.

NEEDS REVIEW cases should normally result in:
PASS with Notable Differences / minor_differences

unless the unresolved difference prevents determining whether ACTUAL answers
QUESTION correctly. In that case use:
FAIL / meaningful_differences

==================================================
METRICS
==================================================

Score ACTUAL using values from 0.0 to 1.0.

ACCURACY
How accurately ACTUAL represents the clinically relevant information required
to answer QUESTION, considering EXPECTED and available supporting evidence.

1.0 = fully accurate
0.0 = substantially incorrect

COMPLETENESS
How much clinically relevant information required to answer QUESTION and
present in EXPECTED is present in ACTUAL.

1.0 = complete
0.0 = substantially incomplete

PRECISION
How much information in ACTUAL is relevant to QUESTION and either supported
by EXPECTED or clearly supported by available evidence.

1.0 = highly focused and relevant
0.0 = largely irrelevant or unsupported

HALLUCINATION
Measure the amount of clinically meaningful unsupported information introduced
by ACTUAL.

1.0 = no meaningful unsupported information
0.0 = substantial unsupported information

IMPORTANT:
Hallucination uses the same direction as the other metrics:
HIGHER IS BETTER.

Do not penalize ACTUAL simply because it contains information absent from
EXPECTED. Determine whether that additional information is supported by
available evidence first.

CONSISTENCY
Whether ACTUAL is internally consistent and does not contradict itself or
its own evidence.

1.0 = fully consistent
0.0 = substantially inconsistent

CLINICAL SAFETY
Use the following score:

1.0 = no clinically meaningful safety concern
0.75 = minor safety concern
0.50 = moderate/major safety concern
0.25 = serious safety concern
0.0 = critical safety concern

CLARITY
Whether ACTUAL communicates the answer clearly, coherently, and
unambiguously.

1.0 = very clear
0.0 = unclear or unusable

Do not lower any score for harmless formatting or equivalent wording.
"""


IGNORE = """
Ignore differences that do not change meaning:

- generated object IDs
- generated database IDs
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
required to answer QUESTION, considering EXPECTED and available supporting
evidence?

1.0 = fully accurate
0.0 = substantially incorrect

completeness:
How much clinically relevant information required to answer QUESTION and
present in EXPECTED is present in ACTUAL?

1.0 = complete
0.0 = substantially incomplete

precision:
How much information in ACTUAL is relevant to QUESTION and either present in
EXPECTED or clearly supported by evidence in ACTUAL?

1.0 = highly focused and relevant
0.0 = largely irrelevant or unsupported

hallucination:
Measure the amount of clinically meaningful unsupported information introduced
by ACTUAL.

IMPORTANT: Higher is better for this metric.

1.0 = no meaningful unsupported content
0.0 = substantial unsupported content

Do not penalize ACTUAL merely because it contains information absent from
EXPECTED. First determine whether the additional information is supported by
evidence available in EXPECTED or ACTUAL.

consistency:
Is ACTUAL internally consistent, including diagnosis status, dates,
classifications, evidence, and narrative?

1.0 = fully consistent
0.0 = substantially inconsistent

clinical_safety:
Assess the severity of clinically meaningful errors.

1.0 = no clinically meaningful safety concern
0.75 = minor safety concern
0.50 = moderate/major safety concern
0.25 = serious safety concern
0.0 = critical safety concern

Use critical only when the difference could plausibly cause severe patient
harm or a materially dangerous misunderstanding.

clarity:
Is ACTUAL clear, coherent, and clinically sensible for QUESTION?

1.0 = very clear
0.0 = unclear or unusable

Do not lower scores for harmless formatting or equivalent wording.
"""


OUTPUT_FORMAT = """
RETURN MARKDOWN ONLY.

DO NOT RETURN JSON.

DO NOT RETURN A JSON OBJECT.

DO NOT RETURN A JSON ARRAY.

DO NOT RETURN JSON-LIKE KEY/VALUE OUTPUT.

DO NOT wrap the report in a Markdown code fence.

Do not include chain-of-thought, hidden reasoning, or internal analysis.

The output must begin exactly with:

# Scout QA Comparison

The output must contain exactly these top-level sections and in this order:

# Scout QA Comparison

## Result

## Summary

## Missing / Changed Information

## Additional Information

## Metrics

## Final Summary

==================================================
RESULT
==================================================

State exactly one result:

**Result:** PASS
OR
**Result:** PASS with Notable Differences
OR
**Result:** FAIL

State exactly one verdict:

**Verdict:** equivalent
OR
**Verdict:** minor_differences
OR
**Verdict:** meaningful_differences

Then provide a concise 1-3 sentence explanation.

==================================================
SUMMARY
==================================================

Identify the QUESTION being evaluated.

Summarize whether ACTUAL correctly answers QUESTION.

Use this table:

| Aspect | EXPECTED | ACTUAL | Assessment |
|---|---|---|---|
| Answer to QUESTION | ... | ... | Equivalent / Difference |
| Key finding | ... | ... | Equivalent / Difference |

Add additional rows only when they are relevant to QUESTION.

Then provide:

| Difference Type | Count |
|---|---:|
| Critical | 0 |
| Major | 0 |
| Minor | 0 |
| Needs Review | 0 |
| Harmless / Acceptable | 0 |

The counts must match the differences actually described later in the report.

Harmless differences must never be included as meaningful differences.

==================================================
MISSING / CHANGED INFORMATION
==================================================

If there are no meaningful differences, write:

No meaningful missing or changed information was identified.

Otherwise, create one numbered subsection for every meaningful difference.

Example:

### 1. [MAJOR] — Incorrect Diagnosis Status

- **Expected information:** ...
- **Actual information:** ...
- **Location / Field:** ...
- **Why it matters to QUESTION:** ...

Use only:

CRITICAL
MAJOR
MINOR
NEEDS REVIEW

Do not include harmless differences in this section.

Do not create a difference merely because wording or structure differs.

==================================================
ADDITIONAL INFORMATION
==================================================

Describe meaningful information present in ACTUAL that is absent from EXPECTED.

For each item clearly identify whether it is:

- Supported by available evidence
- Needs review

Do not call additional information hallucinated solely because it is absent
from EXPECTED.

If there is no meaningful additional information, write:

No meaningful additional information was identified in ACTUAL.

==================================================
METRICS
==================================================

Use exactly this table:

| Metric | Score | Justification |
|---|---:|---|
| Accuracy | 0.0–1.0 | ... |
| Completeness | 0.0–1.0 | ... |
| Precision | 0.0–1.0 | ... |
| Hallucination | 0.0–1.0 | ... |
| Consistency | 0.0–1.0 | ... |
| Clinical Safety | 0.0–1.0 | ... |
| Clarity | 0.0–1.0 | ... |

Scores must be numeric values between 0.0 and 1.0.

==================================================
FINAL SUMMARY
==================================================

Explain:

1. Whether ACTUAL answers QUESTION correctly.
2. The most important omission, contradiction, or changed detail.
3. Any meaningful additional information.
4. Whether the differences affect the QA decision.

The final line must be exactly one of:

**Final Verdict:** equivalent

OR

**Final Verdict:** minor_differences

OR

**Final Verdict:** meaningful_differences

Do not add any content after Final Verdict.
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