# persona_manager.py — Persona loading/saving for Friday/Mr. Clean
import json
import os

PERSONA_PATH = os.path.join(os.path.dirname(__file__), "memory", "persona_mr_clean.json")

def load_persona():
    with open(PERSONA_PATH, "r") as f:
        return json.load(f)

def save_persona(persona):
    with open(PERSONA_PATH, "w") as f:
        json.dump(persona, f, indent=2)
