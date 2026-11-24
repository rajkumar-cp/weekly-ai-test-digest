
import csv
from datetime import date, datetime
from pathlib import Path
from email_generator import create_email, save_email_preview
from ai_analyzer import generate_ai_observations


# Locate the project folder independently of the terminal's location.
PROJECT_DIR = Path(__file__).resolve().parent.parent
CSV_FILE = PROJECT_DIR / "data" / "weekly_test_results.csv"

REQUIRED_COLUMNS = {
    "date",
    "total_tests",
    "passed",
    "failed",
}


def validate_and_read_csv(file_path):
    """Read the CSV and reject invalid execution records."""

    if not file_path.exists():
        raise FileNotFoundError(f"CSV file not found: {file_path}")

    records = []
    errors = []
    seen_dates = set()
    reporting_weeks = set()

    with file_path.open("r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        # Check whether all required columns exist.
        if not reader.fieldnames:
            raise ValueError("CSV file is empty or has no header.")

        missing_columns = REQUIRED_COLUMNS - set(reader.fieldnames)

        if missing_columns:
            raise ValueError(
                f"Missing required columns: {sorted(missing_columns)}"
            )

        for row_number, row in enumerate(reader, start=2):
            try:
                # Validate date.
                date_text = row["date"].strip()
                try:
                    execution_date = date.fromisoformat(date_text)
                except ValueError:
                    execution_date = datetime.strptime(
                        date_text, "%m/%d/%Y"
                    ).date()

                # Validate numerical fields.
                total = int(row["total_tests"])
                passed = int(row["passed"])
                failed = int(row["failed"])

                if total <= 0:
                    raise ValueError("total_tests must be positive.")

                if passed < 0 or failed < 0:
                    raise ValueError("passed and failed cannot be negative.")

                # Validate the business rule.
                if passed + failed != total:
                    raise ValueError(
                        "passed + failed must equal total_tests."
                    )

                # Check duplicate dates.
                if execution_date in seen_dates:
                    raise ValueError("Duplicate execution date.")

                seen_dates.add(execution_date)

                # Check that all records belong to the same ISO week.
                iso_year, iso_week, _ = execution_date.isocalendar()
                reporting_weeks.add((iso_year, iso_week))

                records.append({
                    "date": execution_date,
                    "total_tests": total,
                    "passed": passed,
                    "failed": failed,
                })

            except (ValueError, TypeError, AttributeError) as error:
                errors.append(f"Row {row_number}: {error}")

    if not records:
        errors.append("No valid execution records found.")

    if len(reporting_weeks) > 1:
        errors.append("Records span more than one reporting week.")

    if errors:
        raise ValueError(
            "CSV validation failed:\n- " + "\n- ".join(errors)
        )

    return sorted(records, key=lambda record: record["date"])


def calculate_metrics(records):
    """Calculate weekly and daily execution metrics."""

    total_tests = sum(record["total_tests"] for record in records)
    passed_tests = sum(record["passed"] for record in records)
    failed_tests = sum(record["failed"] for record in records)

    pass_rate = (passed_tests / total_tests) * 100
    failure_rate = (failed_tests / total_tests) * 100

    return {
        "total_tests": total_tests,
        "passed": passed_tests,
        "failed": failed_tests,
        "pass_rate": round(pass_rate, 2),
        "failure_rate": round(failure_rate, 2),
        "daily_results": records,
    }


def print_report(metrics):
    """Display the weekly execution report."""

    print("\n========== WEEKLY TEST EXECUTION REPORT ==========")

    print(f"Total tests : {metrics['total_tests']}")
    print(f"Passed      : {metrics['passed']}")
    print(f"Failed      : {metrics['failed']}")
    print(f"Pass rate   : {metrics['pass_rate']}%")
    print(f"Failure rate: {metrics['failure_rate']}%")

    print("\nDaily results:")

    for record in metrics["daily_results"]:
        print(
            f"{record['date']} | "
            f"Total: {record['total_tests']} | "
            f"Passed: {record['passed']} | "
            f"Failed: {record['failed']}"
        )

    print("==================================================\n")


def main():
    try:
        records = validate_and_read_csv(CSV_FILE)
        metrics = calculate_metrics(records)
        print_report(metrics)
        ai_observations = generate_ai_observations(metrics)
        daily_results = metrics["daily_results"]
        daily_failures = [record["failed"] for record in daily_results]
        latest_result = daily_results[-1]



        email_message = create_email(
            metrics=metrics,
            ai_observations=ai_observations,
            recipient="your-test-email@example.com",
            sender="weekly-digest@example.com",
        )

        save_email_preview(email_message)

    except (FileNotFoundError, ValueError) as error:
        print(f"\nERROR: {error}")


if __name__ == "__main__":
    main()
