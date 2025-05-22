from groq import Groq
import json
import os
import logging
from django.conf import settings

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

GROQ_API_KEY = settings.GROQ_API_KEY

def file_content_with_llm(filecontent, filename):
    """
    Analyze file content using Groq LLM and return a list of identified issues,
    including security vulnerabilities like API key exposure, SQL injection, etc.
    """
    logger.debug(f"Processing file: {filename}")

    if filename.endswith('.DS_Store'):
        logger.debug(f"Skipping .DS_Store file: {filename}")
        return {"issues": []}

    prompt = f"""
You are a secure code analysis tool.

Analyze the following source code for any potential issues. Check for:
- Security vulnerabilities (e.g., hardcoded secrets, input validation, prompt injection, XSS, SQL injection, CSRF, sensitive data exposure, insecure error handling, etc.)
- Coding style issues
- Bugs
- Performance problems
- Violations of best practices

Only return a **valid JSON** object in this exact format:
{{
    "issues": [
        {{
            "type": "security",  // or one of: style, bugs, performance, best_practice
            "line": "12",
            "description": "Brief description of the issue",
            "suggestion": "How to fix it"
        }}
    ]
}}

If no issues are found, return exactly: {{"issues": []}}

File: {filename}
Content:
{filecontent}
"""

    try:
        client = Groq(api_key=GROQ_API_KEY)

        try:
            completion = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": "user", "content": prompt}],
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

        try:
            json_start = raw_response.find('{')
            json_end = raw_response.rfind('}') + 1

            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON object found in response")

            potential_json = raw_response[json_start:json_end]

            for pattern in ['```json', '```', 'json']:
                potential_json = potential_json.replace(pattern, '').strip()

            parsed_response = json.loads(potential_json)

            if not isinstance(parsed_response, dict):
                raise ValueError("Response is not a dictionary")

            if 'issues' not in parsed_response:
                raise ValueError("Response missing 'issues' key")

            valid_types = {"security", "style", "bugs", "performance", "best_practice"}
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
