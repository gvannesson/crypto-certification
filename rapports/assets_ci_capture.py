"""Captures des pages GitHub Actions pour les rapports E3 (C13) et E4 (C18, C19).

Le dépôt est public : les pages de run sont accessibles sans authentification.
Réutilise le Chrome système (channel="chrome") plutôt que de télécharger un navigateur.

    uv run --with playwright python rapports/assets_ci_capture.py <run_id>
"""

import json
import re
import sys
import urllib.request
from pathlib import Path

from playwright.sync_api import sync_playwright

REPO = "gvannesson/crypto-certification"
API = f"https://api.github.com/repos/{REPO}"
OUT = Path(__file__).parent / "assets_ci"

# Jobs dont on veut une capture détaillée, et nom de fichier associé.
WANTED = {
    "Bloc4 App — Tests": "tests_bloc4",
    "Lint — Ruff": "lint",
    "Build & Push — webapp (ghcr.io)": "build_webapp",
    "Build & Push — ml-api (ghcr.io)": "build_ml_api",
    "Deploy (verify pull) — webapp": "deploy_webapp",
}


def get(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.load(r)


def shoot(page, url, dest):
    page.goto(url, wait_until="networkidle", timeout=60000)
    page.wait_for_timeout(3000)
    page.screenshot(path=str(dest))
    print(f"  -> {dest.name}")


def main(run_id):
    OUT.mkdir(exist_ok=True)
    base = f"https://github.com/{REPO}/actions/runs/{run_id}"

    jobs = get(f"{API}/actions/runs/{run_id}/jobs?per_page=30")["jobs"]
    targets = [(j["id"], WANTED[j["name"]]) for j in jobs if j["name"] in WANTED]
    print(f"{len(jobs)} jobs, {len(targets)} captures détaillées prévues")

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome")
        page = browser.new_page(viewport={"width": 1600, "height": 1200})

        print("Vue d'ensemble :")
        shoot(page, base, OUT / "ci_run_overview.png")

        print("Détail des jobs :")
        for job_id, slug in targets:
            shoot(page, f"{base}/job/{job_id}", OUT / f"ci_job_{slug}.png")

        browser.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("usage: assets_ci_capture.py <run_id>")
    main(re.sub(r"\D", "", sys.argv[1]))
