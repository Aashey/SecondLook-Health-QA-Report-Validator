# Scout QA Comparison

## Result

**Overall Result: PASS**

---

## Summary

|                        | Count                                                       |
| ---------------------- | ----------------------------------------------------------- |
| Expected objects/items | 7 diagnosis entries + 2 ICD-10 codes                        |
| Actual objects/items   | 7 diagnosis entries + 2 ICD-10 codes + 1 Historical section |
| Meaningful Differences | 7                                                           |
| Critical               | 0                                                           |
| Major                  | 2                                                           |
| Minor                  | 3                                                           |
| Acceptable             | ≥8                                                         |

---

## Missing / Changed Information

---

**Difference 1**

- **Expected:** `"Second episode (September 2020): central left lower lobar PE with subsegmental emboli in right lower lobe and left upper lobe, unprovoked"`
- **Actual:** `"Second episode: September 29, 2020 (central left lower lobar PE with bilateral subsegmental emboli, submassive with troponin 0.8)"` — no mention of "unprovoked"
- **Location/Field:** Primary Diagnoses → Recurrent Pulmonary Embolism → Second Episode
- **Difference:** The "unprovoked" classification of the second PE is absent in the actual output.
- **Severity:** **Major**
- **Explanation:** The unprovoked nature of the second PE is the primary clinical basis for indefinite anticoagulation. Its absence removes a key piece of clinical reasoning from the diagnosis entry, even though the anticoagulation plan itself is still documented.

---

**Difference 2**

- **Expected:** `"Requires lifelong anticoagulation due to recurrent unprovoked PE"` (under Secondary Hypercoagulable State)
- **Actual:** Not stated under this diagnosis; anticoagulation plan is mentioned under Recurrent PE only.
- **Location/Field:** Secondary Diagnoses → Secondary Hypercoagulable State
- **Difference:** The explicit clinical rationale linking the hypercoagulable state to the need for lifelong anticoagulation is missing.
- **Severity:** **Major**
- **Explanation:** This rationale connects the two diagnoses and explains the management decision. Its omission weakens the clinical completeness of the hypercoagulable state entry.

---

**Difference 3**

- **Expected:** `"Managed with Cetirizine 10 mg twice daily"`
- **Actual:** `"Managed with Cetirizine"` (dose and frequency omitted)
- **Location/Field:** Primary Diagnoses → Chronic Urticaria → Management
- **Difference:** Medication dose (10 mg) and frequency (twice daily) are missing.
- **Severity:** **Minor**
- **Explanation:** Dosing is a clinically meaningful detail, though the drug identity is correct and the omission does not contradict any information.

---

**Difference 4**

- **Expected:** `"MRI: small lacunar infarct in left posterior frontal lobe"`
- **Actual:** `"MRI: punctate restricted diffusion in left posterior frontal lobe"`
- **Location/Field:** Primary Diagnoses → Cryptogenic Stroke → MRI finding
- **Difference:** Actual uses the imaging-level descriptor ("punctate restricted diffusion") rather than the clinical interpretation ("small lacunar infarct"). Both refer to the same lesion in the same location.
- **Severity:** **Minor**
- **Explanation:** "Punctate restricted diffusion" is the MRI phenomenology; "small lacunar infarct" is the clinical conclusion drawn from it. The actual wording is more radiologically precise and does not contradict the expected meaning, but it omits the clinical interpretive label "lacunar infarct."

---

**Difference 5**

- **Expected:** `"Etiology: paradoxical embolism through ASD"`
- **Actual:** `"Etiology: likely paradoxical embolism through ASD"`
- **Location/Field:** Primary Diagnoses → Cryptogenic Stroke → Etiology
- **Difference:** Actual adds the qualifier "likely," softening certainty.
- **Severity:** **Mino**
- **Explanation:** Adding "likely" introduces a degree of uncertainty not present in the expected output. Given the ROPE score and workup, the expected output presents this as a concluded etiology. This is a minor change in clinical confidence language.

---

## Additional Information

The actual output contains the following information **not present** in the expected output. None of it contradicts the expected content; it all represents additional clinical detail.

| Item                                                                         | Location                        | Assessment                                                          |
| ---------------------------------------------------------------------------- | ------------------------------- | ------------------------------------------------------------------- |
| Second PE specifically dated September**29**, 2020                     | Recurrent PE → Second episode  | Acceptable additive detail                                          |
| Second PE characterized as "submassive with troponin 0.8"                    | Recurrent PE → Second episode  | Meaningful additive clinical detail                                 |
| Urticaria confirmed "by rechallenge"                                         | Chronic Urticaria               | Acceptable additive detail                                          |
| Nickel, Cefazolin, radiocontrast testing negative for urticaria              | Chronic Urticaria               | Acceptable additive detail                                          |
| Actual lab values for Protein C (133), Protein S (84), Antithrombin III (88) | Secondary Hypercoagulable State | Acceptable additive detail (replaces "negative" with actual values) |
| Post-operative seroma requiring aspiration after lipoma excision             | Lipoma                          | Acceptable additive detail                                          |
| "Historical Diagnoses" section with Z87.74 and elevated troponin (Feb 2020)  | New section                     | Additive; Z87.74 is present in expected's ICD-10 section            |
| First PE noted as "discovered during device migration workup"                | Recurrent PE → First episode   | Acceptable clinical context                                         |
| ICD-10 Q21.1 placed inline under ASD entry                                   | ASD                             | Acceptable restructuring; code is present in expected               |

---

## Final Summary

The actual output is **semantically equivalent** to the expected output in its core clinical content: all seven diagnoses are identified, key dates and procedures match, ICD-10 codes are present, and the overall clinical narrative is preserved. The actual output is in several areas **more detailed** than the expected (specific PE date, submassive characterization, lab values, seroma, rechallenge confirmation), which is additive rather than contradictory.

Two **major** gaps exist: the absence of the "unprovoked" classification on the second PE, and the missing rationale linking the hypercoagulable state to the lifelong anticoagulation decision. These weaken clinical reasoning traceability but do not introduce incorrect information. Three **minor** gaps exist: missing Cetirizine dosage, a slight softening of stroke etiology certainty ("likely"), and use of imaging-level rather than clinical-level MRI language.

The report is a **PASS** — the clinical picture is substantially correct and complete, with the noted gaps representing omissions rather than errors or contradictions.
