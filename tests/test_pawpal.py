"""Tests for the PawPal+ core classes.

Run from the project root with:  python -m pytest
"""

from datetime import date, time

from pawpal_system import Pet, CareTask, TaskStatus


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
