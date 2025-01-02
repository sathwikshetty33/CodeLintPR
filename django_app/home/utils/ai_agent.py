from groq import Groq
import json
import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

GROQ_API_KEY = "your api key"


def file_content_with_llm(filecontent, filename):
    """
    Analyze file content using Groq LLM and properly return the analysis results.
    """
    logger.debug(f"Processing file: {filename}")

    # First, check if the file is actually a code file that should be analyzed
    if filename.endswith('.DS_Store'):
        logger.debug(f"Skipping .DS_Store file: {filename}")
        return {"issues": []}

    prompt = f"""Analyze this code and return a JSON object with any issues found.

File: {filename}
Content:
{filecontent}

Return ONLY a valid JSON object in this exact format, with no additional text:
{{
    "issues": [
        {{
            "type": "style",
            "line": "1",
            "description": "Issue description here",
            "suggestion": "How to fix it here"
        }}
    ]
}}

Only use these types: "style", "bugs", "performance", "best_practice"
If no issues found, return: {{"issues": []}}"""

    try:
        client = Groq(api_key=GROQ_API_KEY)

        # Add error handling for API call
        try:
            completion = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                temperature=0.0,
                top_p=1,
            )
        except Exception as api_error:
            logger.error(f"Groq API error: {str(api_error)}")
            return {
                "error": "API_ERROR",
                "message": str(api_error),
                "issues": []
            }

        raw_response = completion.choices[0].message.content.strip()
        logger.debug(f"Raw API response: {raw_response}")

        # More robust JSON extraction
        try:
            # Find the first { and last }
            json_start = raw_response.find('{')
            json_end = raw_response.rfind('}') + 1

            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON object found in response")

            potential_json = raw_response[json_start:json_end]

            # Remove any markdown code block indicators
            for pattern in ['```json', '```', 'json']:
                potential_json = potential_json.replace(pattern, '').strip()

            # Parse the JSON response
            parsed_response = json.loads(potential_json)

            # Validate the response structure
            if not isinstance(parsed_response, dict):
                raise ValueError("Response is not a dictionary")

            if 'issues' not in parsed_response:
                raise ValueError("Response missing 'issues' key")

            # Validate issue types and required fields
            valid_types = {"style", "bugs", "performance", "best_practice"}
            required_fields = {'type', 'line', 'description', 'suggestion'}

            valid_issues = []
            for issue in parsed_response['issues']:
                if not isinstance(issue, dict):
                    logger.warning(f"Skipping invalid issue format: {issue}")
                    continue

                if all(field in issue for field in required_fields) and issue['type'] in valid_types:
                    valid_issues.append({
                        "type": issue['type'],
                        "line": issue['line'],
                        "description": issue['description'],
                        "suggestion": issue['suggestion']
                    })
                else:
                    logger.warning(f"Skipping issue with missing/invalid fields: {issue}")

            result = {"issues": valid_issues}
            logger.debug(f"Returning validated issues for {filename}: {json.dumps(result, indent=2)}")
            return result

        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"JSON processing error for {filename}: {str(e)}")
            logger.error(f"Problematic response: {raw_response}")
            return {
                "error": "JSON_PROCESSING_ERROR",
                "message": str(e),
                "issues": []
            }

    except Exception as e:
        logger.error(f"Unexpected error processing {filename}: {str(e)}")
        return {
            "error": "UNEXPECTED_ERROR",
            "message": str(e),
            "issues": []
        }