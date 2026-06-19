class LLMBudget:
    def __init__(self, limit: int):
        self.remaining = limit

    def consume(self):
        if self.remaining <= 0:
            raise RuntimeError("LLM budget exhausted")
        self.remaining -= 1
