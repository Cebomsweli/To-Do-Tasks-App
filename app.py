import streamlit as st
import json
import os
import hashlib
import pandas as pd
from datetime import datetime

# Function to hash PIN securely
def hash_pin(pin):
    return hashlib.sha256(pin.encode()).hexdigest()

# Function to get the file paths based on the username
def get_user_file_paths(username):
    tasks_file = f'{username}_tasks.json'
    history_file = f'{username}_history.json'
    archive_file = f'{username}_archive.json'
    pin_file = f'{username}_pin.json'
    return tasks_file, history_file, archive_file, pin_file

# Function to load user data from file
def load_user_data(username):
    tasks_file, history_file, archive_file, pin_file = get_user_file_paths(username)
    
    tasks = json.load(open(tasks_file)) if os.path.exists(tasks_file) else []
    history = json.load(open(history_file)) if os.path.exists(history_file) else []
    archived = json.load(open(archive_file)) if os.path.exists(archive_file) else []

    return tasks, history, archived

# Function to save user data to file
def save_user_data(username, tasks, history, archived):
    tasks_file, history_file, archive_file, _ = get_user_file_paths(username)
    
    json.dump(tasks, open(tasks_file, 'w'))
    json.dump(history, open(history_file, 'w'))
    json.dump(archived, open(archive_file, 'w'))

# Function to save user PIN securely
def save_user_pin(username, pin):
    pin_file = f'{username}_pin.json'
    hashed_pin = hash_pin(pin)
    json.dump({'pin': hashed_pin}, open(pin_file, 'w'))

# Function to check if the entered PIN matches the stored PIN
def check_user_pin(username, pin):
    pin_file = f'{username}_pin.json'
    if os.path.exists(pin_file):
        stored_data = json.load(open(pin_file))
        return stored_data.get('pin') == hash_pin(pin)
    return False

# Purple Theme Styling
st.markdown(
    """
    <style>
        body { background-color: #f3e5f5; }
        .stButton>button {
            border-radius: 8px;
            color: white;
            background-color: #7b1fa2;
            border: none;
            padding: 8px 16px;
            margin: 4px;
            font-size: 14px;
        }
        .stButton>button:hover { background-color: #9c27b0; }
        .task-table { border-collapse: collapse; width: 100%; }
        .task-table th, .task-table td {
            border: 1px solid #9c27b0;
            padding: 8px;
            text-align: left;
        }
        .task-table th { background-color: #7b1fa2; color: white; }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("📌 Silver To-Do List App")

if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    username = st.text_input("Enter your username")
    pin = st.text_input("Enter your PIN", type="password")

    if username:
        pin_file = f'{username}_pin.json'
        if os.path.exists(pin_file):
            if pin and check_user_pin(username, pin):
                st.session_state['username'] = username
                st.session_state['logged_in'] = True
                st.success(f"Welcome back, {username}!")
                st.rerun()
            elif pin:
                st.error("Incorrect PIN. Please try again.")
        else:
            confirm_pin = st.text_input("Confirm your PIN", type="password")
            if st.button("Create Account"):
                if pin == confirm_pin:
                    save_user_pin(username, pin)
                    save_user_data(username, [], [], [])
                    st.session_state['username'] = username
                    st.session_state['logged_in'] = True
                    st.success("Account created successfully!")
                    st.rerun()
                else:
                    st.error("PINs do not match. Try again.")

if 'username' in st.session_state and st.session_state['logged_in']:
    tasks, history, archived = load_user_data(st.session_state['username'])

    st.sidebar.header(f"Welcome, {st.session_state['username']}")
    view_selection = st.sidebar.radio("📂 Select View", ["Add Task", "Pending Tasks", "Completed Tasks", "Archived Tasks"])

    if st.sidebar.button("🚪 Logout"):
        del st.session_state['username']
        del st.session_state['logged_in']
        st.rerun()

    # Function to add a task
    def add_task(task_name, task_date, start_time, end_time):
        task = {
            'Task': task_name,
            'Due Date': task_date.strftime('%Y-%m-%d'),
            'Start Time': start_time.strftime('%H:%M'),
            'End Time': end_time.strftime('%H:%M'),
            'Status': 'Pending'
        }
        tasks.append(task)
        save_user_data(st.session_state['username'], tasks, history, archived)
        st.success("✅ Task added successfully!")
        st.rerun()

    # Function to mark task as done
    def mark_task_done(task_index):
        task = tasks.pop(task_index)
        task['Status'] = 'Done'
        history.append(task)
        save_user_data(st.session_state['username'], tasks, history, archived)
        st.rerun()

    # Function to archive task
    def archive_task(task_index):
        task = history.pop(task_index)
        archived.append(task)
        save_user_data(st.session_state['username'], tasks, history, archived)
        st.rerun()

    # Handling different views
    if view_selection == "Add Task":
        st.markdown("<h3 style='color:#6a1b9a;'>📝 Add a New Task</h3>", unsafe_allow_html=True)
        with st.form(key="add_task_form"):
            task_name = st.text_input("Task Name")
            task_date = st.date_input("Due Date", min_value=datetime.today())
            start_time = st.time_input("Start Time", value=datetime.now().time())
            end_time = st.time_input("End Time", value=datetime.now().time())
            if st.form_submit_button("➕ Add Task"):
                add_task(task_name, task_date, start_time, end_time)

    elif view_selection == "Pending Tasks":
        st.markdown("<h3 style='color:#6a1b9a;'>📌 Pending Tasks</h3>", unsafe_allow_html=True)
        if tasks:
            for i, task in enumerate(tasks):
                st.write(f"📍 **{task['Task']}** (Due: {task['Due Date']}, {task['Start Time']} - {task['End Time']})")
                if st.button(f"✅ Done {i+1}", key=f"done_{i}"):
                    mark_task_done(i)
        else:
            st.write("🎉 No pending tasks!")

    elif view_selection == "Completed Tasks":
        st.markdown("<h3 style='color:#6a1b9a;'>✅ Completed Tasks</h3>", unsafe_allow_html=True)
        if history:
            for i, task in enumerate(history):
                st.write(f"📍 **{task['Task']}** (Completed: {task['Due Date']})")
                if st.button(f"📂 Archive {i+1}", key=f"archive_{i}"):
                    archive_task(i)
        else:
            st.write("📭 No completed tasks.")

    elif view_selection == "Archived Tasks":
        st.markdown("<h3 style='color:#6a1b9a;'>📦 Archived Tasks</h3>", unsafe_allow_html=True)
    
        if archived:
        # Convert archived tasks into a Pandas DataFrame for a structured table view
            archived_df = pd.DataFrame(archived)

        # Display the table with relevant columns
            st.dataframe(archived_df[['Task', 'Due Date']], use_container_width=True)
        else:
           st.write("📭 No archived tasks.")
