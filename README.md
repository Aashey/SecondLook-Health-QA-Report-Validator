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
4. The response is saved as a numbered Markdown report in that report type's
   folder.

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

From the project root, copy the empty example inputs into the report folder you
want to evaluate. The working `json1.json` and `json2.json` files are ignored by
Git, so your report data and edits will not be pushed:

- `json1.example.json` — empty template for the expected result / source of truth
- `json2.example.json` — empty template for the actual result to evaluate

For example, to prepare Scout inputs in PowerShell:

```powershell
Copy-Item .\scout\json1.example.json .\scout\json1.json
Copy-Item .\scout\json2.example.json .\scout\json2.json
```

Repeat this for the report folder you want to evaluate. Replace the contents of
the copied files with your local data.

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

Each run saves a new report in the corresponding input folder. Files are
numbered sequentially, so rerunning a comparison never replaces an earlier
report. Generated reports are ignored by Git and will not be pushed:

| Report type | Output |
| --- | --- |
| Medical Timeline | `medical_timeline/medical_timeline-comparison1.md`, then `...2.md`, `...3.md`, etc. |
| SoC | `soc/soc-comparison1.md`, then `...2.md`, `...3.md`, etc. |
| Clinical Summary | `clinical_summary/clinical_summary-comparison1.md`, then `...2.md`, `...3.md`, etc. |
| Case Management | `case_management/case_management-comparison1.md`, then `...2.md`, `...3.md`, etc. |
| Scout | `scout/scout-comparison1.md`, then `...2.md`, `...3.md`, etc. |

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
└── scout/
```

Each report input folder has tracked `json1.example.json` and
`json2.example.json` templates. Copy them to the ignored `json1.json` and
`json2.json` working files before running a comparison. The report-specific
comparator modules define the focus and exclusions used for each comparison;
`comparators/semantic.py` provides shared JSON loading and comparison-prompt
logic.
