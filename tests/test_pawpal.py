"""Tests for the PawPal+ core classes.

Run from the project root with:  python -m pytest
"""

from datetime import date, time, timedelta

from pawpal_system import Owner, Pet, CareTask, Schedule, TaskStatus, Frequency


def test_mark_complete_changes_status():
    """Task Completion: markComplete() flips status to COMPLETE."""
    task = CareTask("Morning walk", date.today(), time(7, 30))

    assert task.status == TaskStatus.PENDING  # starts pending
    task.markComplete()
    assert task.status == TaskStatus.COMPLETE


def test_adding_task_increases_pet_task_count():
    """Task Addition: addTask() grows the pet's task list by one."""
    pet = Pet("Biscuit", "dog", 5)
    assert len(pet.getCareNeeds()) == 0  # no tasks yet

    pet.addTask(CareTask("Feed dog", date.today(), time(12, 30)))

    assert len(pet.getCareNeeds()) == 1
    # the back-reference should point back to the pet
    assert pet.getCareNeeds()[0].pet is pet


def test_completing_daily_task_spawns_next_day():
    """Completing a daily task adds a new pending task one day later."""
    pet = Pet("Biscuit", "dog", 5)
    task = CareTask("Morning walk", date(2026, 7, 4), time(7, 30), Frequency.DAILY)
    pet.addTask(task)

    task.markComplete()

    assert len(pet.getCareNeeds()) == 2  # original + next occurrence
    upcoming = pet.getCareNeeds()[1]
    assert upcoming.date == date(2026, 7, 4) + timedelta(days=1)  # 2026-07-05
    assert upcoming.status == TaskStatus.PENDING
    assert upcoming.pet is pet


def test_completing_weekly_task_spawns_next_week():
    """Completing a weekly task adds a new task seven days later."""
    pet = Pet("Biscuit", "dog", 5)
    task = CareTask("Weekly bath", date(2026, 7, 4), time(18, 0), Frequency.WEEKLY)
    pet.addTask(task)

    task.markComplete()

    assert pet.getCareNeeds()[1].date == date(2026, 7, 4) + timedelta(weeks=1)


def test_completing_one_off_task_spawns_nothing():
    """A one-off (ONCE) task does not create a follow-up when completed."""
    pet = Pet("Biscuit", "dog", 5)
    task = CareTask("Vet visit", date(2026, 7, 4), time(15, 0))  # default ONCE
    pet.addTask(task)

    assert task.markComplete() is None
    assert len(pet.getCareNeeds()) == 1


def test_find_conflicts_flags_same_time_tasks():
    """Two tasks at the same time produce one warning; distinct times produce none."""
    owner = Owner("Jordan", "jordan@example.com")
    mochi = Pet("Mochi", "cat", 3)
    biscuit = Pet("Biscuit", "dog", 5)
    owner.addPet(mochi)
    owner.addPet(biscuit)

    day = date(2026, 7, 4)
    mochi.addTask(CareTask("Feed cat", day, time(9, 0)))
    biscuit.addTask(CareTask("Breakfast", day, time(9, 0)))  # same time -> conflict
    biscuit.addTask(CareTask("Walk", day, time(7, 30)))      # unique time -> fine

    schedule = Schedule.for_owner(owner, day)
    conflicts = schedule.find_conflicts()

    assert len(conflicts) == 1
    assert "09:00" in conflicts[0]

    # No conflicts when every task is at a distinct time.
    biscuit.getCareNeeds()[0].reschedule(day, time(10, 0))  # move Breakfast off 09:00
    assert Schedule.for_owner(owner, day).find_conflicts() == []


def _owner_with_scrambled_tasks(day):
    """Helper: build an owner whose tasks are added deliberately out of order."""
    owner = Owner("Jordan", "jordan@example.com")
    mochi = Pet("Mochi", "cat", 3)
    biscuit = Pet("Biscuit", "dog", 5)
    owner.addPet(mochi)
    owner.addPet(biscuit)

    # Added out of chronological order on purpose.
    mochi.addTask(CareTask("Evening play", day, time(19, 0)))
    biscuit.addTask(CareTask("Feed dog", day, time(12, 30)))
    biscuit.addTask(CareTask("Morning walk", day, time(7, 30)))
    return owner, mochi, biscuit


def test_sort_by_time_returns_chronological_order():
    """Sorting: tasks added out of order come back ordered by time of day."""
    day = date(2026, 7, 4)
    owner, _, _ = _owner_with_scrambled_tasks(day)

    schedule = Schedule.for_owner(owner, day)
    times = [t.time for t in schedule.sort_by_time()]

    assert times == [time(7, 30), time(12, 30), time(19, 0)]


def test_get_today_tasks_matches_sort_by_time():
    """getTodayTasks() is just the time-sorted view of the day's tasks."""
    day = date(2026, 7, 4)
    owner, _, _ = _owner_with_scrambled_tasks(day)

    schedule = Schedule.for_owner(owner, day)

    assert schedule.getTodayTasks() == schedule.sort_by_time()


def test_sort_by_time_breaks_ties_by_pet_then_name():
    """Two tasks at the same time break ties by pet name, then task name."""
    day = date(2026, 7, 4)
    owner = Owner("Jordan", "jordan@example.com")
    mochi = Pet("Mochi", "cat", 3)
    biscuit = Pet("Biscuit", "dog", 5)
    owner.addPet(mochi)
    owner.addPet(biscuit)

    # Same 09:00 time; added Mochi-first, but "Biscuit" should sort ahead.
    mochi.addTask(CareTask("Feed cat", day, time(9, 0)))
    biscuit.addTask(CareTask("Breakfast", day, time(9, 0)))

    ordered = Schedule.for_owner(owner, day).sort_by_time()

    assert [t.pet.name for t in ordered] == ["Biscuit", "Mochi"]


def test_sort_by_time_does_not_mutate_stored_order():
    """sort_by_time() returns a new list and leaves schedule.tasks untouched."""
    day = date(2026, 7, 4)
    owner, _, _ = _owner_with_scrambled_tasks(day)
    schedule = Schedule.for_owner(owner, day)

    before = list(schedule.tasks)
    schedule.sort_by_time()

    assert schedule.tasks == before  # original ordering preserved


def test_filter_by_pet_returns_only_that_pets_tasks():
    """filter_by_pet() keeps one pet's tasks, still ordered by time."""
    day = date(2026, 7, 4)
    owner, _, biscuit = _owner_with_scrambled_tasks(day)
    schedule = Schedule.for_owner(owner, day)

    biscuit_tasks = schedule.filter_by_pet("Biscuit")

    assert [t.taskName for t in biscuit_tasks] == ["Morning walk", "Feed dog"]
    assert all(t.pet.name == "Biscuit" for t in biscuit_tasks)
    # An unknown pet name yields an empty list, not an error.
    assert schedule.filter_by_pet("Nobody") == []


def test_filter_by_status_hides_completed_tasks():
    """filter_by_status() keeps only tasks with the requested status."""
    day = date(2026, 7, 4)
    owner, mochi, _ = _owner_with_scrambled_tasks(day)
    schedule = Schedule.for_owner(owner, day)

    # Complete one task; it should drop out of the PENDING view.
    mochi.getCareNeeds()[0].markComplete()

    pending = schedule.filter_by_status(TaskStatus.PENDING)
    assert all(t.status == TaskStatus.PENDING for t in pending)
    assert "Evening play" not in [t.taskName for t in pending]

    complete = schedule.filter_by_status(TaskStatus.COMPLETE)
    assert [t.taskName for t in complete] == ["Evening play"]
