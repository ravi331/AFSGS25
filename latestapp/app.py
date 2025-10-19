import streamlit as st
import pandas as pd
from datetime import datetime
import os
import random

# ---------- CONFIG ----------
ADMIN_PASSWORD = "sgs2025"
EVENT_DATE = "2025-12-20 17:00:00"
TEST_OTP_MODE = True  # OTP shown on screen for testing
REG_FILE = "registrations.csv"
NOTICE_FILE = "notices.csv"
ALLOWED_FILE = "allowed_users.csv"
# -----------------------------

st.set_page_config(page_title="SGS Annual Function 2025", layout="wide")

def load_csv(file, columns):
    if not os.path.exists(file):
        pd.DataFrame(columns=columns).to_csv(file, index=False)
    return pd.read_csv(file, dtype=str)

reg_df = load_csv(REG_FILE, ["Timestamp","Name","Class","Section","Item","Contact","Address","Bus","Status"])
notice_df = load_csv(NOTICE_FILE, ["Timestamp","Title","Message","PostedBy"])
allowed_df = load_csv(ALLOWED_FILE, ["mobile_number","student_name","class","section"])

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ---------- LOGIN SECTION ----------
def is_valid_user(mobile):
    if len(mobile) != 10 or not mobile.isdigit():
        return False
    return mobile in allowed_df["mobile_number"].astype(str).values

def login():
    st.sidebar.title("Login")
    mobile = st.sidebar.text_input("Enter Mobile (10 digits)")

    if st.sidebar.button("Send OTP"):
        if is_valid_user(mobile):
            otp = str(random.randint(100000, 999999))
            st.session_state.otp = otp
            st.session_state.mobile = mobile
            if TEST_OTP_MODE:
                st.sidebar.success(f"OTP sent (Test Mode): {otp}")
        else:
            st.sidebar.error("❌ This number is not registered or invalid")

    if "otp" in st.session_state:
        entered = st.sidebar.text_input("Enter OTP")
        if st.sidebar.button("Verify OTP"):
            if entered == st.session_state.otp:
                st.session_state.logged_in = True
                st.sidebar.success("✅ Login successful!")
                st.session_state.pop("otp")
            else:
                st.sidebar.error("Incorrect OTP")

login()
if not st.session_state.logged_in:
    st.stop()

# ---------- TABS ----------
tabs = st.tabs(["🏠 Home", "📝 Registration", "📋 Registered List", "📢 Notices", "⚙ Admin"])

# Home
with tabs[0]:
    st.title("St. Gregorios H.S. School")
    st.subheader("45th Annual Day - Talent Meets Opportunity")
    st.success("Welcome! You are logged in.")

# Registration
with tabs[1]:
    st.header("Student Registration")
    with st.form("reg_form"):
        name = st.text_input("Student Name")
        clas = st.text_input("Class")
        sec = st.text_input("Section")
        item = st.text_input("Performance Item")
        contact = st.text_input("Contact Number", value=st.session_state.mobile)
        address = st.text_area("Address")
        bus = st.radio("Using School Bus?", ["Yes", "No"])
        submit = st.form_submit_button("Register")

        if submit:
            if not name or not clas or not sec or not item:
                st.error("All fields are required")
            else:
                df = pd.read_csv(REG_FILE)
                df.loc[len(df)] = [datetime.now(), name, clas, sec, item, contact, address, bus, "Pending"]
                df.to_csv(REG_FILE, index=False)
                st.success("✅ Registered Successfully!")

# Registered List
with tabs[2]:
    st.header("All Registrations")
    df = pd.read_csv(REG_FILE)
    st.dataframe(df)

# Notices
with tabs[3]:
    st.header("📢 Notices Board")
    if notice_df.empty:
        st.info("No notices yet.")
    else:
        for _, row in notice_df.iterrows():
            st.markdown(f"**{row['Title']}**  \n{row['Message']}  \n*Posted by {row['PostedBy']}*")

# Admin Panel
with tabs[4]:
    st.header("Admin Panel")
    pw = st.text_input("Enter Admin Password", type="password")
    if st.button("Login as Admin"):
        if pw == ADMIN_PASSWORD:
            st.success("✅ Admin Access Granted")

            # Post Notice
            st.subheader("Post a Notice")
            with st.form("notice_form"):
                title = st.text_input("Title")
                message = st.text_area("Notice")
                posted_by = st.text_input("Posted By", value="Admin")
                if st.form_submit_button("Post"):
                    df = pd.read_csv(NOTICE_FILE)
                    df.loc[len(df)] = [datetime.now(), title, message, posted_by]
                    df.to_csv(NOTICE_FILE, index=False)
                    st.success("✅ Notice Posted")
        else:
            st.error("Incorrect password")
