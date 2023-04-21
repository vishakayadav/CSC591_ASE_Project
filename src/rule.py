class RULE:
    def __init__(self):
        self.rule = {}

    def create(self, ranges: list, max_size: dict) -> dict:
        """Create a  RULE that groups `ranges` by their column id."""
        for range in ranges:
            if range["txt"] not in self.rule:
                self.rule[range["txt"]] = []
            self.rule[range["txt"]].append(
                {"lo": range["lo"], "hi": range["hi"], "at": range["at"]}
            )
        return self.prune(max_size)

    def prune(self, max_size: dict) -> dict:
        n = 0
        for txt, ranges in self.rule.items():
            n += 1
            if len(ranges) == max_size[txt]:
                n -= 1
                self.rule[txt] = []
        if n > 0:
            return self.rule
