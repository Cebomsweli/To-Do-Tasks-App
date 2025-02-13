import streamlit as st
import json
import os
import hashlib
import pandas as pd
from datetime import datetime  # Import datetime to handle date inputs

# Function to hash PIN securely
def hash_pin(pin):
    return hashlib.sha256(pin.encode()).hexdigest()

# Function to get the file paths based on the username
def get_user_file_paths(username):
    tasks_file = f'{username}_tasks.json'
    history_file = f'{username}_history.json'
    archive_file = f'{username}_archive.json'
    pin_file = f'{username}_pin.json'  # Add pin file path
    return tasks_file, history_file, archive_file, pin_file

# Function to load user data from file
def load_user_data(username):
    tasks_file, history_file, archive_file, pin_file = get_user_file_paths(username)
    
    # Load tasks
    if os.path.exists(tasks_file):
        try:
            with open(tasks_file, 'r') as f:
                tasks = json.load(f)
        except json.JSONDecodeError:
            tasks = []
            st.warning("The tasks file was empty or corrupted. Starting fresh.")
    else:
        tasks = []

    # Load history
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r') as f:
                history = json.load(f)
        except json.JSONDecodeError:
            history = []
            st.warning("The history file was empty or corrupted. Starting fresh.")
    else:
        history = []

    # Load archived tasks
    if os.path.exists(archive_file):
        try:
            with open(archive_file, 'r') as f:
                archived = json.load(f)
        except json.JSONDecodeError:
            archived = []
            st.warning("The archive file was empty or corrupted. Starting fresh.")
    else:
        archived = []

    return tasks, history, archived

# Function to save user data to file
def save_user_data(username, tasks, history, archived):
    tasks_file, history_file, archive_file, pin_file = get_user_file_paths(username)
    
    with open(tasks_file, 'w') as f:
        json.dump(tasks, f)
    
    with open(history_file, 'w') as f:
        json.dump(history, f)
    
    with open(archive_file, 'w') as f:
        json.dump(archived, f)

# Function to save user PIN securely
def save_user_pin(username, pin):
    pin_file = f'{username}_pin.json'
    hashed_pin = hash_pin(pin)
    with open(pin_file, 'w') as f:
        json.dump({'pin': hashed_pin}, f)

# Function to check if the entered PIN matches the stored PIN
def check_user_pin(username, pin):
    pin_file = f'{username}_pin.json'
    if os.path.exists(pin_file):
        with open(pin_file, 'r') as f:
            stored_data = json.load(f)
            stored_pin = stored_data.get('pin')
            return stored_pin == hash_pin(pin)
    return False

# Add custom CSS for styling
st.markdown(""" 
    <style> 
        body { 
            background-color: #f5f3f9; 
            font-family: 'Arial', sans-serif; 
        } 
        .sidebar .sidebar-content { 
            background-color: #4b3f72; 
            color: white; 
            padding: 20px; 
        } 
        .sidebar .sidebar-header { 
            font-size: 1.5rem; 
            font-weight: bold; 
            color: white; 
            margin-bottom: 20px; 
        } 
        .sidebar .sidebar-divider { 
            border-bottom: 1px solid #7a6f98; 
            margin: 15px 0; 
        } 
        .sidebar .stRadio label { 
            color: white; 
            font-weight: bold; 
        } 
        .stButton > button { 
            background-color: #6a4c8c; 
            color: white; 
            border-radius: 5px; 
            padding: 10px; 
            width: 100%; 
        } 
        .stButton > button:hover { 
            background-color: #a47bf7; 
        } 
        .stTextInput input { 
            background-color: #e1d8e8; 
            border: 2px solid #6a4c8c; 
        } 
        .stTextInput input:focus { 
            border: 2px solid #a47bf7; 
        } 
        .stForm { 
            background-color: #f3e9f8; 
            padding: 20px; 
            border-radius: 10px; 
            box-shadow: 0px 4px 6px rgba(0,0,0,0.1); 
        } 
        .stTable { 
            border-collapse: collapse; 
            width: 100%; 
        } 
        .stTable th, .stTable td { 
            padding: 10px; 
            text-align: left; 
            border: 1px solid #ddd; 
        } 
        .stTable th { 
            background-color: #4b3f72; 
            color: white; 
        } 
        .stTable tr:nth-child(even) { 
            background-color: #f1e8f3; 
        } 
        .stTable tr:hover { 
            background-color: #d6c3e4; 
        } 
        .stAlert { 
            background-color: #d0a3f3; 
            border: 1px solid #a47bf7; 
        } 
        .sidebar .stButton > button { 
            background-color: #c96fa1; 
            color: white; 
            border-radius: 5px; 
            padding: 10px; 
            width: 100%; 
            margin-top: 10px; 
        } 
        .sidebar .stButton > button:hover { 
            background-color: #d8a2cc; 
        } 
    </style>
""", unsafe_allow_html=True)

# Step 1: Ask for a username and PIN before logging in
st.title("To-Do List App")

# Step 2: Get username and PIN only if not logged in
if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    username = st.text_input("Enter your username")
    pin = st.text_input("Enter your PIN", type="password")

    if username:
        pin_file = f'{username}_pin.json'
        if os.path.exists(pin_file):
            # If username exists, allow login
            if pin:
                if check_user_pin(username, pin):
                    st.session_state['username'] = username
                    st.session_state['logged_in'] = True
                    st.success(f"Welcome back, {username}!")
                else:
                    st.error("Incorrect PIN. Please try again.")
        else:
            # If username doesn't exist, allow account creation
            if pin:
                confirm_pin = st.text_input("Confirm your PIN", type="password")
                submit_button = st.button("Create Account")
                if submit_button:
                    if pin == confirm_pin:
                        # Save PIN and initialize user files
                        save_user_pin(username, pin)
                        tasks_file, history_file, archive_file, _ = get_user_file_paths(username)
                        with open(tasks_file, 'w') as f:
                            json.dump([], f)
                        with open(history_file, 'w') as f:
                            json.dump([], f)
                        with open(archive_file, 'w') as f:
                            json.dump([], f)
                        
                        st.session_state['username'] = username
                        st.session_state['logged_in'] = True
                        st.success("Account created successfully!")
                    else:
                        st.error("PINs do not match. Try again.")

# If user is already logged in, proceed with the app
if 'username' in st.session_state and st.session_state['logged_in']:
    # Load user's tasks, history, and archived tasks
    tasks, history, archived = load_user_data(st.session_state['username'])

    # Sidebar layout with title and view selection
    st.sidebar.markdown("<div class='sidebar-header'>Welcome, {}</div>".format(st.session_state['username']), unsafe_allow_html=True)
    view_selection = st.sidebar.radio("Select View", ["Add Task", "Pending Tasks", "Completed Tasks", "Archived Tasks"])

    # Sidebar divider
    st.sidebar.markdown("<div class='sidebar-divider'></div>", unsafe_allow_html=True)

    # Sidebar Logout Button
    if st.sidebar.button("Logout"):
        del st.session_state['username']
        del st.session_state['logged_in']
        st.rerun()  # Re-run the app to prompt for username again

    # Function to add task
    def add_task(task_name, task_date, start_time, end_time):
        task = {
            'task': task_name,
            'due_date': task_date.strftime('%Y-%m-%d'),
            'status': 'Pending',
            'start_time': start_time.strftime('%H:%M'),  # Save start time
            'end_time': end_time.strftime('%H:%M')       # Save end time
        }
        tasks.append(task)
        save_user_data(st.session_state['username'], tasks, history, archived)  # Save tasks after adding

    # Function to mark task as done
    def mark_task_done(task_index):
        task = tasks[task_index]
        task['status'] = 'Done'
        history.append(task)
        save_user_data(st.session_state['username'], tasks, history, archived)  # Save history and tasks after marking as done
        tasks.pop(task_index)
        save_user_data(st.session_state['username'], tasks, history, archived)  # Save tasks after removing

    # Function to archive task
    def archive_task(task_index):
        task = history[task_index]
        archived.append(task)
        history.pop(task_index)
        save_user_data(st.session_state['username'], tasks, history, archived)  # Save history and archived tasks after archiving

    # Handling the different views
    if view_selection == "Add Task":
        # Task input form with start and end time
        with st.form(key="add_task_form"):
            task_name = st.text_input("Task Name")
            task_date = st.date_input("Due Date", min_value=datetime.today())
            start_time = st.time_input("Start Time", value=datetime.now().time())
            end_time = st.time_input("End Time", value=datetime.now().time())
            submit_button = st.form_submit_button("Add Task")
            if submit_button:
                add_task(task_name, task_date, start_time, end_time)
                st.success("Task added successfully!")

    elif view_selection == "Pending Tasks":
        # Show pending tasks
        st.subheader("Pending Tasks")
        if tasks:
            for i, task in enumerate(tasks):
                st.write(f"{i+1}. {task['task']} (Due: {task['due_date']})")
                if st.button(f"Mark as Done {i+1}"):
                    mark_task_done(i)
                    st.success("Task marked as done.")
        else:
            st.write("No pending tasks.")

    elif view_selection == "Completed Tasks":
        # Show completed tasks (history)
        st.subheader("Completed Tasks")
        if history:
            # Create a DataFrame to display completed tasks in a table
            history_df = pd.DataFrame(history)
            history_df['Action'] = history_df.apply(lambda row: st.button(f"Archive Task {row.name}", key=row.name), axis=1)
            
            # Display the DataFrame as a table
            st.table(history_df.drop('Action', axis=1))

            # Check if a button was clicked for any task to archive it
            for i, task in enumerate(history):
                if history_df.loc[i, 'Action']:  # If the archive button is clicked
                    archive_task(i)  # Archive the task
                    st.success(f"Task '{task['task']}' has been archived.")
        else:
            st.write("No completed tasks.")

    elif view_selection == "Archived Tasks":
        # Show archived tasks
        st.subheader("Archived Tasks")
        if archived:
            for task in archived:
                st.write(f"{task['task']} (Archived: {task['due_date']})")
        else:
            st.write("No archived tasks.")
