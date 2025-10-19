# SGS Annual Function 2025 – Secure App (Streamlit)

Features:
- Mobile login with OTP (TEST_MODE: OTP shown on screen; swap with Firebase later)
- Allowed mobile verification (allowed_users.csv)
- Registration form (Name, Class, Section, Item, Contact, Address, Bus Yes/No)
- News & Notices (admin can post)
- Gallery (view for all; uploads for admin only)
- Admin area (password: sgs2025 by default)

## Run locally
pip install -r requirements.txt
streamlit run app.py

## Deploy (Streamlit Cloud)
Push to GitHub, set main file path to `app.py`.

## Android APK
Wrap this app URL in a WebView app via Android Studio to publish or side-load.
