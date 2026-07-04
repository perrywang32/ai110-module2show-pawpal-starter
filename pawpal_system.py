"""PawPal+ system classes.

Implements the four core classes from diagrams/uml.mmd:

- CareTask : a single care activity (name, date/time, frequency, status).
- Pet      : pet details plus the list of tasks it needs.
- Owner    : manages many pets and exposes all of their tasks.
- Schedule : the "brain" that gathers, organizes, and manages tasks
             across an owner's pets for a given day.

Design decisions after review:
- A Pet owns its CareTasks (single source of truth).
- Each CareTask links back to its Pet so a task can be labeled/explained.
- An Owner has many Schedules (one per day), not just one.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, time
from enum import Enum


class TaskStatus(str, Enum):
    """Allowed values for a CareTask's status (avoids magic strings)."""

    PENDING = "pending"
    COMPLETE = "complete"
    SKIPPED = "skipped"


class Frequency(str, Enum):
    """How often a CareTask recurs."""

    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"


@dataclass
class CareTask:
    """A single pet care task (walk, feeding, meds, etc.)."""

    taskName: str
    date: date
    time: time
    frequency: Frequency = Frequency.ONCE
    status: TaskStatus = TaskStatus.PENDING
    # Back-reference to the owning Pet. repr/compare disabled so the
    # Pet <-> CareTask cycle does not cause infinite __repr__ recursion
    # or make two tasks "unequal" just because their pets differ.
    pet: Pet | None = field(default=None, repr=False, compare=False)

    def markComplete(self) -> None:
        """Mark this task as complete."""
        self.status = TaskStatus.COMPLETE

    def reschedule(self, newDate: date, newTime: time) -> None:
        """Move this task to a new date and time (and reopen it)."""
        self.date = newDate
        self.time = newTime
        self.status = TaskStatus.PENDING

    def occurs_on(self, day: date) -> bool:
        """Whether this task happens on ``day``, honoring its frequency."""
        if day < self.date:
            return False
        if self.frequency == Frequency.ONCE:
            return day == self.date
        if self.frequency == Frequency.DAILY:
            return True
        if self.frequency == Frequency.WEEKLY:
            return (day - self.date).days % 7 == 0
        return False


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
        """Update one or more of this pet's fields (leaves others as-is)."""
        if name is not None:
            self.name = name
        if species is not None:
            self.species = species
        if age is not None:
            self.age = age
        if careNotes is not None:
            self.careNotes = careNotes

    def addTask(self, task: CareTask) -> None:
        """Attach a task to this pet, maintaining the back-reference."""
        task.pet = self
        self.careTasks.append(task)

    def getCareNeeds(self) -> list[CareTask]:
        """Return the care tasks this pet needs."""
        return self.careTasks


@dataclass
class Owner:
    """The pet owner using PawPal+."""

    name: str
    email: str
    pets: list[Pet] = field(default_factory=list)
    schedules: list[Schedule] = field(default_factory=list)

    def addPet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        if pet not in self.pets:
            self.pets.append(pet)

    def removePet(self, pet: Pet) -> None:
        """Remove a pet from this owner."""
        if pet in self.pets:
            self.pets.remove(pet)

    def getAllTasks(self) -> list[CareTask]:
        """Flatten every care task across all of this owner's pets."""
        return [task for pet in self.pets for task in pet.getCareNeeds()]

    def viewTodayTasks(self) -> list[CareTask]:
        """Return all care tasks due today across this owner's pets."""
        return Schedule.for_owner(self, date.today()).getTodayTasks()


@dataclass
class Schedule:
    """The "brain": gathers and organizes an owner's tasks for one day."""

    date: date
    tasks: list[CareTask] = field(default_factory=list)

    @classmethod
    def for_owner(cls, owner: Owner, day: date) -> Schedule:
        """Build a schedule of every task across ``owner``'s pets on ``day``."""
        schedule = cls(date=day)
        for task in owner.getAllTasks():
            if task.occurs_on(day):
                schedule.addTask(task)
        return schedule

    def addTask(self, task: CareTask) -> None:
        """Add a task, but only to a schedule for a day on which it occurs."""
        if not task.occurs_on(self.date):
            raise ValueError(
                f"Task '{task.taskName}' does not occur on {self.date}."
            )
        self.tasks.append(task)

    def removeTask(self, task: CareTask) -> None:
        """Remove a task from the schedule (no error if absent)."""
        if task in self.tasks:
            self.tasks.remove(task)

    def getTodayTasks(self) -> list[CareTask]:
        """Return this day's tasks, ordered by time of day."""
        return sorted(self.tasks, key=lambda t: t.time)
