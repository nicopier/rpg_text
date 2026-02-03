from combat_engine.models import CombatState


def evaluate_end_conditions(state: CombatState, *, player_id: str) -> str:
    """
    Devuelve:
      - 'defeat'   si el player murió
      - 'victory'  si no quedan enemigos vivos
      - 'ongoing'  si el combate continúa
    """

    player = state.entities.get(player_id)
    if player and player.hp_current <= 0:
        return "defeat"

    enemies_alive = [
        e for e in state.entities.values()
        if e.team == "enemies" and e.hp_current > 0
    ]
    if not enemies_alive:
        return "victory"

    return "ongoing"
