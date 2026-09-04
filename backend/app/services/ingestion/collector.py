from abc import ABC, abstractmethod


class Collector(ABC):
    @abstractmethod
    async def collect(self) -> list[dict]:
        ...


class SeedDataCollector(Collector):
    def __init__(self, skills_data: list[dict]):
        self._skills_data = skills_data

    async def collect(self) -> list[dict]:
        return [dict(skill) for skill in self._skills_data]
