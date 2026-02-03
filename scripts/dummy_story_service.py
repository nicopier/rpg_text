class DummyStoryService:
    def apply_llm_patch(self, story: dict, patch: dict) -> dict:
        new_story = dict(story)
        for k in ("c", "g", "e"):
            if k in patch and isinstance(patch[k], dict):
                base = dict(new_story.get(k, {}))
                base.update(patch[k])
                new_story[k] = base
        return new_story
