from dataclasses import dataclass
from functools import total_ordering
from quantities import UnitQuantity, Quantity

criteria = UnitQuantity("criteria")


@dataclass
@total_ordering
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
        ratio = self.allowable_value / self.calculated_value
        # Since ths is allowable/calculated value for desing purposes, the real concern is for ratios<1
        # The cutoff is there so big numbers don't clutter the report
        # if ratio > 10:
        #     ratio = ">10"
        return Quantity(ratio, criteria)

    def __eq__(self, other: "Criteria"):
        if self.ratio == other.ratio:
            return True
        return False

    def __lt__(self, other: "Criteria"):
        if self.ratio < other.ratio:
            return True
        return False
