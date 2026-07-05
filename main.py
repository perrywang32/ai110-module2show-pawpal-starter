"""PawPal+ demo script.

Builds a small owner/pet/task setup and prints today's schedule so you can
see the scheduling logic from pawpal_system.py working end-to-end.

Run with:  python main.py
"""

import sys
from datetime import date, time

from pawpal_system import Owner, Pet, CareTask, Schedule, Frequency, TaskStatus

# Print UTF-8 so emoji work even on Windows' default cp1252 console.
sys.stdout.reconfigure(encoding="utf-8")


def print_tasks(title: str, tasks: list[CareTask]) -> None:
    """Print a titled list of tasks, one per line."""
    print(f"\n{title}")
    print("-" * 48)
    if not tasks:
        print("  (none)")
        return
    for task in tasks:
        print(
            f"  {task.time:%H:%M}  {task.taskName:<15} "
            f"({task.pet.name})  [{task.status.value}]"
        )


def main() -> None:
    today = date.today()

    # 1. Create an owner.
    owner = Owner(name="Jordan", email="jordan@example.com")

    # 2. Create at least two pets and give them to the owner.
    mochi = Pet(name="Mochi", species="cat", age=3, careNotes="Shy; feed twice a day")
    biscuit = Pet(name="Biscuit", species="dog", age=5, careNotes="Needs lots of walks")
    owner.addPet(mochi)
    owner.addPet(biscuit)

    # 3. Add tasks OUT OF ORDER on purpose, so we can prove sort_by_time works.
    #    Two tasks share 09:00 (Feed cat / Breakfast) to trigger a conflict
    #    warning, and also to exercise the tie-break (pet, then name).
    mochi.addTask(CareTask("Evening play", today, time(19, 0), Frequency.DAILY))
    biscuit.addTask(CareTask("Feed dog", today, time(12, 30), Frequency.DAILY))
    mochi.addTask(CareTask("Feed cat", today, time(9, 0), Frequency.DAILY))
    biscuit.addTask(CareTask("Breakfast", today, time(9, 0), Frequency.DAILY))
    biscuit.addTask(CareTask("Morning walk", today, time(7, 30), Frequency.DAILY))

    # Mark one task complete so the status filter has something to hide.
    mochi.getCareNeeds()[0].markComplete()

    # 4. Build today's schedule (the "brain" gathers tasks across pets).
    schedule = Schedule.for_owner(owner, today)

    print(f"🐾 PawPal+ — {owner.name}'s day — {today:%A, %B %d, %Y}")

    # All tasks sorted by time.
    print_tasks("All tasks (sorted by time):", schedule.sort_by_time())

    # Tasks for one selected pet.
    print_tasks(f"Tasks for {biscuit.name}:", schedule.filter_by_pet(biscuit.name))

    # Only pending tasks.
    print_tasks("Pending tasks only:", schedule.filter_by_status(TaskStatus.PENDING))

    # Conflict check: warns about overlapping time slots without crashing.
    print("\nConflict check:")
    print("-" * 48)
    conflicts = schedule.find_conflicts()
    if conflicts:
        for message in conflicts:
            print(f"  ⚠️  {message}")
    else:
        print("  No conflicts. ✅")


if __name__ == "__main__":
    main()
