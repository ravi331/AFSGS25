
import streamlit as st
import pandas as pd
from datetime import datetime
import os
import random

# ---------------- CONFIG ----------------
APP_TITLE = "SGS Annual Function 2025"
ADMIN_PASSWORD = "sgs2025"                   # change in production
EVENT_DATE = "2025-12-20 17:00:00"           # YYYY-MM-DD HH:MM:SS
TEST_OTP_MODE = True                         # True: show OTP on screen (for testing), False: use real OTP (Firebase)
REG_FILE = "registrations.csv"
NOTICE_FILE = "notices.csv"
ALLOWED_FILE = "allowed_users.csv"
IMG_DIR = "gallery_images"
VID_DIR = "gallery_videos"
# ----------------------------------------

st.set_page_config(page_title=APP_TITLE, layout="wide")

# Ensure data files exist
def ensure_csv(path, headers):
    if not os.path.exists(path):
        pd.DataFrame(columns=headers).to_csv(path, index=False)

ensure_csv(REG_FILE, ["Timestamp","Name","Class","Section","Item","Contact","Address","Bus","Status"])
ensure_csv(NOTICE_FILE, ["Timestamp","Title","Message","PostedBy"])
ensure_csv(ALLOWED_FILE, ["mobile_number","student_name","class","section"])

# Load data
reg_df = pd.read_csv(REG_FILE, dtype=str)
notice_df = pd.read_csv(NOTICE_FILE, dtype=str)
allowed_df = pd.read_csv(ALLOWED_FILE, dtype=str)

# ---------------- AUTH (Mobile + OTP) ----------------
if "authed" not in st.session_state:
    st.session_state.authed = False
if "mobile" not in st.session_state:
    st.session_state.mobile = ""

def is_mobile_allowed(mobile: str) -> bool:
    if allowed_df.empty:  # if empty, deny all for safety
        return False
    return mobile.strip() in allowed_df["mobile_number"].astype(str).str.strip().values

def generate_otp():
    return f"{random.randint(100000, 999999)}"

def login_ui():
    st.sidebar.title("User Login")
    mobile = st.sidebar.text_input("Enter mobile number", max_chars=15, key="login_mobile")
    if st.sidebar.button("Send OTP"):
        if not mobile:
            st.sidebar.error("Please enter a mobile number.")
        elif not is_mobile_allowed(mobile):
            st.sidebar.error("This number is not registered for the Annual Function.")
        else:
            otp = generate_otp()
            st.session_state["_otp_expected"] = otp
            st.session_state["_otp_mobile"] = mobile
            if TEST_OTP_MODE:
                st.sidebar.info(f"TEST MODE OTP: {otp}")
            else:
                st.sidebar.info("OTP sent. Please check your phone.")  # Hook Firebase here
    if st.session_state.get("_otp_expected"):
        code = st.sidebar.text_input("Enter OTP", max_chars=6)
        if st.sidebar.button("Verify OTP"):
            if code == st.session_state.get("_otp_expected"):
                st.session_state.authed = True
                st.session_state.mobile = st.session_state.get("_otp_mobile","")
                st.sidebar.success("Login successful!")
                # cleanup
                st.session_state.pop("_otp_expected", None)
                st.session_state.pop("_otp_mobile", None)
            else:
                st.sidebar.error("Incorrect OTP. Try again.")

login_ui()

# Gate content
if not st.session_state.authed:
    st.title(APP_TITLE)
    st.write("Please login from the sidebar to access the app.")
    st.stop()

# ---------------- MAIN TABS ----------------
tabs = st.tabs(["🏠 Home","🗞️ News & Notices","🕒 Day & Time","📝 Registration","📋 Registered List","🖼️ Gallery","🔧 Admin"])

# ---------- Home ----------
with tabs[0]:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=260)
    st.title("St. Gregorios H.S. School")
    st.subheader("45th Annual Day - Talent Meets Opportunity")
    if os.path.exists("mascot.png"):
        st.image("mascot.png", width=260)

    # Countdown
    try:
        event_dt = datetime.strptime(EVENT_DATE, "%Y-%m-%d %H:%M:%S")
        now = datetime.now()
        delta = event_dt - now
        if delta.total_seconds() > 0:
            days = delta.days
            hours = (delta.seconds)//3600
            minutes = (delta.seconds % 3600)//60
            st.markdown(f"### 🎉 Event on **{EVENT_DATE.split(' ')[0]}** • Starts in **{days}d {hours}h {minutes}m**")
        else:
            st.markdown("### 🎉 The Annual Function has begun!")
    except Exception as e:
        st.warning("Invalid EVENT_DATE format.")

# ---------- News & Notices ----------
with tabs[1]:
    st.header("Latest News & Notices")
    if notice_df.empty:
        st.info("No notices yet.")
    else:
        for _, row in notice_df.sort_values(by="Timestamp", ascending=False).iterrows():
            st.markdown(f"**{row.get('Title','')}**  \n{row.get('Message','')}  \n*Posted by {row.get('PostedBy','Admin')}*")
    st.caption("Notices are added by admins from the Admin tab.")

# ---------- Day & Time ----------
with tabs[2]:
    st.header("Event Schedule")
    st.info("Upload your detailed schedule PDF in Admin tab (coming soon) or add a schedule CSV and display it here.")

# ---------- Registration ----------
with tabs[3]:
    st.header("Student Registration")
    st.caption("Your mobile will be used as contact by default.")
    with st.form("reg_form"):
        name = st.text_input("Student Name")
        sclass = st.text_input("Class")
        sec = st.text_input("Section")
        item = st.text_input("Item Name / Performance")
        contact = st.text_input("Contact Number", value=st.session_state.mobile)
        address = st.text_area("Address")
        bus = st.radio("Availing School Bus for the Event?", ["Yes", "No"], horizontal=True)
        submitted = st.form_submit_button("Register")
        if submitted:
            if not all([name, sclass, sec, item, contact]):
                st.error("Please fill all required fields (Name, Class, Section, Item, Contact).")
            else:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                row = {
                    "Timestamp": timestamp,
                    "Name": name,
                    "Class": sclass,
                    "Section": sec,
                    "Item": item,
                    "Contact": contact,
                    "Address": address,
                    "Bus": bus,
                    "Status": "Pending"
                }
                df = pd.read_csv(REG_FILE, dtype=str)
                df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
                df.to_csv(REG_FILE, index=False)
                st.success(f"{name} registered successfully!")

# ---------- Registered List ----------
with tabs[4]:
    st.header("All Registrations")
    reg_df = pd.read_csv(REG_FILE, dtype=str)
    if reg_df.empty:
        st.info("No registrations yet.")
    else:
        st.dataframe(reg_df.sort_values(by="Timestamp", ascending=False), use_container_width=True)

# ---------- Gallery ----------
with tabs[5]:
    st.header("📸 Photo & 🎬 Video Gallery")
    # Images
    img_files = [f for f in os.listdir(IMG_DIR) if f.lower().endswith((".png",".jpg",".jpeg",".gif",".bmp"))] if os.path.isdir(IMG_DIR) else []
    if img_files:
        st.subheader("Photos")
        cols = st.columns(3)
        for i, fname in enumerate(img_files):
            with cols[i % 3]:
                st.image(os.path.join(IMG_DIR, fname), use_column_width=True)
    else:
        st.info("No images yet.")

    # Videos
    vid_files = [f for f in os.listdir(VID_DIR) if f.lower().endswith((".mp4",".mov",".mkv",".webm",".avi"))] if os.path.isdir(VID_DIR) else []
    if vid_files:
        st.subheader("Videos")
        for fname in vid_files:
            st.video(os.path.join(VID_DIR, fname))
    else:
        st.info("No videos yet.")

# ---------- Admin ----------
with tabs[6]:
    st.header("Admin")
    admin_pw = st.text_input("Enter Admin Password", type="password")
    if st.button("Login as Admin"):
        if admin_pw == ADMIN_PASSWORD:
            st.success("Admin access granted.")
            st.session_state["is_admin"] = True
        else:
            st.error("Incorrect admin password.")
    if st.session_state.get("is_admin"):
        st.subheader("Post a New Notice")
        with st.form("notice_form"):
            title = st.text_input("Notice Title")
            message = st.text_area("Message")
            posted_by = st.text_input("Posted By", value="Admin")
            post_btn = st.form_submit_button("Post Notice")
            if post_btn:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                df = pd.read_csv(NOTICE_FILE, dtype=str)
                df = pd.concat([df, pd.DataFrame([{"Timestamp":timestamp,"Title":title,"Message":message,"PostedBy":posted_by}])], ignore_index=True)
                df.to_csv(NOTICE_FILE, index=False)
                st.success("Notice posted.")

        st.subheader("Upload Gallery Media")
        img_upload = st.file_uploader("Upload Image(s)", type=["png","jpg","jpeg","gif","bmp"], accept_multiple_files=True, key="up_imgs")
        if st.button("Save Images"):
            if img_upload:
                for file in img_upload:
                    with open(os.path.join(IMG_DIR, file.name), "wb") as f:
                        f.write(file.getbuffer())
                st.success(f"Saved {len(img_upload)} image(s).")
            else:
                st.info("No images selected.")

        vid_upload = st.file_uploader("Upload Video(s)", type=["mp4","mov","mkv","webm","avi"], accept_multiple_files=True, key="up_vids")
        if st.button("Save Videos"):
            if vid_upload:
                for file in vid_upload:
                    with open(os.path.join(VID_DIR, file.name), "wb") as f:
                        f.write(file.getbuffer())
                st.success(f"Saved {len(vid_upload)} video(s).")
            else:
                st.info("No videos selected.")

        st.subheader("Allowed Mobile Numbers")
        st.dataframe(allowed_df, use_container_width=True)
        st.caption("Only these mobile numbers can request OTP.")

        new_mobile = st.text_input("Add a mobile number")
        new_name = st.text_input("Student Name")
        new_class = st.text_input("Class")
        new_sec = st.text_input("Section")
        if st.button("Add Mobile"):
            if new_mobile:
                df = pd.read_csv(ALLOWED_FILE, dtype=str)
                df = pd.concat([df, pd.DataFrame([{"mobile_number":new_mobile.strip(),"student_name":new_name,"class":new_class,"section":new_sec}])], ignore_index=True)
                df.to_csv(ALLOWED_FILE, index=False)
                st.success("Mobile added to allowed list. (Reload to see latest.)")
            else:
                st.error("Please enter a mobile number.")
    else:
        st.info("Enter the admin password above to manage notices, gallery, and allowed users.")
