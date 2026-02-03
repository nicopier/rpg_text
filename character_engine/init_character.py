from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

# Modelos Pydantic
from character_engine.models.inventory import InventoryModel
from character_engine.models.stats import StatsBaseModel, EquippedModel, StatsModel
from character_engine.models.state import TimeModel, StateModel
from character_engine.models.story import StoryModel


# -----------------------------
# Config / .env loader
# -----------------------------
def load_env_file(env_path: Path) -> None:
    """
    Cargador .env minimalista:
    - KEY=VALUE por línea
    - ignora comentarios y líneas vacías
    - no soporta export ni cosas complejas
    """
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def get_characters_root(project_root: Path) -> Path:
    load_env_file(project_root / ".env")
    base = os.getenv("CHARACTERS_DIR", "./characters").strip()

    base_path = Path(base)
    if base_path.is_absolute():
        return base_path.resolve()
    return (project_root / base_path).resolve()


# -----------------------------
# Validación de nombre
# -----------------------------
_NAME_RE = re.compile(r"^[A-Za-z0-9_-]{1,16}$")


def validate_character_name(name: str) -> str:
    cleaned = name.strip()
    if not cleaned:
        raise ValueError("Nombre de personaje vacío.")
    if len(cleaned) > 16:
        raise ValueError("El nombre del personaje no puede superar 16 caracteres.")
    if not _NAME_RE.match(cleaned):
        raise ValueError("Nombre inválido. Usá solo letras, números, '_' y '-' (1..16 chars).")
    return cleaned


# -----------------------------
# JSON writing
# -----------------------------
def write_model_json(path: Path, model: Any) -> None:
    """
    Pydantic v2: model_dump()
    Guardamos JSON bonito (indent=2, utf-8).
    """
    payload = model.model_dump()
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


# -----------------------------
# Crear personaje (plantillas iniciales)
# -----------------------------
def build_initial_models(
    *,
    level: int = 1,
    fuerza: int = 1,
    destreza: int = 1,
    inteligencia: int = 1,
    puntos_vida: int = 1,
    estres: int = 0,
) -> tuple[StatsModel, InventoryModel, StateModel, StoryModel]:
    stats_base = StatsBaseModel(
        level=level,
        fuerza=fuerza,
        destreza=destreza,
        inteligencia=inteligencia,
        puntos_vida=puntos_vida,  # base
        estres=estres,            # base
    )

    equipped = EquippedModel()  # todo None
    stats_model = StatsModel(stats=stats_base, equipped=equipped)

    inventory_model = InventoryModel(items=[])

    # HP actual inicia al máximo hardcodeado
    hp_max = 10 * level
    state_model = StateModel(
        location="start_zone",
        hp_current=hp_max,
        mana_current=0,
        time=TimeModel(day=1, hour=0),
    )

    # Story compacto por defecto
    story_model = StoryModel.default()
    # Opcional: setear un contexto inicial coherente con el estado
    story_model.c.l = "start_zone"
    story_model.c.a = "e"      # exploration
    story_model.c.s = "intro"  # scene id corto
    story_model.c.x = "none"
    story_model.c.p = "0"

    return stats_model, inventory_model, state_model, story_model


def init_character(
    project_root: Path,
    *,
    name: str,
    level: int = 1,
    fuerza: int = 1,
    destreza: int = 1,
    inteligencia: int = 1,
    puntos_vida: int = 1,
    estres: int = 0,
) -> Path:
    characters_root = get_characters_root(project_root)
    characters_root.mkdir(parents=True, exist_ok=True)

    char_dir = characters_root / name
    if char_dir.exists():
        raise FileExistsError(f"Ya existe el personaje '{name}' en: {char_dir}")

    char_dir.mkdir(parents=False, exist_ok=False)

    stats_model, inventory_model, state_model, story_model = build_initial_models(
        level=level,
        fuerza=fuerza,
        destreza=destreza,
        inteligencia=inteligencia,
        puntos_vida=puntos_vida,
        estres=estres,
    )

    write_model_json(char_dir / "stats.json", stats_model)
    write_model_json(char_dir / "inventory.json", inventory_model)
    write_model_json(char_dir / "state.json", state_model)
    write_model_json(char_dir / "story.json", story_model)

    return char_dir


# -----------------------------
# CLI
# -----------------------------
def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="init_character", add_help=True)
    parser.add_argument("name", help="Nombre del personaje (1..16, letras/números/_/-)")

    parser.add_argument("--level", type=int, default=1)
    parser.add_argument("--fuerza", type=int, default=1)
    parser.add_argument("--destreza", type=int, default=1)
    parser.add_argument("--inteligencia", type=int, default=1)
    parser.add_argument("--puntos-vida", dest="puntos_vida", type=int, default=1)
    parser.add_argument("--estres", type=int, default=0)

    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)

    try:
        name = validate_character_name(args.name)
    except ValueError as e:
        print(f"[error] {e}", file=sys.stderr)
        return 2

    # Validaciones básicas rápidas
    if args.level < 1:
        print("[error] level debe ser >= 1", file=sys.stderr)
        return 2
    for field_name in ("fuerza", "destreza", "inteligencia", "puntos_vida"):
        if getattr(args, field_name) < 0:
            print(f"[error] {field_name} no puede ser negativo", file=sys.stderr)
            return 2
    if args.estres < 0:
        print("[error] estres no puede ser negativo", file=sys.stderr)
        return 2

    project_root = Path.cwd()

    try:
        char_dir = init_character(
            project_root,
            name=name,
            level=args.level,
            fuerza=args.fuerza,
            destreza=args.destreza,
            inteligencia=args.inteligencia,
            puntos_vida=args.puntos_vida,
            estres=args.estres,
        )
    except FileExistsError as e:
        print(f"[error] {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"[error] Falló la inicialización: {e}", file=sys.stderr)
        return 3

    print(f"[ok] Personaje creado: {name}")
    print(f"     Path: {char_dir}")
    print("     Files: stats.json, inventory.json, state.json, story.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
