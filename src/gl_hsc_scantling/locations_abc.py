from abc import ABC, abstractmethod


# Abstract classes
class Pressure(ABC):
    name: str

    @abstractmethod
    def calc(self, elmt) -> float:
        pass


class Location(ABC):
    _pressures: list[Pressure]

    def calc_pressures(self, elmt):
        return {pressure.name: pressure.calc(elmt=elmt) for pressure in self._pressures}
