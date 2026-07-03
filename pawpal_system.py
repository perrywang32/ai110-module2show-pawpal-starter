"""PawPal+ system classes.

Skeleton generated from diagrams/uml.mmd. Attributes and method
signatures are in place; method bodies are left as stubs to implement.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, time


@dataclass
class CareTask:
    """A single pet care task (walk, feeding, meds, etc.)."""

    taskName: str
    date: date
    time: time
    status: str = "pending"

    def markComplete(self) -> None:
        """Mark this task as complete."""
        ...

    def reschedule(self, newDate: date, newTime: time) -> None:
        """Move this task to a new date and time."""
        ...


@dataclass
class Pet:
    """An animal being cared for."""

    name: str
    species: str
    age: int
    careNotes: str = ""

    def updateInfo(
        self,
        name: str | None = None,
        species: str | None = None,
        age: int | None = None,
        careNotes: str | None = None,
    ) -> None:
        """Update one or more of this pet's fields."""
        ...

    def getCareNeeds(self) -> list[CareTask]:
        """Return the care tasks this pet needs."""
        ...


@dataclass
class Schedule:
    """A collection of care tasks for a given day."""

    date: date
    tasks: list[CareTask] = field(default_factory=list)

    def addTask(self, task: CareTask) -> None:
        """Add a task to the schedule."""
        ...

    def removeTask(self, task: CareTask) -> None:
        """Remove a task from the schedule."""
        ...

    def getTodayTasks(self) -> list[CareTask]:
        """Return the tasks scheduled for today."""
        ...


@dataclass
class Owner:
    """The pet owner using PawPal+."""

    name: str
    email: str
    pets: list[Pet] = field(default_factory=list)

    def addPet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        ...

    def removePet(self, pet: Pet) -> None:
        """Remove a pet from this owner."""
        ...

    def viewTodayTasks(self) -> list[CareTask]:
        """Return all care tasks due today across this owner's pets."""
        ...
