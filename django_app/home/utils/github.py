import requests
from urllib.parse import urlparse
import uuid
from .ai_agent import file_content_with_llm


def get_owner(url):
    """
    Extracts the owner and repository name from the GitHub repository URL.
    """
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.strip("/").split("/")
    if len(path_parts) >= 2:
        owner, repo = path_parts[0], path_parts[1]
        return owner, repo
    return None, None


def fetch_pr_files(repo_url, pr_num, github_token):
    """
    Fetch files from a specific pull request.
    """
    owner, repo = get_owner(repo_url)
    if not owner or not repo:
        raise ValueError("Invalid repository URL")

    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_num}/files"
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json",
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP Error fetching PR files: {http_err}")
        print(f"Response content: {response.text}")
        raise
    except Exception as err:
        print(f"Error fetching PR files: {err}")
        raise


def fetch_file_content(raw_url, github_token):
    """
    Fetch raw file content directly using GitHub API token.
    """
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3.raw",
    }

    try:
        response = requests.get(raw_url, headers=headers)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Request error while fetching file content: {e}")
        raise


def any_pr(repo_url, pr_num, github_token):
    """
    Analyzes the files in a pull request.
    """
    task_id = str(uuid.uuid4())
    try:
        pr_files = fetch_pr_files(repo_url, pr_num, github_token)
        analysis_result = []

        for file in pr_files:
            filename = file['filename']
            raw_url = file.get('raw_url')

            if not raw_url:
                analysis_result.append({"results": "Raw URL not available", "filename": filename})
                continue

            try:
                # Fetch content directly using GitHub API
                raw_content = fetch_file_content(raw_url, github_token)

                if not raw_content:
                    analysis_result.append({"results": "Empty file content", "filename": filename})
                    continue

                # Analyze the file content
                analysis = file_content_with_llm(raw_content,
                                                 filename) if 'file_content_with_llm' in globals() else "No analysis function available"
                analysis_result.append({"results": analysis, "filename": filename})
                print("the analysis is", analysis)
            except Exception as file_err:
                print(f"Error processing file {filename}: {file_err}")
                analysis_result.append({"results": f"Error fetching content: {str(file_err)}", "filename": filename})

        return {"task_id": task_id, "results": analysis_result}
    except Exception as e:
        print(f"Error processing PR: {e}")
        return {"task_id": task_id, "results": "An error occurred. Verify the URL, token, or PR existence."}