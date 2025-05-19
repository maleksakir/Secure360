from fastapi import APIRouter
from pydantic import BaseModel
from database import SessionLocal
from models import ScanTask, ScanResult
import subprocess, os, uuid

router = APIRouter(prefix="/gitleaks", tags=["GitLeaks"])

class GitLeaksScanRequest(BaseModel):
    repo_url: str

@router.post("/scan")
def run_gitleaks_scan(request: GitLeaksScanRequest):
    db = SessionLocal()
    task = ScanTask(scan_type="gitleaks", status="running")
    db.add(task)
    db.commit()
    db.refresh(task)

    repo = request.repo_url
    local_path = f"/tmp/{uuid.uuid4()}"
    os.system(f"git clone {repo} {local_path}")

    result = subprocess.run([
        "docker", "run", "--rm",
        "-v", f"{local_path}:/repo",
        "zricethezav/gitleaks",
        "detect", "--source=/repo", "--no-git"
    ], capture_output=True)

    output = result.stdout.decode() + result.stderr.decode()

    db_result = ScanResult(task_id=task.id, result=output)
    db.add(db_result)
    task.status = "completed"
    db.commit()
    return {"task_id": task.id, "output": output[:1000]}

@router.get("/results")
def get_gitleaks_results():
    db = SessionLocal()
    return db.query(ScanResult).filter_by(scan_type="gitleaks").order_by(ScanResult.created_at.desc()).all()

