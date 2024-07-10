import streamlit

SENDER_EMAIL_ID = streamlit.secrets["sender_email_id"]  # Fetch the users mail id
SENDER_PASSWORD = streamlit.secrets["sender_email_password"]  # Get user password

GEMINI_API_KEY = streamlit.secrets["gemini_api_key"]  # Fetch gemini1.5's api key
