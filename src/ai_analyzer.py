
import json

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


def generate_ai_observations(metrics):
    client = OpenAI()

    metrics_json = json.dumps(metrics, indent=2, default=str)

    instructions = """
You are an experienced test automation reporting analyst.

Analyse the supplied weekly test execution metrics.

Rules:
1. Use only the supplied data.
2. Do not invent root causes or explanations.
3. Do not repeat the same observation.
4. Identify meaningful patterns or changes in the results.
5. If the data does not support a meaningful conclusion, say so.
6. Return valid JSON with an "observations" key.
7. The observations value must be a list of short strings.
"""

    response = client.responses.create(
        model="gpt-6-luna",
        instructions=instructions,
        input=f"Analyse these weekly test metrics:\n{metrics_json}"
    )

    try:
        result = json.loads(response.output_text)
    except json.JSONDecodeError as error:
        raise ValueError("AI did not return valid JSON.") from error

    observations = result.get("observations")

    if (
        not isinstance(observations, list)
        or not observations
        or not all(
            isinstance(item, str) and item.strip()
            for item in observations
        )
    ):
        raise ValueError("AI returned an invalid observations list.")

    return observations
