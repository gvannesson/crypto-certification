from PIL import Image
from pathlib import Path

D = Path("rapports/assets_ci")

# (source, destination, boite de recadrage) — coordonnees relevees sur les captures 1600x1200
CROPS = [
    # Vue d'ensemble : du titre du run jusqu'au bas du graphe de jobs (avant "Annotations")
    ("ci_run_overview.png", "crop_ci_overview.png", (24, 190, 1590, 900)),
    # Pages de detail : titre + liste des jobs a gauche + etapes du job, sans le vide en bas
    ("ci_job_build_webapp.png", "crop_ci_build_webapp.png", (24, 190, 1590, 800)),
    ("ci_job_deploy_webapp.png", "crop_ci_deploy_webapp.png", (24, 190, 1590, 800)),
    ("ci_job_build_ml_api.png", "crop_ci_build_ml_api.png", (24, 190, 1590, 800)),
    ("ci_job_tests_bloc4.png", "crop_ci_tests_bloc4.png", (24, 190, 1590, 800)),
    ("ci_job_lint.png", "crop_ci_lint.png", (24, 190, 1590, 800)),
]

for src, dst, box in CROPS:
    im = Image.open(D / src).crop(box)
    im.save(D / dst)
    print(f"{dst}  {im.size}")
