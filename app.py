import streamlit as st
from datetime import date, time

# Bring in the core PawPal+ classes. CareTask is imported as Task so the
# UI code can refer to it by the shorter name.
from pawpal_system import Owner, Pet, CareTask as Task, Schedule, Frequency, TaskStatus

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ app. Add your pets, give each one some care tasks,
then generate today's schedule.
"""
)

with st.expander("Scenario", expanded=False):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.
"""
    )

# --- Session "vault": create the Owner once and reuse it across reruns. ---
# Streamlit re-runs this whole script on every interaction, so guard the
# creation with `not in` — otherwise we'd wipe out pets/tasks each rerun.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", email="jordan@example.com")

owner = st.session_state.owner

st.divider()

# --- Owner ---
st.subheader("Owner")
owner.name = st.text_input("Owner name", value=owner.name)
owner.email = st.text_input("Owner email", value=owner.email)

st.divider()

# --- Add a pet ---
st.subheader("Add a Pet")
col1, col2, col3 = st.columns(3)
with col1:
    pet_name = st.text_input("Pet name", value="Mochi")
with col2:
    species = st.selectbox("Species", ["dog", "cat", "other"])
with col3:
    age = st.number_input("Age", min_value=0, max_value=50, value=3)

if st.button("Add pet"):
    if pet_name.strip():
        pet = Pet(name=pet_name.strip(), species=species, age=int(age))
        owner.addPet(pet)
        st.success(f"Added {pet.name} ({pet.species}).")
    else:
        st.warning("Please enter a pet name.")

if owner.pets:
    st.caption("Current pets:")
    st.table(
        [
            {"Name": p.name, "Species": p.species, "Age": p.age, "Tasks": len(p.getCareNeeds())}
            for p in owner.pets
        ]
    )
else:
    st.info("No pets yet. Add one above.")

st.divider()

# --- Add a task to a pet ---
st.subheader("Add a Task")
if not owner.pets:
    st.info("Add a pet first, then you can give it tasks.")
else:
    col1, col2 = st.columns(2)
    with col1:
        # Select by index, then look the pet up in the vault. Passing the Pet
        # objects directly returns a *copy* through session_state, so mutating
        # it would not touch the stored pet.
        pet_index = st.selectbox(
            "Pet",
            options=range(len(owner.pets)),
            format_func=lambda i: owner.pets[i].name,
        )
        selected_pet = owner.pets[pet_index]
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        task_date = st.date_input("Date", value=date.today())
        task_time = st.time_input("Time", value=time(8, 0))
    frequency = st.selectbox(
        "Frequency", options=list(Frequency), format_func=lambda f: f.value
    )

    if st.button("Add task"):
        if task_title.strip():
            task = Task(
                taskName=task_title.strip(),
                date=task_date,
                time=task_time,
                frequency=frequency,
            )
            selected_pet.addTask(task)  # wires task.pet back-reference
            st.success(f"Added '{task.taskName}' to {selected_pet.name}.")
        else:
            st.warning("Please enter a task title.")

st.divider()

# --- Build a schedule for a chosen day ---
st.subheader("Build Schedule")
st.caption(
    "Pick a day and generate the plan. Tasks are gathered across all your pets, "
    "sorted by time, and checked for time conflicts."
)

# Let the user choose ANY date, not just today. The `key` makes Streamlit
# remember the chosen date across reruns (clicks/filter changes).
schedule_day = st.date_input("Schedule date", value=date.today(), key="schedule_day")

# Pressing the button flips a flag we keep in session_state, so the schedule
# stays on screen through later reruns (e.g. when filtering or marking done).
if st.button("Generate schedule"):
    st.session_state.show_schedule = True

if st.session_state.get("show_schedule"):
    # Rebuild the schedule fresh each rerun from the chosen day. Because
    # Schedule.for_owner reuses the pets' real CareTask objects, marking one
    # complete below actually updates the stored task (and spawns recurrences).
    schedule = Schedule.for_owner(owner, schedule_day)

    st.markdown(f"**Plan for {owner.name} — {schedule_day:%A, %B %d, %Y}**")

    # Conflict warnings are computed on the FULL day (not the filtered view),
    # so a clash is never hidden just because a filter is active.
    for message in schedule.find_conflicts():
        st.warning(f"⚠️ {message}")

    # --- Filtering controls ---
    fcol1, fcol2 = st.columns(2)
    with fcol1:
        pet_filter = st.selectbox(
            "Filter by pet", ["All pets"] + [p.name for p in owner.pets]
        )
    with fcol2:
        status_filter = st.selectbox(
            "Filter by status", ["All"] + [s.value for s in TaskStatus]
        )

    # Start from the time-sorted list, then narrow with the Schedule methods.
    tasks = schedule.getTodayTasks()
    if pet_filter != "All pets":
        tasks = schedule.filter_by_pet(pet_filter)
    if status_filter != "All":
        wanted = schedule.filter_by_status(TaskStatus(status_filter))
        tasks = [t for t in tasks if t in wanted]

    if not tasks:
        st.info("Nothing to show for this day and filter. 🎉")
    else:
        # A header row, then one row per task with a "Mark done" button.
        head = st.columns([1, 3, 2, 2, 2, 2])
        for col, label in zip(head, ["Time", "Task", "Pet", "Frequency", "Status", ""]):
            col.markdown(f"**{label}**")

        for i, t in enumerate(tasks):
            c1, c2, c3, c4, c5, c6 = st.columns([1, 3, 2, 2, 2, 2])
            c1.write(t.time.strftime("%H:%M"))
            c2.write(t.taskName)
            c3.write(t.pet.name if t.pet else "—")
            c4.write(t.frequency.value)
            c5.write(t.status.value)
            with c6:
                if t.status == TaskStatus.PENDING:
                    # Unique key per row so Streamlit tracks each button.
                    if st.button("✓ Done", key=f"done_{i}_{t.taskName}_{t.time}"):
                        t.markComplete()  # recurring tasks spawn their next date
                        st.rerun()
                else:
                    c6.write("—")
