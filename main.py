import time
import datetime
import numpy as np
import pandas as pd
from PIL import Image
import google.generativeai as genai

import streamlit as st
import streamlit_antd_components as sac

#Physical: Bloating, breast tenderness, headaches, fatigue, acne
#Emotional: Irritability, anxiety, mood swings, crying spells
#Behavioral: Food cravings, increased sleep, social withdrawal
#Cognitive: Difficulty concentrating, forgetfulness, brain fog

st.set_page_config(
    page_title="Flo: Your Period Buddy",
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


@st.experimental_dialog("Log Symptoms")
def log_symptoms_popup():
    physical_symptoms_list = ['Cramps', 'Headache', 'Bloating', 'Breast Tenderness', 'Fatigue', 'Back Pain', 'Acne', 'Nausea', 'Appetite Changes', 'Digestive Issues']
    logged_physical_symptoms = st.multiselect("Physical Symptoms", physical_symptoms_list, placeholder='Physical Symptoms')

    cola, colb = st.columns(2)
    with cola:
        logged_energy_level = st.selectbox("Energy levels", ['High', 'Moderate', 'Low'], index=None, placeholder="Energy levels")
    with colb:
        logged_sleep_quality = st.selectbox("Sleep quality", ['Good', 'Average', 'Poor'], index=None, placeholder="Sleep Quality")

    emotional_symptoms_list = ['Mood Swings', 'Irritation', 'Anxiety', 'Depression', 'Stress']
    logged_emotional_symptoms = st.multiselect("Emotional Symptoms", emotional_symptoms_list, placeholder='Emotional Symptoms')

    st.button("Log my Symptoms")


@st.experimental_dialog("Log Periods")
def log_menstrual_cycle_popup():
    tab_log_menstrual_cycle = sac.tabs(
        [
            sac.TabsItem(label="Periods Start"),
            sac.TabsItem(label="Periods End Reporting"),
        ],
        align="left",
    )

    if tab_log_menstrual_cycle == "Periods Start":
        date_first_period = st.date_input("Date of First Period", datetime.date(2019, 7, 6))
        notes_first_period = st.text_area("Notes", placeholder="Additional comments or observation", label_visibility='collapsed')
        
        st.button("Log Cycle Beginning")

    elif tab_log_menstrual_cycle == "Periods End Reporting":
        cola, colb = st.columns(2)
        with cola:
            date_first_period = st.date_input("Date of First Period", datetime.date(2019, 7, 6))
        with colb:
            date_last_period = st.date_input("Date of Last Period", datetime.date(2019, 7, 6))

        flow_intensity = st.selectbox("Flow Intensity", ['Light', 'Medium', 'Heavy'], index=None, placeholder="Flow Intensity", label_visibility='collapsed')
        #medications_taken = st.text_input("Medications", placeholder="Medications Taken", label_visibility='collapsed')

        notes_first_period = st.text_area("Notes", placeholder="Additional comments or observation", label_visibility='collapsed')
        
        st.button("Log Cycle End")


if __name__ == "__main__":
    with st.sidebar:
        selected_menu_item = sac.menu(
            [
                sac.MenuItem(
                    "My Dashboard",
                    icon="grid",
                ),
                sac.MenuItem(
                    "Flo Community",
                    icon="clipboard-pulse",
                ),
                sac.MenuItem(
                    "Chat with FloAI",
                    icon="chat-square-text",
                ),
                sac.MenuItem(" ", disabled=True),
                sac.MenuItem(type="divider"),
            ],
            open_all=True,
        )

    if selected_menu_item == "My Dashboard":
        with st.sidebar:
            with st.container(height=310, border=False):
                with st.expander("Analyze Symptoms", expanded=True):
                    st.text_area("Enter your symptoms", placeholder="Enter your symptoms", label_visibility="collapsed")
                    st.button("Analyze Symptoms", use_container_width=True)

            if st.button("My Profile", use_container_width=True):
                st.switch_page("pages/user_profile.py")

        st.markdown(
            """
            <style>
                .custom-h6-bmi {
                    font-size: 18px; /* Adjust the font size as needed */
                    margin-bottom: 0px;
                    padding: 0px;
                }
                .custom-font-size-bmi {
                    font-size: 36px; /* Adjust the font size as needed */
                }
            </style>
            """,
            unsafe_allow_html=True,
        )

        # Homepage - top ribbon
        ribbon_col_1, ribbon_col_2, ribbon_col_3 = st.columns([4.6, 1, 0.4])

        with ribbon_col_1:
            st.markdown("<H4>Welcome Bhavna</H4>", unsafe_allow_html=True)
        
        with ribbon_col_2:
            if st.button("🛍️ Marketplace", use_container_width=True):
                st.switch_page("pages/marketplace.py")

        with ribbon_col_3:
            notificatons_button = st.button("🔔", use_container_width=True)
        st.write(" ")

        dashboard_hero_section_1, dashboard_hero_section_2 = st.columns([0.9, 1.75])

        # Homepage - User Profile Card
        with dashboard_hero_section_1:
            patient_details_container = dashboard_hero_section_1.container(height=397, border=True)
            patient_details_container.write(" ")

            user_profile_image_path = "assets/user_profile/profile_photo.png"
            patient_details_container.image(
                user_profile_image_path, use_column_width=True
            )
            patient_details_container.markdown(
                f"""<H5 style="padding: 0px 0px;"><center>Bhavna Mukherjee</H5></center>""", unsafe_allow_html=True
            )
            patient_details_container.markdown(
                f"""<center>Flo Username: @bhavnamukherjee</center>""", unsafe_allow_html=True
            )
            patient_details_container.markdown(
                f"<center>Period Flow in 4 days (expected)</center>", unsafe_allow_html=True
            )
            patient_details_container.write(" ")
            with patient_details_container:
                if st.button("Log Menstrual Cycle", use_container_width=True):
                    log_menstrual_cycle_popup()

        with dashboard_hero_section_2:
            dashboard_hero_section_2a, dashboard_hero_section_2b = st.columns([1, 1])

            # Homepage - Cycle Length Card
            with dashboard_hero_section_2a:
                bmi_details_container = st.container(border=True)
                bmi_details_container.image(
                    Image.open("assets/application/smiley_icon.png").resize((33, 33))
                )

                bmi_details_container.markdown(
                    f'<span class="custom-h6-bmi">Average Cycle Length:</span><BR><span class="custom-font-size-bmi"><B>28</span> Days</B> (Basis last four cycles)',
                    unsafe_allow_html=True,
                )

            # Homepage - Fertility Score Card
            with dashboard_hero_section_2b:
                muac_details_container = st.container(border=True)

                muac_details_container.image(
                    Image.open("assets/application/smiley_icon.png").resize((33, 33))
                )
                muac_details_container.markdown(
                    f'<span class="custom-h6-bmi">Current Menstrual Phase:</span><BR><span style="font-size: 20px;">#</span><B><span class="custom-font-size-bmi">18</span></B> (High Chance of Pregnancy)',
                    unsafe_allow_html=True,
                )

            with st.container(border=True, height=212):
                st.markdown(
                    "<H6>Cycle Lengths - Last 10 Cycles</H6>", unsafe_allow_html=True
                )

                st.line_chart(
                    np.random.randn(20, 1),
                    height=150,
                    use_container_width=True,
                )

        # Homepage - middle ribbon
        mid_ribbon_col_1, mid_ribbon_col_2 = st.columns([4.75, 1,])

        with mid_ribbon_col_1:
            st.markdown("<H4>Your Historical Data</H4>", unsafe_allow_html=True)

        with mid_ribbon_col_2:
            if st.button("Log Symptoms", use_container_width=True):
                log_symptoms_popup()

        reports_and_plans_hero_section_1, reports_and_plans_hero_section_2 = st.columns(
            [2, 1]
        )

        with reports_and_plans_hero_section_1:
            with st.container(border=True, height=410):
                tab_selection_visit_history_or_lab_reports = sac.tabs(
                    [
                        sac.TabsItem(label="Cycle History"),
                        sac.TabsItem(label="Logged Symptoms"),
                    ],
                    align="left",
                )


                if tab_selection_visit_history_or_lab_reports == "Cycle History":
                    for index in [1,2,3,4]:
                        cola, colb, colc = st.columns([0.75, 3.5, 2])
                        with cola:
                            all_icons = [
                                "assets/application/smiley_icon.png",
                            ]
                            st.image(Image.open(all_icons[0]).resize((50, 50)))

                        with colb:
                            st.markdown(
                                f"<B>Jan 12 - Jan 19, 2024</B><BR>You had a regular cycle of 26 days",
                                unsafe_allow_html=True,
                            )

                        with colc:
                            st.link_button(
                                f"View Report",
                                url="https://www.google.com/",
                                use_container_width=True,
                            )

                        if index < 4:
                            st.markdown(
                                """<hr style="height:1px;margin:0px;padding:0px;border:none;color:#111;background-color:#111;" /> """,
                                unsafe_allow_html=True,
                            )

                else:
                    st.markdown("<BR>" * 2, unsafe_allow_html=True)
                    sac.result(
                        label="No Symptoms logged",
                        description="Help us keep track of your health by logging your symptoms",
                        status="empty",
                    )

        with reports_and_plans_hero_section_2:
            with st.container(border=True, height=205):
                st.markdown(
                    "<H5>Weekly Meal Plan</H5>",
                    unsafe_allow_html=True,
                )

                st.markdown(
                    """
                    <p align='justify'>Healthy vegetarian meal structured to provide a daily intake of approx 1800 cals, divided across four meals!!</p>
                    """,
                    unsafe_allow_html=True,
                )

                st.button("Download Meal Plan", use_container_width=True, type="primary", key="_button_meal_plan")

            with st.container(border=True, height=189):
                st.markdown(
                    "<H5>Exercise Routine</H5>",
                    unsafe_allow_html=True,
                )

                st.markdown(
                    """
                    <p align='justify'>Daily exercise routines designed to complement your overall well-being!</p>
                    """,
                    unsafe_allow_html=True,
                )

                st.button("Download Exercise Routine", use_container_width=True, type="primary", key="_button_exercise_routine")

        bottom_ribbon_col_1, bottom_ribbon_col_2 = st.columns([4.75, 1,])

        with bottom_ribbon_col_1:
            st.markdown("<H4>Educational Resources</H4>", unsafe_allow_html=True)

        with st.container(border=True):

            cola, colb, colc = st.columns(3)

            with cola:
                st.image(Image.open("assets/application/blog_banner_1.png"), use_column_width=True)
                st.markdown(
                    "<H6>Fitness article 1</H6><P align='justify'>Lorem ipsum dolor sit amet, conseur adipiscing elit ul sellus imperdiet, rnulla</P>",
                    unsafe_allow_html=True,
                )

            with colb:
                st.image(Image.open("assets/application/blog_banner_2.png"), use_column_width=True)
                st.markdown(
                    "<H6>Fitness article 1</H6><P align='justify'>Lorem ipsum dolor sit amet, conseur adipiscing elit ul sellus imperdiet, rnulla</P>",
                    unsafe_allow_html=True,
                )

            with colc:
                st.image(Image.open("assets/application/blog_banner_3.png"), use_column_width=True)
                st.markdown(
                    "<H6>Fitness article 1</H6><P align='justify'>Lorem ipsum dolor sit amet, conseur adipiscing elit ul sellus imperdiet, rnulla</P>",
                    unsafe_allow_html=True,
                )

    elif selected_menu_item == "Flo Community":
        with st.sidebar:
            with st.container(height=310, border=False):
                st.success("Stay hydrated and incorporate light exercises to reduce bloating & ease premenstrual symptoms.", icon=":material/thread_unread:")

            if st.button("My Profile", use_container_width=True):
                st.switch_page("pages/user_profile.py")

        st.markdown(
            """
            <style>
                .custom-h6-bmi {
                    font-size: 18px; /* Adjust the font size as needed */
                    margin-bottom: 0px;
                    padding: 0px;
                }
                .custom-font-size-bmi {
                    font-size: 36px; /* Adjust the font size as needed */
                }
            </style>
            """,
            unsafe_allow_html=True,
        )

        # Homepage - top ribbon
        ribbon_col_1, ribbon_col_2, ribbon_col_3 = st.columns([4.6, 1, 0.4])

        with ribbon_col_1:
            st.markdown("<H4>Flo Community</H4>", unsafe_allow_html=True)

        with ribbon_col_2:
            if st.button("🛍️ Marketplace", use_container_width=True):
                st.switch_page("pages/marketplace.py")

        with ribbon_col_3:
            notificatons_button = st.button("🔔", use_container_width=True)
        st.write(" ")

        mid_ribbon_col_1, mid_ribbon_col_2 = st.columns([2, 1,])

        with mid_ribbon_col_1:
            with st.expander("📝 Create and Share your Post", expanded=False):
                with st.form("_create_post", border=False):                
                    st.text_area("Type your post here", placeholder="What's on your mind?", label_visibility="collapsed")

                    st.file_uploader("Attachment", type=['png', 'jpg'], accept_multiple_files=False, label_visibility="collapsed")

                    col_button, _, _ = st.columns([1.5, 1, 1])
                    col_button.form_submit_button("Share my Post", use_container_width=True, type="primary")

        with mid_ribbon_col_2:
            with st.container(border=True):
                st.markdown("<H6>Hot Topics</H6>", unsafe_allow_html=True)

                for i in [1, 2, 3, 4, 5]:
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        st.image(Image.open("assets/application/smiley_icon.png").resize((50, 50)))
                    with col2:
                        st.markdown(
                            f"<B>A Hot Topic</B><BR>Description of hot topic",
                            unsafe_allow_html=True,
                        )

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
                        Image.open("assets/application/blog_banner_1.png"), use_column_width=True
                    )

        with mid_ribbon_col_1:
            for i in [1,2,3,4,5]:
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

                    cola, colb, colc, _, _, _, colx = st.columns([1,1,1,1,1,1,4])

                    with cola:
                        st.button("👍", use_container_width=True, key=f"_like_button_{i}")

                    with colb:
                        st.button("👎", use_container_width=True, key=f"_save_button_{i}")

                    with colx:
                        st.button("⚠️ Report this Post", use_container_width=True, key=f"_report_post_button_{i}")

                    #st.markdown(
                    #    """<hr style="height:1px;margin:0px;padding:0px;border:none;color:#111;background-color:#111;" /> """,
                    #    unsafe_allow_html=True,
                    #)
            
            st.write(" ")
            ans = sac.pagination(page_size=5, align='center', variant='light', jump=True, show_total=True)

        with mid_ribbon_col_2:
            with st.container(border=True):
                st.markdown("<H6>Top Creators</H6>", unsafe_allow_html=True)
                
                for i in [1, 2, 3, 4, 5, 6, 7, 8]:
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        st.image(Image.open("assets/application/smiley_icon.png").resize((50, 50)))
                    with col2:
                        st.markdown(
                            f"<B>Full Name</B><BR>Shared 13 Posts recently",
                            unsafe_allow_html=True,
                        )

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

    elif selected_menu_item == "Chat with FloAI":
        with st.sidebar:
            with st.container(height=310, border=False):
                st.warning(
                    "**⚠️ Our chatbots are experimental!** It may display inaccurate info. Kindly double-check, for response accuracy."
                )

            if st.button("My Profile", use_container_width=True):
                st.switch_page("pages/user_profile.py")

        st.write(" ")

        # Homepage - top ribbon
        ribbon_col_1, ribbon_col_2, ribbon_col_3 = st.columns([4.6, 1, 0.4])

        with ribbon_col_1:
            st.markdown("<H4>Chat with Agent</H4>", unsafe_allow_html=True)
        
        with ribbon_col_2:
            if st.button("🛍️ Marketplace", use_container_width=True):
                st.switch_page("pages/marketplace.py")

        with ribbon_col_3:
            notificatons_button = st.button("🔔", use_container_width=True)
        st.write(" ")

        genai.configure(api_key="AIzaSyBcdHMULkpfokjNJ7ai6ek7R_CYRpPtBHE")

        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Type your message here..."):
            st.session_state.messages.append({"role": "user", "content": prompt})

            with st.chat_message("user"):
                st.markdown(prompt)
            
            safe = [
                {
                    "category": "HARM_CATEGORY_MEDICAL",
                    "threshold": "BLOCK_NONE",
                },
            ]

            model = genai.GenerativeModel(model_name='gemini-pro')
            chat = model.start_chat()
            
            response_from_model = chat.send_message(
                "You are a highly qualified menstrual health expert. Under 75 words, answer this user query:\n\nQuestion: " + prompt,
                stream=True,
            )

            print(response_from_model)

            def response_generator(response):
                for word in response:
                    yield word.text
                    time.sleep(0.05)

            with st.chat_message("assistant"):
                try:
                    response = st.write_stream(
                        response_generator(response_from_model)
                    )
                except:
                    response = st.markdown(
                        "Sorry, I am unable to answer this."
                    )

            st.session_state.messages.append(
                {"role": "assistant", "content": response}
            )
