import time
import datetime
import numpy as np
import pandas as pd
from PIL import Image
import google.generativeai as genai

import streamlit as st
import streamlit_antd_components as sac

st.set_page_config(
    page_title="Flo: Marketplace",
    page_icon="assets/favicon/flo_favicon.png",
    initial_sidebar_state="expanded",
    layout="wide",
)

st.markdown(
    """
        <style>
               .block-container {
                    padding-top: 1.75rem;
                    padding-bottom: 1rem;
                }
        </style>
        """,
    unsafe_allow_html=True,
)


if "themes" not in st.session_state:
    st.session_state.themes = {
        "current_theme": "dark",
        "refreshed": True,
        "light": {
            "theme.base": "dark",
            "theme.backgroundColor": "#111111",
            "theme.primaryColor": "#FFC0CB",
            "theme.secondaryBackgroundColor": "#181818",
            "theme.textColor": "#FFFFFF",
            "button_face": "🌜",
        },
        "dark": {
            "theme.base": "light",
            "theme.backgroundColor": "#fdfefe",
            "theme.primaryColor": "#FFC0CB",
            "theme.secondaryBackgroundColor": "#f0f2f5",
            "theme.textColor": "#333333",
            "button_face": "🌞",
        },
    }

def change_streamlit_theme():
    previous_theme = st.session_state.themes["current_theme"]
    tdict = (
        st.session_state.themes["light"]
        if st.session_state.themes["current_theme"] == "light"
        else st.session_state.themes["dark"]
    )

    for vkey, vval in tdict.items():
        if vkey.startswith("theme"):
            st._config.set_option(vkey, vval)

    st.session_state.themes["refreshed"] = False

    if previous_theme == "dark":
        st.session_state.themes["current_theme"] = "light"

    elif previous_theme == "light":
        st.session_state.themes["current_theme"] = "dark"


if st.session_state.themes["refreshed"] == False:
    st.session_state.themes["refreshed"] = True
    st.rerun()


if __name__ == "__main__":
    if 1 == 1:
        with st.sidebar:
            with st.container(height=485, border=False):
                st.image(
                    Image.open("assets/user_profile/profile_photo.png"),
                    use_column_width=True,
                )

                cola, colb = st.columns(2)

                st.selectbox("Dietary Preferences", ("A", "B"), placeholder="Select your Dietary Preferences", index=None, label_visibility='collapsed')
                
                options = st.multiselect(
                    "List your Allergies",
                    ["Green", "Yellow", "Red", "Blue"],
                    placeholder="List your Allergies", label_visibility='collapsed'
                )

                options = st.multiselect(
                    "List Medical Conditions",
                    ["Green", "Yellow", "Red", "Blue"],
                    placeholder="List your Medical Conditions", label_visibility='collapsed'
                )

            if st.button("Return to Dashboard", use_container_width=True):
                st.switch_page("main.py")

        st.markdown(
            """
            <style>
                .custom-h6-bmi {
                    font-size: 16px; /* Adjust the font size as needed */
                    margin-bottom: 0px;
                    padding: 0px;
                }
                .custom-font-size-bmi {
                    font-size: 16px; /* Adjust the font size as needed */
                }
            </style>
            """,
            unsafe_allow_html=True,
        )

        # Homepage - top ribbon
        ribbon_col_1, ribbon_col_2, ribbon_col_3 = st.columns([4.6, 1, 0.4])

        with ribbon_col_1:
            st.markdown("<H4>Manage your Profile</H4>", unsafe_allow_html=True)
        
        with ribbon_col_2:
            if st.button("🛍️ Marketplace", use_container_width=True):
                st.switch_page("pages/marketplace.py")

        with ribbon_col_3:
            btn_face = (
                st.session_state.themes["light"]["button_face"]
                if st.session_state.themes["current_theme"] == "light"
                else st.session_state.themes["dark"]["button_face"]
            )

            st.button(
                btn_face,
                use_container_width=True,
                type="secondary",
                on_click=change_streamlit_theme,
            )
        #st.write(" ")
        st.markdown("Loerem inpsum dolor mit inpsum dolor mit inpsum dolorii mit inpsum dolor mit inpsum dolor mit inpsum dolor mitinpsum dolor mit inpsum dolor mit inpsum dolor mitinpsum dolor mitinpsum dolor mit inpsum dolor mit inpsum dolor mit inpsum dolor mitaii", unsafe_allow_html=True)

        selected_profile_tab = sac.tabs([
            sac.TabsItem(label='Personal Details'),
            sac.TabsItem(label='Published Posts'),
        ], variant='outline')

        if selected_profile_tab == "Personal Details":
            with st.container(border=True):
                st.markdown("<H6>Edit Your Personal Details</H6>", unsafe_allow_html=True)
                    
                cola, colb = st.columns(2)

                with cola:
                    st.text_input("Full Name", placeholder="Bhavna Mukherjee")
                with colb:
                    st.date_input("Date of Birth", datetime.date(2019, 7, 6))

                cola, colb, colc = st.columns(3)

                with cola:
                    st.text_input("Height", placeholder="Bhavna Mukherjee")
                with colb:
                    st.text_input("Weight", placeholder="Bhavna Mukherjee")
                with colc:
                    st.text_input("Phone No.", placeholder="Bhavna Mukherjee")

                st.text_area("Preent Address", placeholder="This is a long address line")
                st.file_uploader("Profile Picture", accept_multiple_files=False)

                cola, _, _ = st.columns(3)
                with cola:
                    st.button("Save your Changes", type='primary', use_container_width=True)

        else:
            mid_ribbon_col_1, mid_ribbon_col_2 = st.columns([2, 1,])

            with mid_ribbon_col_2:
                with st.container(border=True):
                    st.markdown("<H6>Your Analytics</H6>", unsafe_allow_html=True)
                    
                    for i in [1, 2, 3, 4]:
                        col1, col2 = st.columns([1, 3])
                        with col1:
                            st.image(Image.open("assets/application/smiley_icon.png").resize((50, 50)))
                        with col2:
                            st.markdown(
                                f"<B>Full Name</B><BR>Shared 13 Posts recently",
                                unsafe_allow_html=True,
                            )

            with mid_ribbon_col_1:
                for i in [1,2,3]:
                    with st.container(border=True):

                        col1, col2 = st.columns([1,9])

                        with col1:
                            st.image(
                                Image.open("assets/application/smiley_icon.png").resize((33, 33)), use_column_width=True
                            )
                        with col2:
                            st.markdown("<B>Charlotte Flair</B><BR>Jan 24, 2024 at 02:34 PM", unsafe_allow_html=True)
                        
                        st.markdown("Assembly Line Innovation: Ford revolutionized manufacturing with th all newe introduction of the moving assembly line in 1913, drastically reducing the time it took to build a car from over 12 hours to just 2 hours and 30 minutes.")

                        st.image(
                            Image.open("assets/application/blog_banner_3.png"), use_column_width=True
                        )

                        cola, colc, _, _, _, colx = st.columns([2,1,1,1,1,4])

                        with cola:
                            st.button("✏️ Edit", use_container_width=True, key=f"_like_button_{i}")

                        with colx:
                            st.button("❌ Delete this Post", use_container_width=True, key=f"_report_post_button_{i}")

            with mid_ribbon_col_2:
                with st.container(border=True):
                    st.markdown("<H6>Sponsored</H6>", unsafe_allow_html=True)
                    
                    col1, col2 = st.columns([1, 3])

                    with col1:
                        st.image(Image.open("assets/application/smiley_icon.png").resize((50, 50)))

                    with col2:
                        st.markdown(
                            f"<B>A Hot Topic</B><BR>Description of hot topic",
                            unsafe_allow_html=True,
                        )
                        st.image(
                            Image.open("assets/application/blog_banner_2.png"), use_column_width=True
                        )
