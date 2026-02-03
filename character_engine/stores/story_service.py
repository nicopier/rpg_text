from __future__ import annotations

from typing import Any, Dict, Optional

from character_engine.models.story import StoryModel, EncounterModel, EncounterType, Activity


class StoryService:
    """
    Helpers para:
    - setear contexto actual (reanudar)
    - upsert de encounter
    - actualizar summary/facts/state
    - mantener tail corto
    - aplicar patch devuelto por LLM (merge seguro)
    """

    def __init__(self, *, tail_cap: int = 4, facts_cap: int = 12) -> None:
        self.tail_cap = tail_cap
        self.facts_cap = facts_cap

    # ---------- contexto actual ----------
    def set_context(
        self,
        story: StoryModel,
        *,
        l: Optional[str] = None,
        a: Optional[Activity] = None,
        s: Optional[str] = None,
        x: Optional[str] = None,
        p: Optional[str] = None,
    ) -> None:
        if l is not None:
            story.c.l = l
        if a is not None:
            story.c.a = a
        if s is not None:
            story.c.s = s
        if x is not None:
            story.c.x = x
        if p is not None:
            story.c.p = p

    # ---------- global memory ----------
    def set_global_summary(self, story: StoryModel, summary: str) -> None:
        story.g.s = (summary or "").strip()

    def add_global_fact(self, story: StoryModel, fact: str) -> None:
        f = (fact or "").strip()
        if not f:
            return
        if f not in story.g.f:
            story.g.f.append(f)
        if len(story.g.f) > self.facts_cap:
            story.g.f = story.g.f[-self.facts_cap :]

    # ---------- encounter ----------
    def upsert_encounter(self, story: StoryModel, *, encounter_id: str, t: EncounterType, n: str) -> EncounterModel:
        if encounter_id not in story.e:
            story.e[encounter_id] = EncounterModel(t=t, n=n)
        else:
            # si cambia el nombre, actualizamos
            story.e[encounter_id].n = n
        return story.e[encounter_id]

    def add_tail(self, story: StoryModel, *, encounter_id: str, text: str) -> None:
        txt = (text or "").strip()
        if not txt:
            return
        enc = story.e.get(encounter_id)
        if enc is None:
            # si no existe encounter, lo creamos genérico como evento
            enc = self.upsert_encounter(story, encounter_id=encounter_id, t="v", n=encounter_id)

        enc.tl.append(txt)
        if len(enc.tl) > self.tail_cap:
            enc.tl = enc.tl[-self.tail_cap :]

    def set_encounter_summary(self, story: StoryModel, *, encounter_id: str, summary: str) -> None:
        enc = story.e.get(encounter_id)
        if enc is None:
            enc = self.upsert_encounter(story, encounter_id=encounter_id, t="v", n=encounter_id)
        enc.s = (summary or "").strip()

    def add_encounter_fact(self, story: StoryModel, *, encounter_id: str, fact: str) -> None:
        enc = story.e.get(encounter_id)
        if enc is None:
            enc = self.upsert_encounter(story, encounter_id=encounter_id, t="v", n=encounter_id)

        f = (fact or "").strip()
        if not f:
            return
        if f not in enc.f:
            enc.f.append(f)
        if len(enc.f) > self.facts_cap:
            enc.f = enc.f[-self.facts_cap :]

    def patch_encounter_state(self, story: StoryModel, *, encounter_id: str, patch: Dict[str, Any]) -> None:
        enc = story.e.get(encounter_id)
        if enc is None:
            enc = self.upsert_encounter(story, encounter_id=encounter_id, t="v", n=encounter_id)

        # merge superficial (dict)
        for k, v in (patch or {}).items():
            enc.st[k] = v

    # ---------- patch LLM (merge seguro) ----------
    def apply_llm_patch(self, story: StoryModel, patch: Dict[str, Any]) -> None:
        """
        Espera un patch con la MISMA estructura compacta:
          { "c": {...}, "g": {...}, "e": { "enc_id": {...} } }
        y mergea solo keys conocidas, sin borrar lo existente.
        """
        if not patch:
            return

        # context
        c = patch.get("c")
        if isinstance(c, dict):
            self.set_context(
                story,
                l=c.get("l"),
                a=c.get("a"),
                s=c.get("s"),
                x=c.get("x"),
                p=c.get("p"),
            )

        # global
        g = patch.get("g")
        if isinstance(g, dict):
            if "s" in g:
                self.set_global_summary(story, g.get("s") or "")
            if "f" in g and isinstance(g.get("f"), list):
                for fact in g["f"]:
                    self.add_global_fact(story, str(fact))

        # encounters
        e = patch.get("e")
        if isinstance(e, dict):
            for enc_id, enc_patch in e.items():
                if not isinstance(enc_patch, dict):
                    continue
                # ensure encounter exists if type+name provided
                t = enc_patch.get("t")
                n = enc_patch.get("n")
                if t and n:
                    self.upsert_encounter(story, encounter_id=str(enc_id), t=str(t), n=str(n))
                enc = story.e.get(str(enc_id))
                if enc is None:
                    # si no hay t/n, lo creamos genérico
                    enc = self.upsert_encounter(story, encounter_id=str(enc_id), t="v", n=str(enc_id))

                if "s" in enc_patch:
                    enc.s = str(enc_patch.get("s") or "").strip()

                if "f" in enc_patch and isinstance(enc_patch.get("f"), list):
                    for fact in enc_patch["f"]:
                        self.add_encounter_fact(story, encounter_id=str(enc_id), fact=str(fact))

                if "st" in enc_patch and isinstance(enc_patch.get("st"), dict):
                    self.patch_encounter_state(story, encounter_id=str(enc_id), patch=enc_patch["st"])

                if "tl" in enc_patch and isinstance(enc_patch.get("tl"), list):
                    # tail: merge y cap
                    for line in enc_patch["tl"]:
                        enc.tl.append(str(line))
                    if len(enc.tl) > self.tail_cap:
                        enc.tl = enc.tl[-self.tail_cap:]
