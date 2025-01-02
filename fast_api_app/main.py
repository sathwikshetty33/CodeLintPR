from typing import Optional

from fastapi import FastAPI, status
from pydantic import BaseModel
app = FastAPI()

class Analyze(BaseModel):
    repo : str
    prnum : int
    githubtok : Optional[str] = None


@app.post("/start_task")
async def start_task_endpoint(task_request : Analyze):
    data = {
        "repo_url" : task_request.repo,
        "pr_num" : task_request.prnum,
        "Github_token" : task_request.githubtok,
    }
    print(data)
    return {"task_id" : "123", "status" : "Task started"}
