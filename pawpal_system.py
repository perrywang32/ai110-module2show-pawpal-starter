"""PawPal+ system classes.

Skeleton generated from diagrams/uml.mmd. Attributes and method
signatures are in place; method bodies are left as stubs to implement
(except where a design fix required real logic, e.g. Schedule.addTask).

Design decisions after review:
- Single source of truth: a Pet owns its CareTasks. A Schedule holds
  references to the tasks that fall on one day.
- Every CareTask links back to its Pet (so a task can be labeled/explained).
- An Owner has many Schedules (one per day), not just one.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from datetime import date, time


class TaskStatus(str, Enum):
    """Allowed values for a CareTask's status (avoids magic strings)."""

    PENDING = "pending"
    COMPLETE = "complete"
    SKIPPED = "skipped"


@dataclass
class CareTask:
    """A single pet care task (walk, feeding, meds, etc.)."""

    taskName: str
    date: date
    time: time
    status: TaskStatus = TaskStatus.PENDING
    # Back-reference to the owning Pet. repr/compare disabled so the
    # Pet <-> CareTask cycle does not cause infinite __repr__ recursion
    # or make two tasks "unequal" just because their pets differ.
    pet: Pet | None = field(default=None, repr=False, compare=False)

    def markComplete(self) -> None:
        """Mark this task as complete."""
        ...

    def reschedule(self, newDate: date, newTime: time) -> None:
        """Move this task to a new date and time."""
        ...


@dataclass
class Pet:
    """An animal being cared for. Owns the tasks it needs."""

    name: str
    species: str
    age: int
    careNotes: str = ""
    careTasks: list[CareTask] = field(default_factory=list)

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
    """The care tasks that fall on a single day (a filtered view)."""

    date: date
    tasks: list[CareTask] = field(default_factory=list)

    def addTask(self, task: CareTask) -> None:
        """Add a task to the schedule.

        Guards against the duplicate-date bottleneck: a task can only be
        added to the schedule for its own day.
        """
        if task.date != self.date:
            raise ValueError(
                f"Task '{task.taskName}' is dated {task.date}, "
                f"but this schedule is for {self.date}."
            )
        self.tasks.append(task)

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
    schedules: list[Schedule] = field(default_factory=list)

    def addPet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        ...

    def removePet(self, pet: Pet) -> None:
        """Remove a pet from this owner."""
        ...

    def viewTodayTasks(self) -> list[CareTask]:
        """Return all care tasks due today across this owner's pets."""
        ...
