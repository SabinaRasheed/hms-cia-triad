import streamlit as st
from database import get_db, init_db, log_action
from security import verify_password, anonymize_name, mask_contact
from datetime import datetime
import pandas as pd

st.set_page_config(page_title="Mini Hospital Management System", layout="centered")
# database Initialization
init_db()

# session state to track login state logged in user and last sync time
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None
if "last_sync" not in st.session_state:
    st.session_state.last_sync = None

def authenticate(username, password):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    user = cursor.fetchone()
    conn.close()
    if user and verify_password(password, user["password"]):
        return user
    return None

#Login screen is displayed here OK TA
if not st.session_state.logged_in:
    st.title("GDPR-Compliant Mini Hospital Management System")
    st.subheader("Login to Continue")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login", use_container_width=True):
        user = authenticate(username, password)
        if user:
            st.session_state.logged_in = True
            st.session_state.user = dict(user)
            st.success(f"Logged in as {user['role'].capitalize()}")
            st.session_state.last_sync = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            log_action(user["user_id"], user["role"], "Login", "User logged in")
        else:
            st.error("Invalid username or password.")

    st.stop()

user = st.session_state.user
role = user["role"]

# Sidebar 
st.sidebar.title("Navigation")
st.sidebar.write(f"👤 **{user['username']}** ({role.capitalize()})")
st.sidebar.markdown(f"**Last Sync:** {st.session_state.last_sync}")

# Logout
if st.sidebar.button("Logout", use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.user = None
    st.rerun()

#Role based user permissions
if role == "admin":
    menu_options = ["Dashboard", "View Logs", "Export Patients CSV"]
elif role == "doctor":
    menu_options = ["Dashboard", "View Patients (Anonymized)"]
elif role == "receptionist":
    menu_options = ["Dashboard", "Add Patient"]

selection = st.sidebar.radio("Menu", menu_options)


# ADMIN DASHBOARD
if role == "admin":
    if selection == "Dashboard":
        st.header("Admin Dashboard")
        st.write("Full system access available.")

    elif selection == "View Logs":
        st.header("Audit Logs")
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM logs ORDER BY timestamp DESC")
        logs = cursor.fetchall()
        conn.close()
        st.table([{k: log[k] for k in log.keys()} for log in logs])

    elif selection == "Export Patients CSV":
        st.header("Export Patients Data")
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patients")
        patients = cursor.fetchall()
        conn.close()
        df = pd.DataFrame([{k: p[k] for k in p.keys()} for p in patients])
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Patients CSV",
            data=csv,
            file_name="patients_data.csv",
            mime="text/csv"
        )
        st.success("Patients CSV ready to download!")

#Dco Dashbboard
elif role == "doctor":
    if selection == "Dashboard":
        st.header("Doctor Dashboard")
        st.write("View anonymized patient records.")

    elif selection == "View Patients (Anonymized)":
        st.header("Patients (Anonymized)")
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT anonymized_name, anonymized_contact, diagnosis, date_added FROM patients")
        patients = cursor.fetchall()
        conn.close()
        st.table([{k: p[k] for k in p.keys()} for p in patients])

#Receptionist dashboard
elif role == "receptionist":
    if selection == "Dashboard":
        st.header("Receptionist Dashboard")
        st.write("You can add new patient entries here.")

    elif selection == "Add Patient":
        st.header("Add New Patient")
        with st.form("add_patient_form"):
            name = st.text_input("Patient Name")
            contact = st.text_input("Contact Number")
            diagnosis = st.text_input("Diagnosis")
            submitted = st.form_submit_button("Add Patient")

            if submitted:
                anonymized = anonymize_name(name)
                masked_contact = mask_contact(contact)
                date_added = datetime.utcnow().isoformat()

                try:
                    conn = get_db()
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO patients (name, contact, diagnosis, anonymized_name, anonymized_contact, date_added)
                        VALUES (?,?,?,?,?,?)
                    """, (name, contact, diagnosis, anonymized, masked_contact, date_added))
                    conn.commit()
                    conn.close()
                    st.success(f"Patient '{name}' added successfully (anonymized).")
                    log_action(user["user_id"], role, "Add Patient", f"{name}, {contact}, {diagnosis}")
                    st.session_state.last_sync = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                except Exception as e:
                    st.error(f"Error adding patient: {e}")