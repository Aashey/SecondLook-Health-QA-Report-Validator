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
4. The response is saved as a numbered Markdown report under
   `output/<report_type>/`.

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

From the project root, copy the empty example inputs into the matching folder
under `input/`. The working `json1.json` and `json2.json` files are ignored by
Git, so your report data and edits will not be pushed:

- `json1.example.json` — empty template for the expected result / source of truth
- `json2.example.json` — empty template for the actual result to evaluate

For example, to prepare SoC inputs in PowerShell:

```powershell
Copy-Item .\input\soc\json1.example.json .\input\soc\json1.json
Copy-Item .\input\soc\json2.example.json .\input\soc\json2.json
```

Repeat this for the report folder you want to evaluate. Replace the contents of
the copied files with your local data.

Run a comparison in PowerShell:

```powershell
python .\run_comparator.py timeline
```

The executable command format for each comparator is:

| Report | Command |
| --- | --- |
| Medical Timeline | `timeline` or `medical_timeline` |
| SoC | `soc` |
| Clinical Summary | `clinical_summary` |
| Case Management | `case_management` |
| Scout | `scout` |
| Segments | `segments` |

Run any command below from the project root after preparing its input JSON
files. Each line is executable in PowerShell:

```powershell
python .\run_comparator.py timeline
python .\run_comparator.py soc
python .\run_comparator.py clinical_summary
python .\run_comparator.py case_management
python .\run_comparator.py scout
python .\run_comparator.py segments
```

## Results

Each run saves a new report in its own numbered folder under `output`. Runs
are numbered separately for each report type, so rerunning a comparison never
replaces an earlier report. Generated reports are ignored by Git and will not
be pushed:

| Report type | Output |
| --- | --- |
| Medical Timeline | `output/medical_timeline/1/comparison.md`, then `.../2/comparison.md`, `.../3/comparison.md`, etc. |
| SoC | `output/soc/1/comparison.md`, then `.../2/comparison.md`, `.../3/comparison.md`, etc. |
| Clinical Summary | `output/clinical_summary/1/comparison.md`, then `.../2/comparison.md`, `.../3/comparison.md`, etc. |
| Case Management | `output/case_management/1/comparison.md`, then `.../2/comparison.md`, `.../3/comparison.md`, etc. |
| Scout | `output/scout/1/comparison.md`, then `.../2/comparison.md`, `.../3/comparison.md`, etc. |
| Segments | `output/segments/1/comparison.md`, then `.../2/comparison.md`, `.../3/comparison.md`, etc. |

The report includes an overall result, a summary by severity, details of
missing or changed information, and additional information found in the actual
JSON.

## Project structure

```text
.
├── run_comparator.py
├── comparators/
│   ├── semantic.py
│   ├── medical_timeline/
│   │   ├── medical_timeline.py
│   │   └── prompt.txt
│   ├── soc/
│   │   ├── soc.py
│   │   └── prompt.txt
│   └── ...
├── input/
│   ├── medical_timeline/
│   ├── soc/
│   ├── clinical_summary/
│   ├── case_management/
│   ├── scout/
│   ├── segments/
│   └── source/
└── output/
```

Each report input folder is under `input/`. Tracked example templates are
provided where available; copy them to the ignored `json1.json` and
`json2.json` working files before running a comparison. Scout also reads
`input/scout/question.txt`. The source evidence index is
`input/source/source.json`.

Each comparator lives in its own folder under `comparators/`, alongside its
`prompt.txt`. `comparators/semantic.py` provides shared JSON loading and
comparison-prompt logic.
