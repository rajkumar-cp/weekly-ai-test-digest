# Weekly AI Test Digest

A Python command-line tool that validates weekly test execution results, calculates summary metrics, asks the OpenAI API for data-grounded observations, and saves an email preview.

## Requirements

- Python 3
- An OpenAI API key with access to the model configured in `src/ai_analyzer.py` (`gpt-6-luna`)

## Setup

From the project root, create and activate a virtual environment, then install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Create a `.env` file in the project root and add your API key:

```dotenv
OPENAI_API_KEY=your_api_key_here
```

Keep the key private. `.env` is excluded by `.gitignore`.

## Input data

The program reads `data/weekly_test_results.csv`. The CSV must contain these columns:

| Column | Description |
| --- | --- |
| `date` | Execution date in `YYYY-MM-DD` or `MM/DD/YYYY` format |
| `total_tests` | Number of tests executed; must be positive |
| `passed` | Number of passed tests; must be zero or greater |
| `failed` | Number of failed tests; must be zero or greater |

Each row must satisfy `passed + failed = total_tests`. Dates must be unique and all rows must fall within the same ISO week. The file may include a UTF-8 byte-order mark.

## Run

From the project root:

```powershell
python .\src\main.py
```

The script prints the weekly totals, pass/failure rates, and daily results. It then requests observations from the OpenAI API and saves an email preview to:

```text
output/weekly_digest.eml
```

The message is not sent. The recipient and sender are currently placeholders in `src/main.py`; update them before relying on the preview.

## Project layout

```text
data/
  weekly_test_results.csv
output/
src/
  ai_analyzer.py
  email_generator.py
  main.py
requirements.txt
```
