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

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
# e.g.:
# Daily plan for Biscuit (Golden Retriever):
#   08:00 — Morning walk (30 min) [priority: high]
#   09:00 — Feeding (10 min) [priority: high]
#   ...
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

## 📐 Smarter Scheduling

The scheduling logic lives in `pawpal_system.py`. The `Schedule` class acts as
the "brain": `Schedule.for_owner(owner, day)` gathers every task across an
owner's pets that occurs on a given day, and the methods below organize,
filter, and validate that day's tasks.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Schedule.sort_by_time()` | Sorts by the tuple `(time, pet name, task name)` so same-time ties break deterministically. `Schedule.getTodayTasks()` delegates to it. |
| Filtering | `Schedule.filter_by_pet(pet_name)`, `Schedule.filter_by_status(status)` | Return the time-sorted subset for one pet, or for a status (e.g. only `pending`). |
| Conflict detection | `Schedule.find_conflicts()` | Buckets tasks by `time` and warns about any slot with 2+ tasks (same-pet or cross-pet). Returns warning strings instead of raising, so a clash never crashes the app. |
| Recurring tasks | `CareTask.markComplete()`, `CareTask.next_occurrence()` | Completing a `daily`/`weekly` task auto-creates the next occurrence using `timedelta` (+1 day / +7 days). A `once` task creates nothing. |

### Details

- **Sorting behavior — `Schedule.sort_by_time()`**
  Returns a new list of the day's tasks ordered by time of day. The sort key
  is `(time, pet name, task name)`, so if two tasks share a time they fall
  back to pet name then task name rather than depending on insertion order.
  `getTodayTasks()` is a thin wrapper around this method.

- **Filtering behavior — `Schedule.filter_by_pet()` / `Schedule.filter_by_status()`**
  `filter_by_pet(pet_name)` keeps only tasks belonging to the named pet.
  `filter_by_status(status)` keeps only tasks with the given `TaskStatus`
  (e.g. `TaskStatus.PENDING`); because `TaskStatus` is a string-based enum, the
  plain string `"pending"` works too. Both return results already sorted by time.

- **Conflict detection — `Schedule.find_conflicts()`**
  A lightweight, single-pass check: it buckets every task by its `time` value
  and flags any slot that holds two or more tasks. This catches both a single
  pet double-booked and two different pets needing attention at once. It
  returns a list of human-readable warnings (empty when there are none)
  instead of throwing, so the caller decides how to surface them.

- **Recurring task logic — `CareTask.markComplete()` / `CareTask.next_occurrence()`**
  When a `daily` or `weekly` task is marked complete, `markComplete()` sets its
  status to `complete` and then calls `next_occurrence()`, which uses
  `datetime.timedelta` to advance the date (`+1 day` for daily, `+7 days` for
  weekly) and build a fresh pending `CareTask`. The new task is attached to the
  same pet automatically, so the next occurrence shows up without manual entry.
  One-off (`once`) tasks return `None` and create no follow-up.

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
