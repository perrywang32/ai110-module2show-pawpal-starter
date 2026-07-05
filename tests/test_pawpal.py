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
