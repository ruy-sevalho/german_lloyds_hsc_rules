from dataclasses import dataclass


@dataclass
class Criteria:
    calculated_value: float
    theoretical_limit_value: float
    safety_factor: float

    @property
    def allowable_value(self):
        return self.theoretical_limit_value / self.safety_factor

    @property
    def passed(self):
        if self.calculated_value < self.allowable_value:
            return True
        return False

    @property
    def ratio(self):
        return self.allowable_value / self.calculated_value
