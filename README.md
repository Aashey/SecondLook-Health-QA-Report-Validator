<<<<<<< HEAD
# QA-Report-Validator
QA regression validation tool for medical case reports, enabling automated and AI-assisted comparison of generated reports and their underlying data to identify content differences, missing information, and unexpected changes across releases.
=======
# Python JSON Semantic Comparator

This project compares expected JSON (`json1.json`) against actual JSON
(`json2.json`) using report-specific rules and the local Claude Code CLI.

It does NOT use the Claude API.

## Requirements

- Python 3.10+
- Claude Code CLI installed and available as `claude`
- Run from the project root

Test Claude Code:

```powershell
claude --version
```

## Folder structure

```text
pythonJudge/
├── run_comparator.py
├── comparators/
│   ├── __init__.py
│   ├── semantic.py
│   ├── medical_timeline.py
│   ├── soc.py
│   ├── clinical_summary.py
│   ├── case_management.py
│   └── scout.py
├── medical_timeline/
│   ├── json1.json
│   └── json2.json
├── soc/
│   ├── json1.json
│   └── json2.json
├── clinical_summary/
│   ├── json1.json
│   └── json2.json
├── case_management/
│   ├── json1.json
│   └── json2.json
├── scout/
│   ├── json1.json
│   └── json2.json
└── reports/
```

Put your own JSON files into the five report folders.

## Run individually

Medical Timeline:

```powershell
python .\run_comparator.py timeline
```

SoC:

```powershell
python .\run_comparator.py soc
```

Clinical Summary:

```powershell
python .\run_comparator.py clinical_summary
```

Case Management:

```powershell
python .\run_comparator.py case_management
```

Scout:

```powershell
python .\run_comparator.py scout
```

## Output

Claude's result is saved automatically to:

```text
reports/medical_timeline-comparison.md
reports/soc-comparison.md
reports/clinical_summary-comparison.md
reports/case_management-comparison.md
reports/scout-comparison.md
```

## Important

`comparators/medical_timeline.py` is the Python comparator.

`medical_timeline/json1.json` and `medical_timeline/json2.json` are the
input data.

They intentionally have similar names but are different things.
>>>>>>> d7ed181 (Initialization)
