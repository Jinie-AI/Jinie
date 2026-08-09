import sys
import os
from datetime import datetime

sys.path.insert(0, ".")
sys.path.insert(0, "backend")
sys.path.insert(0, "backend/srs")

from pipeline import run_srs_pipeline


prompt = "Build me a food delivery app where users can browse restaurants, order food, and track delivery"
# prompt = input("Describe your app idea: ")

result = run_srs_pipeline(prompt)

print("\n===== SRS OUTPUT =====")

print(
    "Functional Requirements:",
    len(result.functional_requirements.requirements)
)

for fr in result.functional_requirements.requirements:
    print(" -", fr.fr_id, ":", fr.description)

print(
    "\nScreens:",
    [n.screen_name for n in result.sitemap.nodes]
)

print(
    "Entities:",
    [e.name for e in result.entities.entities]
)

print(
    "Tech Stack:",
    result.tech_stack.state_management,
    "|",
    result.tech_stack.ui_library,
    "|",
    result.tech_stack.backend_service
)


# --------------------------------------------------
# CREATE OUTPUT FOLDER
# --------------------------------------------------

output_dir = "srs_outputs"
os.makedirs(output_dir, exist_ok=True)


# --------------------------------------------------
# CREATE UNIQUE FILE NAME
# --------------------------------------------------

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

json_path = os.path.join(
    output_dir,
    f"srs_{timestamp}.json"
)


# --------------------------------------------------
# SAVE SRS
# --------------------------------------------------

with open(json_path, "w", encoding="utf-8") as f:
    f.write(result.model_dump_json(indent=2))


print("\nFull SRS saved to:")
print(json_path)