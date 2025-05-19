from celery import Celery

app = Celery("worker", broker="redis://redis:6379/0")

@app.task
def run_semgrep():
    import subprocess
    return subprocess.run(["docker", "exec", "semgrep", "semgrep", "--config=auto", "/code"], capture_output=True).stdout.decode()
