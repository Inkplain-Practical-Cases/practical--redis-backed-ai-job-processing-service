"""Offline deterministic AI adapter: never sends data to a third party."""
class FakeAI:
    def infer(self, prompt: str) -> str:
        return f"Processed: {prompt.strip()[:500]}"
