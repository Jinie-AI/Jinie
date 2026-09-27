"""Project-scoped EAS jobs. Secrets stay in the backend environment."""

import json
import os
import shutil
import subprocess
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from . import store

router = APIRouter(prefix="/api/projects")


class MobileSettings(BaseModel):
    expo_project_id: uuid.UUID
    owner: str = Field(pattern=r"^[A-Za-z0-9_-]{1,64}$")
    slug: str = Field(pattern=r"^[a-z0-9][a-z0-9-]{0,63}$")
    android_package: str = Field(pattern=r"^[a-z][a-z0-9_]*(?:[.][a-z][a-z0-9_]*)+$")
    ios_bundle: str = Field(
        pattern=r"^[A-Za-z][A-Za-z0-9-]*(?:[.][A-Za-z][A-Za-z0-9-]*)+$"
    )
    asc_app_id: str = Field(default="", pattern=r"^\d*$")
    credentials_ready: bool = False


class SubmitRequest(BaseModel):
    platform: Literal["android", "ios", "all"]


def project(pid):
    try:
        return store.get(pid)
    except KeyError:
        raise HTTPException(404, "Project not found")


def preflight(p, platform):
    issues = []
    settings = p.get("mobile_settings")
    if not settings:
        issues.append("Save the Expo project and app identifiers below.")
    else:
        if not settings.get("credentials_ready"):
            issues.append("Complete EAS signing and store credential setup first.")
        if platform in ("ios", "all") and not settings.get("asc_app_id"):
            issues.append("Add the App Store Connect numeric app ID.")
    if not shutil.which("eas"):
        issues.append("Install eas-cli on the backend machine.")
    if not os.getenv("EXPO_TOKEN"):
        issues.append("Set EXPO_TOKEN in the backend environment and restart it.")
    key = os.getenv("JINIE_GOOGLE_SERVICE_ACCOUNT_FILE")
    if key and platform in ("android", "all") and not Path(key).is_file():
        issues.append("The configured Google service account file is unavailable.")
    if p.get("build_revision") is None or p.get("build_revision") != p["revision"]:
        issues.append("Accept your screens and build the current revision first.")
    if p["status"] in ("building", "deploying"):
        issues.append("A build or deployment is already running.")
    if p["status"] not in ("ready", "building", "deploying"):
        issues.append("Finish a successful current build before submitting.")
    return issues


@router.get("/{pid}/mobile-deployment")
def status(pid: str):
    p = project(pid)
    return {
        "settings": p.get("mobile_settings"),
        "job": p.get("mobile_deployment"),
        "checks": {
            target: preflight(p, target) for target in ("android", "ios", "all")
        },
    }


@router.put("/{pid}/mobile-deployment/settings")
def configure(pid: str, settings: MobileSettings):
    with store.LOCK:
        p = project(pid)
        if p["status"] in ("building", "deploying"):
            raise HTTPException(409, "Wait for the current job to finish.")
        p["mobile_settings"] = settings.model_dump(mode="json")
        store.save(p)
    return status(pid)


def update_job(pid, job_id, **changes):
    with store.LOCK:
        p = project(pid)
        if p.get("mobile_deployment", {}).get("id") != job_id:
            return
        p["mobile_deployment"].update(
            changes, updated_at=datetime.now(timezone.utc).isoformat()
        )
        if changes.get("state") in ("submitted", "failed"):
            p["status"] = "ready"
        store.save(p)


def run_eas(args, cwd):
    result = subprocess.run(
        [shutil.which("eas"), *args],
        cwd=cwd,
        env={**os.environ, "EAS_NO_VCS": "1", "CI": "1"},
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=7200,
    )
    if result.returncode:
        # CLI output can include account details; never return raw logs to the browser.
        raise RuntimeError(
            "EAS rejected the job. Check your Expo dashboard, signing credentials and store permissions, then retry."
        )
    return result.stdout


def work(pid, job_id, platform):
    try:
        p = project(pid)
        settings = p["mobile_settings"]
        source = store.folder(pid) / "source"
        target = store.folder(pid) / "mobile-jobs" / job_id
        shutil.copytree(
            source,
            target,
            ignore=shutil.ignore_patterns(
                "node_modules", ".git", ".env*", "model-candidates"
            ),
        )
        app = json.loads((target / "app.json").read_text(encoding="utf-8"))
        expo = app["expo"]
        expo.update(owner=settings["owner"], slug=settings["slug"])
        expo.setdefault("extra", {}).setdefault("eas", {})["projectId"] = settings[
            "expo_project_id"
        ]
        expo.setdefault("android", {})["package"] = settings["android_package"]
        expo.setdefault("ios", {}).update(
            bundleIdentifier=settings["ios_bundle"], supportsTablet=True
        )
        (target / "app.json").write_text(json.dumps(app, indent=2), encoding="utf-8")
        android = {"track": "internal", "releaseStatus": "completed"}
        key = os.getenv("JINIE_GOOGLE_SERVICE_ACCOUNT_FILE")
        if key:
            android["serviceAccountKeyPath"] = str(Path(key).resolve())
        eas = {
            "cli": {"appVersionSource": "remote"},
            "build": {"production": {"distribution": "store", "autoIncrement": True}},
            "submit": {
                "production": {
                    "android": android,
                    "ios": {"ascAppId": settings["asc_app_id"]},
                }
            },
        }
        (target / "eas.json").write_text(json.dumps(eas, indent=2), encoding="utf-8")
        (target / ".easignore").write_text(
            "node_modules\n.env*\nmodel-candidates\npreview.jsx\n", encoding="utf-8"
        )
        update_job(
            pid,
            job_id,
            state="building",
            message="Building signed store binaries with Expo.",
        )
        raw = run_eas(
            [
                "build",
                "--platform",
                platform,
                "--profile",
                "production",
                "--non-interactive",
                "--wait",
                "--json",
            ],
            target,
        )
        builds = json.loads(raw)
        if isinstance(builds, dict):
            builds = [builds]
        expected = {"ANDROID", "IOS"} if platform == "all" else {platform.upper()}
        if {b.get("platform") for b in builds} != expected or any(
            b.get("status") != "FINISHED" for b in builds
        ):
            raise RuntimeError(
                "EAS did not report completed builds for every selected platform."
            )
        links = []
        for build in builds:
            build_id = str(uuid.UUID(build["id"]))
            links.append(
                {
                    "platform": build["platform"].lower(),
                    "url": f"https://expo.dev/accounts/{settings['owner']}/projects/{settings['slug']}/builds/{build_id}",
                }
            )
        update_job(
            pid,
            job_id,
            state="submitting",
            message="Uploading to the selected store testing destinations.",
            builds=links,
        )
        for build in builds:
            run_eas(
                [
                    "submit",
                    "--platform",
                    build["platform"].lower(),
                    "--id",
                    str(uuid.UUID(build["id"])),
                    "--profile",
                    "production",
                    "--non-interactive",
                    "--wait",
                ],
                target,
            )
        update_job(
            pid,
            job_id,
            state="submitted",
            message="Upload completed. Check TestFlight / Play internal testing for processing. Public store review and release remain separate.",
        )
    except subprocess.TimeoutExpired:
        update_job(
            pid,
            job_id,
            state="failed",
            message="Timed out waiting for EAS. Check Expo before retrying; the remote job may still be running.",
        )
    except Exception as exc:  # noqa: BLE001 - persist a terminal state for background jobs
        message = (
            str(exc)
            if isinstance(exc, RuntimeError)
            else "Deployment could not complete. Verify project configuration and inspect the Expo dashboard before retrying."
        )
        update_job(pid, job_id, state="failed", message=message)


@router.post("/{pid}/mobile-deployment", status_code=202)
def submit(pid: str, request: SubmitRequest):
    with store.LOCK:
        p = project(pid)
        issues = preflight(p, request.platform)
        if issues:
            raise HTTPException(409, " ".join(issues))
        job_id = uuid.uuid4().hex
        p["mobile_deployment"] = {
            "id": job_id,
            "platform": request.platform,
            "revision": p["revision"],
            "state": "queued",
            "message": "Deployment queued.",
            "builds": [],
        }
        p["status"] = "deploying"
        store.save(p)
    threading.Thread(
        target=work, args=(pid, job_id, request.platform), daemon=True
    ).start()
    return status(pid)
