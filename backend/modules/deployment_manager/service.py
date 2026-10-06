"""Module 09: execute Firebase Hosting deployment and record results."""
import json
import shutil
import subprocess
from modules.utilities import store
from modules.logger.events import log, now

def deploy_project(p, pid, project):
    try:
        base = store.folder(pid)
        (base / "firebase.json").write_text(
            json.dumps(
                {
                    "hosting": {
                        "public": p.get("preview_directory", "preview"),
                        "ignore": ["**/.*"],
                        "rewrites": [
                            {"source": "**", "destination": "/index.html"}
                        ],
                    }
                }
            )
        )
        result = subprocess.run(
            [
                shutil.which("firebase"),
                "deploy",
                "--only",
                "hosting",
                "--project",
                project,
                "--non-interactive",
                "--json",
            ],
            cwd=base,
            capture_output=True,
            text=True,
            timeout=240,
        )
        if result.returncode:
            raise RuntimeError(result.stderr[-2000:] or result.stdout[-2000:])
        response = json.loads(result.stdout)
        if response.get("status") != "success":
            raise RuntimeError("Firebase did not report a successful deployment.")
        p["deployment"] = {
            "url": "https://" + project + ".web.app",
            "time": now(),
            "revision": p["revision"],
            "build_id": pid + "-" + str(p["build_revision"]),
        }
        p["status"] = "ready"
        log(p, "deployment", "Firebase Hosting deployment succeeded.")
    except Exception as e:
        p["status"] = "ready"
        p["error"] = str(e)
        log(p, "error", "Deployment failed: " + str(e))
