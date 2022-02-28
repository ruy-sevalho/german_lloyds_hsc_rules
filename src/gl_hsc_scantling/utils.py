from dataclasses import dataclass
from functools import total_ordering
from functools import cached_property as proprety
from quantities import UnitQuantity
from quantities import Quantity as Quant
from pylatex import Quantity, Command
import numpy as np

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
        return ratio

    def __eq__(self, other: "Criteria"):
        if self.ratio == other.ratio:
            return True
        return False

    def __lt__(self, other: "Criteria"):
        if self.ratio < other.ratio:
            return True
        return False

    def to_latex(self, round_precision: int = 2):
        ratio = self.ratio
        if ratio > 10:
            return ">10"
        print_ratio = Quantity(
            Quant(ratio), options={"round-precision": round_precision}
        )
        if ratio < 1:
            print_ratio = Command(
                "textcolor", arguments="red", extra_arguments=print_ratio
            )
        return print_ratio
