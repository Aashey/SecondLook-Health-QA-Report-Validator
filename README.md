# QA Report Validator

Compare expected and generated JSON for medical reports with report-specific
semantic checks. The validator looks for missing, changed, contradictory, and
meaningfully unexpected information—not just differences in formatting or
wording—and saves a readable Markdown report.

## How it works

1. Each comparator loads `json1.json` as the expected result and `json2.json`
   as the actual result.
2. It builds a comparison prompt using the rules for that report type.
3. The prompt is sent to the locally installed Claude Code CLI.
4. The response is saved in `reports/`.

This project does not call the Claude API directly. JSON content is passed to
Claude Code, so only use data in accordance with your organization's privacy
and data-handling requirements.

## Requirements

- Python 3.10 or newer
- Claude Code CLI installed, authenticated, and available as `claude` in your
  terminal

Check that Claude Code is available:

```powershell
claude --version
```

No additional Python packages are required.

## Quick start

From the project root, replace the sample inputs in the report folder you want
to evaluate:

- `json1.json` — expected result / source of truth
- `json2.json` — actual result to evaluate

Run a comparison in PowerShell:

```powershell
python .\run_comparator.py timeline
```

Choose one of the supported report types:

| Report | Command |
| --- | --- |
| Medical Timeline | `timeline` or `medical_timeline` |
| SoC | `soc` |
| Clinical Summary | `clinical_summary` |
| Case Management | `case_management` |
| Scout | `scout` |

For example, to compare the Scout inputs:

```powershell
python .\run_comparator.py scout
```

## Results

Each run writes or replaces its report in `reports/`:

| Report type | Output |
| --- | --- |
| Medical Timeline | `reports/medical_timeline-comparison.md` |
| SoC | `reports/soc-comparison.md` |
| Clinical Summary | `reports/clinical_summary-comparison.md` |
| Case Management | `reports/case_management-comparison.md` |
| Scout | `reports/scout-comparison.md` |

The report includes an overall result, a summary by severity, details of
missing or changed information, and additional information found in the actual
JSON.

## Project structure

```text
.
├── run_comparator.py
├── comparators/
│   ├── semantic.py
│   ├── medical_timeline.py
│   ├── soc.py
│   ├── clinical_summary.py
│   ├── case_management.py
│   └── scout.py
├── medical_timeline/
├── soc/
├── clinical_summary/
├── case_management/
├── scout/
└── reports/
```

Each report input folder contains `json1.json` and `json2.json`. The
report-specific comparator modules define the focus and exclusions used for
each comparison; `comparators/semantic.py` provides shared JSON loading and
comparison-prompt logic.
