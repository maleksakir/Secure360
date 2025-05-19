from fastapi import APIRouter
from pydantic import BaseModel
from database import SessionLocal
from models import ScanTask, ScanResult
import subprocess, os, uuid

router = APIRouter(prefix="/scan", tags=["Scan"])

class ScanRequest(BaseModel):
    repo_url: str = None

@router.post("/{scan_type}")
def run_scan(scan_type: str, request: ScanRequest):
    db = SessionLocal()
    task = ScanTask(scan_type=scan_type, status="running")
    db.add(task)
    db.commit()
    db.refresh(task)

    output = ""
    local_path = f"/tmp/{uuid.uuid4()}"

    if scan_type == "secrets":
        repo = request.repo_url or "https://github.com/example/repo.git"
        os.system(f"git clone {repo} {local_path}")
        result = subprocess.run([
            "docker", "run", "--rm",
            "-v", f"{local_path}:/repo",
            "zricethezav/gitleaks",
            "detect", "--source=/repo", "--no-git"
        ], capture_output=True)
        output = result.stdout.decode() + result.stderr.decode()

    elif scan_type == "code":
        os.system(f"git clone https://github.com/example/repo.git {local_path}")
        result = subprocess.run([
            "docker", "run", "--rm",
            "-v", f"{local_path}:/src",
            "returntocorp/semgrep",
            "--config=auto", "/src"
        ], capture_output=True)
        output = result.stdout.decode() + result.stderr.decode()

    elif scan_type == "cve":
        result = subprocess.run([
            "docker", "run", "--rm",
            "aquasec/trivy", "image", "python:3.10"
        ], capture_output=True)
        output = result.stdout.decode() + result.stderr.decode()

    elif scan_type == "web":
        result = subprocess.run([
            "docker", "exec", "zap", "zap-cli", "quick-scan", "http://example.com"
        ], capture_output=True)
        output = result.stdout.decode() + result.stderr.decode()

    elif scan_type == "cloud":
        result = subprocess.run([
            "docker", "exec", "prowler", "./prowler"
        ], capture_output=True)
        output = result.stdout.decode() + result.stderr.decode()

    else:
        output = f"Scan type '{scan_type}' is not supported."

    db_result = ScanResult(task_id=task.id, result=output)
    db.add(db_result)
    task.status = "completed"
    db.commit()
    return {"task_id": task.id, "output": output[:1000]}

@router.get("/results")
def get_results():
    db = SessionLocal()
    return db.query(ScanResult).order_by(ScanResult.created_at.desc()).all()
