# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Run the command-line demo to see the scheduling logic end-to-end:

```bash
python main.py
```

```
🐾 PawPal+ — Jordan's day — Sunday, July 05, 2026

All tasks (sorted by time):
------------------------------------------------
  07:30  Morning walk    (Biscuit)  [pending]
  09:00  Breakfast       (Biscuit)  [pending]
  09:00  Feed cat        (Mochi)  [pending]
  12:30  Feed dog        (Biscuit)  [pending]
  19:00  Evening play    (Mochi)  [complete]

Tasks for Biscuit:
------------------------------------------------
  07:30  Morning walk    (Biscuit)  [pending]
  09:00  Breakfast       (Biscuit)  [pending]
  12:30  Feed dog        (Biscuit)  [pending]

Pending tasks only:
------------------------------------------------
  07:30  Morning walk    (Biscuit)  [pending]
  09:00  Breakfast       (Biscuit)  [pending]
  09:00  Feed cat        (Mochi)  [pending]
  12:30  Feed dog        (Biscuit)  [pending]

Conflict check:
------------------------------------------------
  ⚠️  Conflict at 09:00: Breakfast (Biscuit), Feed cat (Mochi)
```

## 🧪 Testing PawPal+

Run the full automated test suite from the project root:

```bash
python -m pytest
```

The tests in `tests/test_pawpal.py` cover the scheduler's most important behaviors:

- **Sorting** — tasks added out of order come back in chronological order, ties break deterministically by pet then task name, and sorting never mutates the stored order.
- **Filtering** — `filter_by_pet()` and `filter_by_status()` return the correct time-sorted subset (and an empty list for no matches).
- **Recurring tasks** — completing a `daily`/`weekly` task auto-creates the next occurrence (+1 day / +7 days), while a `once` task creates nothing.
- **Conflict detection** — `find_conflicts()` flags two tasks scheduled at the same time with a warning message instead of crashing.

### Sample Test Output

```
............                                                             [100%]
12 passed in 0.05s
```

### Confidence Level

⭐⭐⭐⭐⭐ (5/5)

All 12 tests pass, covering every core scheduling behavior — sorting, filtering, recurrence, and conflict detection — including edge cases such as tie-breaking, non-mutation of stored order, one-off tasks, and unknown pet names. The green suite gives high confidence that the scheduling logic in `pawpal_system.py` behaves as designed.

## ✨ Features

The scheduling logic lives in `pawpal_system.py`, where the `Schedule` class
acts as the "brain": `Schedule.for_owner(owner, day)` gathers every task across
an owner's pets that occurs on a given day. Four core features organize and
validate that day's plan:

- **Sorting by time** — `sort_by_time()` returns the day's tasks ordered by time
  of day. Its sort key is `(time, pet name, task name)`, so tasks at the same
  time break ties deterministically by pet then task name rather than by
  insertion order. `getTodayTasks()` is a thin wrapper around it.
- **Filtering** — `filter_by_pet(pet_name)` keeps only one pet's tasks, and
  `filter_by_status(status)` keeps only tasks with a given `TaskStatus`
  (e.g. only `pending`). Both return results already sorted by time.
- **Recurring tasks** — completing a `daily` or `weekly` task via
  `markComplete()` calls `next_occurrence()`, which uses `timedelta` to advance
  the date (`+1 day` for daily, `+7 days` for weekly) and attaches a fresh
  pending task to the same pet automatically. A `once` task creates no follow-up.
- **Conflict detection** — `find_conflicts()` buckets tasks by `time` and flags
  any slot holding two or more tasks (same-pet or cross-pet). It returns
  human-readable warning strings instead of raising, so a clash never crashes
  the app.

## 📸 Demo Walkthrough

Launch the Streamlit app from the project root:

```bash
streamlit run app.py
```

The single-page UI walks top to bottom:

1. **Set the owner.** Enter the owner's name and email at the top. These persist
   across interactions for the whole session.
2. **Add a pet.** Under *Add a Pet*, enter a name, pick a species, set an age,
   and click **Add pet**. Each pet you add appears in the *Current pets* table
   with its task count. Repeat to add as many pets as you like.
3. **Schedule a task.** Under *Add a Task*, choose the pet, give the task a
   title, pick a date, a time, and a frequency (`once`, `daily`, or `weekly`),
   then click **Add task**. The task is attached to that pet.
4. **Generate the schedule.** Under *Build Schedule*, choose the date to view
   and click **Generate schedule**. PawPal+ gathers every task that occurs on
   that day across all pets and displays them **sorted by time**. Use the
   *Filter by pet* and *Filter by status* dropdowns to narrow the view.
5. **Watch sorting and conflict detection.** Tasks always render earliest-first,
   with same-time ties ordered by pet then task name. If two tasks fall on the
   same time slot, a **⚠️ conflict warning** appears above the table naming the
   clashing tasks — it warns without blocking the plan. Marking a `daily` or
   `weekly` task **✓ Done** completes it and automatically schedules its next
   occurrence.
