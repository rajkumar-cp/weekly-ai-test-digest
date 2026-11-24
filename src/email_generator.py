
from email.message import EmailMessage
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_DIR / "output"


def generate_subject(metrics):
    """Generate the email subject using Python."""

    daily_results = metrics["daily_results"]

    start_date = daily_results[0]["date"]
    end_date = daily_results[-1]["date"]

    return (
        f"Weekly Test Automation Summary - "
        f"{start_date:%d %b} to {end_date:%d %b %Y}"
    )


def generate_email_body(metrics, ai_observations):
    """Generate the email body using Python and AI observations."""

    daily_results = metrics["daily_results"]

    start_date = daily_results[0]["date"]
    end_date = daily_results[-1]["date"]

    body = f"""
Hello Team,

Here is the weekly test automation execution summary.

Reporting period: {start_date:%d %B %Y} to {end_date:%d %B %Y}

1. EXECUTION OVERVIEW

Total tests executed : {metrics['total_tests']}
Passed tests         : {metrics['passed']}
Failed tests         : {metrics['failed']}
Pass rate            : {metrics['pass_rate']}%
Failure rate         : {metrics['failure_rate']}%

2. AI-GENERATED OBSERVATIONS

"""

    for index, observation in enumerate(ai_observations, start=1):
        body += f"{index}. {observation}\n"

    body += """

3. ATTENTION REQUIRED

Please review the failed test cases and investigate
recurring failures where applicable.

Regards,
Weekly AI Test Execution Digest
"""

    return body


def create_email(metrics, ai_observations, recipient, sender):
    """Create a structured email message."""

    email = EmailMessage()

    email["Subject"] = generate_subject(metrics)
    email["From"] = sender
    email["To"] = recipient

    email.set_content(
        generate_email_body(metrics, ai_observations)
    )

    return email


def save_email_preview(email):
    """Save the email without sending it."""

    output_dir = OUTPUT_DIR
    if output_dir.exists() and not output_dir.is_dir():
        output_dir = PROJECT_DIR / "output_previews"
        print(
            f"'{OUTPUT_DIR}' is not a directory; "
            f"saving the preview to '{output_dir}' instead."
        )

    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "weekly_digest.eml"

    output_file.write_bytes(email.as_bytes())

    print(f"\nEmail preview saved to: {output_file}")

    return output_file
