
class MultiCriterionPolicy:
    def __init__(self, criteria, hard_cap):
        self.criteria = criteria
        self.hard_cap = hard_cap

    def target_workers(self):
        limits = [c.max_workers() for c in self.criteria]
        return max(1, min(min(limits), self.hard_cap))
