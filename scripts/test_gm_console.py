from ia_engine.gpt_engine.gpt_engine import LLMEngine as GPTEngine
from ia_engine.prompts.gm.service import GMService

from scripts.dummy_story_service import DummyStoryService

from dotenv import load_dotenv
load_dotenv()

import os
print("AZURE_OPENAI_ENDPOINT =", os.getenv("AZURE_OPENAI_ENDPOINT"))
print("AZURE_OPENAI_API_KEY =", "SET" if os.getenv("AZURE_OPENAI_API_KEY") else "NONE")
# ---- Dummy Character Store ----
class DummyCharacterStore:
    def __init__(self):
        self._character = {
            "stats": {
                "name": "Demo",
                "class": "Viajero",
                "level": 1
            },
            "state": {
                "location": "taberna",
                "hp": 10
            },
            "story": {
                "c": {},
                "g": {},
                "e": {}
            }
        }

    def load(self, character_id: str):
        return self._character

    def save(self, character_id: str, character: dict):
        self._character = character
        print("\n=== STORY UPDATED ===")
        print(character["story"])

def main():
    from dotenv import load_dotenv
    from pathlib import Path
    import os

    # Cargar .env desde la raíz del proyecto
    ROOT = Path(__file__).resolve().parents[1]
    load_dotenv(dotenv_path=ROOT / ".env")

    engine = GPTEngine()
    story_service = DummyStoryService()
    store = DummyCharacterStore()

    gm = GMService(
        llm_engine=engine,
        story_service=story_service,
        character_store=store,
        world_rules="Fantasía oscura, magia con costo real.",
    )

    character_id = "demo"
    print("\nChat GM (escribí /exit para salir)\n")

    while True:
        msg = input("Vos> ").strip()
        if not msg:
            continue
        if msg.lower() in {"/exit", "exit", "quit"}:
            print("Saliendo...")
            break

        out = gm.run_turn(character_id=character_id, player_message=msg)

        print("\nGM> " + out.reply + "\n")

if __name__ == "__main__":
    main()
