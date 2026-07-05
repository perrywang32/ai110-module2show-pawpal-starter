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
from datetime import date, time, timedelta
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

    def next_occurrence(self) -> CareTask | None:
        """Build the next occurrence of a recurring task.

        Uses ``timedelta`` to advance this task's date by its frequency
        (DAILY -> +1 day, WEEKLY -> +7 days) and returns a fresh, pending
        CareTask at the same time. A one-off (ONCE) task does not recur, so
        this returns ``None``.

        Returns:
            A new CareTask for the next date, or ``None`` if non-recurring.
        """
        if self.frequency == Frequency.DAILY:
            next_date = self.date + timedelta(days=1)
        elif self.frequency == Frequency.WEEKLY:
            next_date = self.date + timedelta(weeks=1)
        else:  # Frequency.ONCE
            return None
        return CareTask(self.taskName, next_date, self.time, self.frequency)

    def markComplete(self) -> CareTask | None:
        """Mark this task complete and, if recurring, schedule the next one.

        Sets the status to COMPLETE, then asks ``next_occurrence()`` for the
        follow-up task. If one exists and this task belongs to a pet, the
        new task is attached to that pet (which wires its back-reference),
        so tomorrow's/next week's occurrence appears automatically.

        Returns:
            The newly created follow-up CareTask, or ``None`` for a one-off.
        """
        self.status = TaskStatus.COMPLETE
        upcoming = self.next_occurrence()
        if upcoming is not None and self.pet is not None:
            self.pet.addTask(upcoming)  # wires the new task's pet back-reference
        return upcoming

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

    def sort_by_time(self) -> list[CareTask]:
        """Return the day's tasks ordered by time of day.

        Sorts on the tuple ``(time, pet name, task name)`` so ties at the
        same time break deterministically (by pet, then task name) rather
        than depending on insertion order. Returns a new list; the stored
        ``tasks`` order is left untouched.
        """
        return sorted(
            self.tasks,
            key=lambda t: (t.time, t.pet.name if t.pet else "", t.taskName),
        )

    def getTodayTasks(self) -> list[CareTask]:
        """Return this day's tasks, ordered by time (delegates to sort_by_time)."""
        return self.sort_by_time()

    def filter_by_pet(self, pet_name: str) -> list[CareTask]:
        """Return only the tasks belonging to one pet, ordered by time.

        Args:
            pet_name: Name of the pet to keep tasks for.

        Returns:
            The time-sorted subset of tasks whose pet has that name.
        """
        return [t for t in self.sort_by_time() if t.pet and t.pet.name == pet_name]

    def filter_by_status(self, status: TaskStatus) -> list[CareTask]:
        """Return only the tasks with a given status, ordered by time.

        Args:
            status: The TaskStatus to keep (also accepts its string value,
                e.g. "pending", since TaskStatus is a str-based enum).

        Returns:
            The time-sorted subset of tasks matching that status.
        """
        return [t for t in self.sort_by_time() if t.status == status]

    def find_conflicts(self) -> list[str]:
        """Detect tasks scheduled at the same time and return warning messages.

        Lightweight, single-pass strategy: bucket every task by its ``time``
        value, then flag any slot holding two or more tasks (covering both
        same-pet and cross-pet clashes). Returns human-readable warnings
        instead of raising, so a clash never crashes the program.

        Returns:
            One message per conflicting time slot naming the clashing tasks
            and their pets; an empty list when there are no conflicts.
        """
        by_time: dict[time, list[CareTask]] = {}
        for task in self.sort_by_time():
            by_time.setdefault(task.time, []).append(task)

        warnings: list[str] = []
        for slot, tasks in sorted(by_time.items()):
            if len(tasks) > 1:
                labels = ", ".join(
                    f"{t.taskName} ({t.pet.name if t.pet else '?'})" for t in tasks
                )
                warnings.append(f"Conflict at {slot:%H:%M}: {labels}")
        return warnings
