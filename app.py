import streamlit as st
from datetime import date, time

# Bring in the core PawPal+ classes. CareTask is imported as Task so the
# UI code can refer to it by the shorter name.
from pawpal_system import Owner, Pet, CareTask as Task, Schedule, Frequency

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

# --- Build today's schedule ---
st.subheader("Build Schedule")
st.caption("Gathers every task across your pets that occurs today, ordered by time.")

if st.button("Generate schedule"):
    schedule = Schedule.for_owner(owner, date.today())
    todays_tasks = schedule.getTodayTasks()

    st.markdown(f"**Today's plan for {owner.name} — {date.today():%A, %B %d, %Y}**")
    if not todays_tasks:
        st.info("Nothing scheduled today. 🎉")
    else:
        st.table(
            [
                {
                    "Time": t.time.strftime("%H:%M"),
                    "Task": t.taskName,
                    "Pet": t.pet.name if t.pet else "—",
                    "Frequency": t.frequency.value,
                    "Status": t.status.value,
                }
                for t in todays_tasks
            ]
        )
