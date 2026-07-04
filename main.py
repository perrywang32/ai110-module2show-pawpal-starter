"""PawPal+ demo script.

Builds a small owner/pet/task setup and prints today's schedule so you can
see the scheduling logic from pawpal_system.py working end-to-end.

Run with:  python main.py
"""

import sys
from datetime import date, time

from pawpal_system import Owner, Pet, CareTask, Frequency

# Print UTF-8 so emoji work even on Windows' default cp1252 console.
sys.stdout.reconfigure(encoding="utf-8")


def main() -> None:
    today = date.today()

    # 1. Create an owner.
    owner = Owner(name="Jordan", email="jordan@example.com")

    # 2. Create at least two pets and give them to the owner.
    mochi = Pet(name="Mochi", species="cat", age=3, careNotes="Shy; feed twice a day")
    biscuit = Pet(name="Biscuit", species="dog", age=5, careNotes="Needs lots of walks")
    owner.addPet(mochi)
    owner.addPet(biscuit)

    # 3. Add at least three tasks with different times across the pets.
    biscuit.addTask(CareTask("Morning walk", today, time(7, 30), Frequency.DAILY))
    mochi.addTask(CareTask("Feed cat", today, time(9, 0), Frequency.DAILY))
    biscuit.addTask(CareTask("Feed dog", today, time(12, 30), Frequency.DAILY))
    mochi.addTask(CareTask("Evening play", today, time(19, 0), Frequency.DAILY))

    # 4. Print today's schedule (gathered + ordered by the Schedule "brain").
    print(f"🐾 Today's Schedule for {owner.name} — {today:%A, %B %d, %Y}")
    print("-" * 48)

    todays_tasks = owner.viewTodayTasks()
    if not todays_tasks:
        print("  Nothing scheduled today. 🎉")
    else:
        for task in todays_tasks:
            print(
                f"  {task.time:%H:%M}  {task.taskName:<15} "
                f"({task.pet.name})  [{task.status.value}]"
            )


if __name__ == "__main__":
    main()
