import time
import math
import datetime
import numpy as np
import pandas as pd
from PIL import Image
import google.generativeai as genai

import streamlit as st
import streamlit_antd_components as sac

from backend.genai_engine import FloAI
from backend.database import UserDB, CyclesDB, PeriodsDB, SymptomsDB
from backend.database import PostsDB, NotificationsDB, CredentialsDB
from configs import credentials


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


if "user_authentication_status" not in st.session_state:
    st.session_state.user_authentication_status = None

if "signup_full_name" not in st.session_state:
    st.session_state.signup_full_name = None

if "signup_dob" not in st.session_state:
    st.session_state.signup_dob = None

if "signup_height" not in st.session_state:
    st.session_state.signup_height = None

if "signup_weight" not in st.session_state:
    st.session_state.signup_weight = None

if "signup_dietary_preferences" not in st.session_state:
    st.session_state.signup_dietary_preferences = None

if "signup_address" not in st.session_state:
    st.session_state.signup_address = None

if "signup_profile_pic" not in st.session_state:
    st.session_state.signup_profile_pic = None

if "signup_phone_no" not in st.session_state:
    st.session_state.signup_phone_no = None

if "signup_allergies" not in st.session_state:
    st.session_state.signup_allergies = []

if "signup_medical_conditions" not in st.session_state:
    st.session_state.signup_medical_conditions = []

if "signup_cycle_length" not in st.session_state:
    st.session_state.signup_cycle_length = None

if "signup_periods_length" not in st.session_state:
    st.session_state.signup_periods_length = None

if "signup_uploaded_profile_pic" not in st.session_state:
    st.session_state.signup_uploaded_profile_pic = None

if "logged_in_username" not in st.session_state:
    st.session_state.logged_in_username = None


@st.experimental_dialog("Notifications")
def display_latest_notification():
    notifications_db = NotificationsDB()
    notifications_list = notifications_db.fetch_notifications_for_user(
        logged_in_username, limit=5
    )

    for notifs in notifications_list:
        if notifs[1] == "all":
            st.info(notifs[3], icon=":material/drafts:")
        else:
            st.info(notifs[3], icon=":material/forum:")


@st.experimental_dialog("Edit Cycle Details")
def edit_periods_details(start_date, end_date, flow_intensity, notes):
    with st.form("_edit_period_details_form", clear_on_submit=False, border=True):
        st.markdown("<H4>Edit Periods Details</H4>", unsafe_allow_html=True)

        colx, coly = st.columns(2)

        with colx:
            start_date = st.date_input(
                "Start Date",
                datetime.datetime.strptime(start_date, "%Y-%m-%d"),
                disabled=True,
            )
        with coly:
            new_end_date = st.date_input(
                "End Date", datetime.datetime.strptime(end_date, "%Y-%m-%d")
            )

        flow_intensity_list = ["Light", "Medium", "Heavy"]
        flow_intensity_pre_selected_option = flow_intensity_list.index(flow_intensity)

        new_flow_intensity = st.selectbox(
            "Flow Intensity",
            flow_intensity_list,
            index=flow_intensity_pre_selected_option,
        )
        new_notes = st.text_area("Observations", value=notes)

        colb3, colb4 = st.columns([1, 1.75])
        with colb3:
            save_changes_button = st.form_submit_button(
                "💾 Save Changes", use_container_width=True
            )

        if save_changes_button:
            periodsdb = PeriodsDB()
            periodsdb.edit_period(
                logged_in_username,
                start_date,
                end_date=new_end_date,
                flow_intensity=new_flow_intensity,
                notes=new_notes,
            )

            st.success("Your changes have been saved successfully!", icon="✔️")
            time.sleep(5)
            st.rerun()

        with colb4:
            if st.form_submit_button("❌"):
                st.rerun()


@st.experimental_dialog("Edit Cycle Details")
def edit_cycle_details(start_date, end_date):
    st.markdown(
        f"Editing details for the menstrual cycle starting on {datetime.datetime.strptime(start_date, '%Y-%m-%d').strftime('%B %d')}",
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        colx, coly = st.columns(2)

        with colx:
            new_start_date = st.date_input(
                "Start Date",
                datetime.datetime.strptime(start_date, "%Y-%m-%d"),
                disabled=True,
            )
        with coly:
            new_end_date = st.date_input(
                "End Date", datetime.datetime.strptime(end_date, "%Y-%m-%d")
            )

        calculated_cycle_length = (new_end_date - new_start_date).days + 1
        new_cycle_length = st.text_input(
            "Cycle Length", value=str(calculated_cycle_length), disabled=True
        )

        colb1, colb2 = st.columns([1, 1.75])

        with colb1:
            save_changes_button = st.button("💾 Save Changes", use_container_width=True)

        if save_changes_button:
            cyclesdb = CyclesDB()
            cyclesdb.edit_cycle(
                logged_in_username,
                start_date,
                end_date=new_end_date,
                cycle_length=new_cycle_length,
            )

            st.success("Your changes have been saved successfully!", icon="✔️")
            time.sleep(2)
            st.rerun()

        with colb2:
            discard_changes_button = st.button("❌")

        if discard_changes_button:
            st.rerun()


@st.experimental_dialog("Cycles Details")
def display_cycle_details(start_date=None, end_date=None, cycle_length=None):
    cola, colb = st.columns([7, 1])
    with cola:
        st.markdown(
            f"<H4>{datetime.datetime.strptime(start_date, '%Y-%m-%d').strftime('%b %d')} to {datetime.datetime.strptime(end_date, '%Y-%m-%d').strftime('%b %d, %Y')}</H4>You logged a complete menstrual cycle of {cycle_length} days",
            unsafe_allow_html=True,
        )
        st.markdown("<BR>", unsafe_allow_html=True)

    selected_tab = sac.tabs(
        [
            sac.TabsItem(label="Periods Details"),
            sac.TabsItem(label="Logged Symptoms"),
        ],
        variant="outline",
    )

    if selected_tab == "Periods Details":
        cola, colb = st.columns([7, 1])

        periodsdb = PeriodsDB()
        (
            _,
            _,
            periods_start_date,
            periods_end_date,
            flow_intensity,
            notes,
        ) = periodsdb.get_period(logged_in_username, start_date)

        with cola:
            st.markdown(
                f"<H4>You had periods from {datetime.datetime.strptime(periods_start_date, '%Y-%m-%d').strftime('%b %d')} to {datetime.datetime.strptime(periods_end_date, '%Y-%m-%d').strftime('%b %d, %Y')}</H4><B>• Intensity:</B> {flow_intensity}<BR><B>• Notes Logged by User:</B> {notes}<BR><BR>",
                unsafe_allow_html=True,
            )

    else:
        symptomsdb = SymptomsDB()
        symptoms_logged_between_two_dates = symptomsdb.get_symptoms_between_two_dates(
            logged_in_username, start_date, end_date
        )

        if len(symptoms_logged_between_two_dates) >= 1:
            for symptom in symptoms_logged_between_two_dates:
                st.markdown(
                    f"<B>{datetime.datetime.strptime(symptom[2], '%Y-%m-%d').strftime('%B %d')}</B><BR> • Physical Symptoms: {symptom[3]} <BR> • Energy level: {symptom[4]} <BR> • Sleep Quality: {symptom[5]} <BR> • Emotional Symptoms: {symptom[6]}<BR>",
                    unsafe_allow_html=True,
                )

        else:
            sac.result(
                label="No Symptoms logged",
                description="Help us keep track of your health by logging your symptoms",
                status="empty",
            )


@st.experimental_dialog("Log Symptoms")
def log_symptoms_popup():
    ist_date = datetime.datetime.utcnow() + datetime.timedelta(hours=5, minutes=30)
    logged_date = st.date_input("Select Date", ist_date.date())

    physical_symptoms_list = [
        "Cramps",
        "Headache",
        "Bloating",
        "Breast Tenderness",
        "Fatigue",
        "Back Pain",
        "Acne",
        "Nausea",
        "Appetite Changes",
        "Digestive Issues",
    ]
    logged_physical_symptoms = st.multiselect(
        "Physical Symptoms", physical_symptoms_list, placeholder="Physical Symptoms"
    )

    cola, colb = st.columns(2)
    with cola:
        logged_energy_level = st.selectbox(
            "Energy levels",
            ["High", "Moderate", "Low"],
            index=None,
            placeholder="Energy levels",
        )
    with colb:
        logged_sleep_quality = st.selectbox(
            "Sleep quality",
            ["Good", "Average", "Poor"],
            index=None,
            placeholder="Sleep Quality",
        )

    emotional_symptoms_list = [
        "Mood Swings",
        "Irritation",
        "Anxiety",
        "Depression",
        "Stress",
    ]
    logged_emotional_symptoms = st.multiselect(
        "Emotional Symptoms", emotional_symptoms_list, placeholder="Emotional Symptoms"
    )

    if st.button("Log my Symptoms"):
        logged_physical_symptoms = ", ".join(logged_physical_symptoms)
        logged_emotional_symptoms = ", ".join(logged_emotional_symptoms)

        symptomsdb = SymptomsDB()
        symptomsdb.add_symptoms(
            logged_in_username,
            logged_date,
            physical_symptoms=logged_physical_symptoms,
            energy_level=logged_energy_level,
            sleep_quality=logged_sleep_quality,
            emotional_symptoms=logged_emotional_symptoms,
        )

        st.success("Your symptoms have been logged successfully!", icon="✔️")
        time.sleep(5)
        st.rerun()


@st.experimental_dialog("Log Periods")
def log_menstrual_cycle_popup(logged_in_username):
    tab_log_menstrual_cycle = sac.tabs(
        [
            sac.TabsItem(label="Log Periods Start"),
            sac.TabsItem(label="Periods End Reporting"),
        ],
        align="left",
    )

    if tab_log_menstrual_cycle == "Log Periods Start":
        ist_date = datetime.datetime.utcnow() + datetime.timedelta(hours=5, minutes=30)

        date_first_period = st.date_input("Date of First Period", ist_date.date())
        notes_first_period = st.text_area(
            "Notes",
            placeholder="Additional comments or observation",
            label_visibility="collapsed",
        )

        if st.button("Log Cycle Beginning"):
            userdb = UserDB()
            (
                _,
                _,
                _,
                _,
                _,
                _,
                _,
                _,
                _,
                _,
                _,
                logged_in_users_avg_cycle_length,
                logged_in_users_avg_periods_length,
            ) = userdb.get_user(logged_in_username)

            date_last_period = date_first_period + datetime.timedelta(
                days=logged_in_users_avg_periods_length
            )

            periodsdb = PeriodsDB()
            generated_periods_id = periodsdb.add_period(
                logged_in_username,
                date_first_period.strftime("%Y-%m-%d"),
                date_last_period.strftime("%Y-%m-%d"),
            )

            date_last_cycle = date_first_period + datetime.timedelta(
                days=logged_in_users_avg_cycle_length
            )

            cyclesdb = CyclesDB()
            cyclesdb.add_cycle(
                date_first_period.strftime("%Y-%m-%d"),
                date_last_cycle.strftime("%Y-%m-%d"),
                generated_periods_id,
                logged_in_username,
            )

            st.success("Your Cycle has been logged successfully", icon="✔️")
            time.sleep(5)
            st.rerun()

    elif tab_log_menstrual_cycle == "Periods End Reporting":
        periodsdb = PeriodsDB()
        latest_periods = periodsdb.fetch_latest_periods(logged_in_username, 3)

        latest_periods_start_dates = []

        for period in latest_periods:
            latest_periods_start_dates.append(period[2])

        date_first_period = st.selectbox(
            "Date of First Period",
            latest_periods_start_dates,
            index=None,
        )

        if date_first_period:
            cola, colb = st.columns(2)

            periodsdb = PeriodsDB()
            (
                _,
                _,
                _,
                logged_end_date,
                logged_flow_intenity,
                logged_notes,
            ) = periodsdb.get_period(logged_in_username, date_first_period)

            with cola:
                new_period_end_date = st.date_input(
                    "Date of Last Period",
                    datetime.datetime.strptime(logged_end_date, "%Y-%m-%d"),
                )
            with colb:
                flow_intensity_list = ["Light", "Medium", "Heavy"]
                flow_intensity_pre_selected_option = flow_intensity_list.index(
                    logged_flow_intenity
                )

                new_flow_intensity = st.selectbox(
                    "Flow Intensity",
                    flow_intensity_list,
                    index=flow_intensity_pre_selected_option,
                )

            new_notes = st.text_area("Observations", value=logged_notes)

            if st.button("Log Periods Details"):
                periodsdb = PeriodsDB()
                periodsdb.edit_period(
                    logged_in_username,
                    date_first_period,
                    end_date=new_period_end_date,
                    flow_intensity=new_flow_intensity,
                    notes=new_notes,
                )

                st.success("Changes saved successfully", icon="✔️")
                time.sleep(5)
                st.rerun()

        else:
            st.info(
                "You can edit details of only the last three period cycles", icon="ℹ️"
            )


if __name__ == "__main__":
    if st.session_state.user_authentication_status == True:
        logged_in_username = st.session_state.logged_in_username

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
            floai = FloAI()

            with st.sidebar:
                sidebar_container = st.container(height=325, border=False)
                with sidebar_container:
                    with st.expander("🧪 Analyze Symptoms", expanded=False):
                        query_symptoms = st.text_area(
                            "Enter your symptoms",
                            placeholder="Enter your symptoms",
                            label_visibility="collapsed",
                        )

                        if st.button("Analyze Symptoms", use_container_width=True):
                            response = floai.analyze_symptoms(query_symptoms)

                            display_ai_response = st.info(response)
                            time.sleep(7)
                            display_ai_response.empty()

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

            ribbon_col_1, ribbon_col_2, ribbon_col_3 = st.columns([4.6, 1, 0.4])

            userdb = UserDB()
            (
                _,
                logged_in_users_full_name,
                logged_in_users_dob,
                logged_in_users_height,
                logged_in_users_weight,
                _,
                _,
                logged_in_users_profile_pic_url,
                _,
                _,
                _,
                logged_in_users_avg_cycle_length,
                logged_in_users_avg_periods_length,
            ) = userdb.get_user(logged_in_username)

            with ribbon_col_1:
                st.markdown(
                    f"<H4>Hey, Hello {logged_in_users_full_name.split()[0]} 🌼</H4>",
                    unsafe_allow_html=True,
                )

            with ribbon_col_2:
                if st.button("🛍️ Marketplace", use_container_width=True):
                    st.switch_page("pages/marketplace.py")

            with ribbon_col_3:
                if st.button("🔔", use_container_width=True):
                    display_latest_notification()

            st.write(" ")

            dashboard_hero_section_1, dashboard_hero_section_2 = st.columns([0.9, 1.75])

            with dashboard_hero_section_1:
                patient_details_container = dashboard_hero_section_1.container(
                    height=397, border=True
                )
                patient_details_container.write(" ")

                patient_details_container.image(
                    logged_in_users_profile_pic_url, use_column_width=True
                )
                patient_details_container.markdown(
                    f"""<H5 style="padding: 0px 0px;"><center>{logged_in_users_full_name}</H5></center>""",
                    unsafe_allow_html=True,
                )
                patient_details_container.markdown(
                    f"""<center>Flo Username: {logged_in_username}</center>""",
                    unsafe_allow_html=True,
                )

                dob = datetime.datetime.strptime(logged_in_users_dob, "%Y-%m-%d")
                today = datetime.datetime.today()
                logged_in_users_age = (
                    today.year
                    - dob.year
                    - ((today.month, today.day) < (dob.month, dob.day))
                )

                total_inches = logged_in_users_height * 0.393701

                patient_details_container.markdown(
                    f"<center>Age: {logged_in_users_age} • Height: {int(total_inches // 12)}'{int(total_inches % 12)}\" • Weight: {int(logged_in_users_weight)} kg</center>",
                    unsafe_allow_html=True,
                )
                patient_details_container.write(" ")
                with patient_details_container:
                    if st.button("🩸 Log Menstrual Cycle", use_container_width=True):
                        log_menstrual_cycle_popup(logged_in_username)

            with dashboard_hero_section_2:
                dashboard_hero_section_2a, dashboard_hero_section_2b = st.columns(
                    [1, 1]
                )

                with dashboard_hero_section_2a:
                    bmi_details_container = st.container(border=True)
                    bmi_details_container.image(
                        Image.open("assets/app_graphics/yellow_hearthand.png").resize(
                            (33, 33)
                        )
                    )

                    bmi_details_container.markdown(
                        f'<span class="custom-h6-bmi">Average Cycle Length:</span><BR><span class="custom-font-size-bmi"><B>{logged_in_users_avg_cycle_length}</span> Days</B> (Periods Length: {logged_in_users_avg_periods_length} days)',
                        unsafe_allow_html=True,
                    )

                with dashboard_hero_section_2b:
                    muac_details_container = st.container(border=True)

                    muac_details_container.image(
                        Image.open("assets/app_graphics/green_heartshake.png").resize(
                            (33, 33)
                        )
                    )

                    try:
                        cyclesdb = CyclesDB()
                        (
                            _,
                            start_date_str,
                            end_date_str,
                            cycle_length,
                            _,
                            _,
                        ) = cyclesdb.fetch_latest_cycles(logged_in_username, 1)[0]

                        start_date = datetime.datetime.strptime(
                            start_date_str, "%Y-%m-%d"
                        ).date()
                        end_date = datetime.datetime.strptime(
                            end_date_str, "%Y-%m-%d"
                        ).date()

                        today = datetime.datetime.utcnow() + datetime.timedelta(
                            hours=5, minutes=30
                        )
                        today = today.date()

                        if today > end_date:
                            sidebar_container.warning(
                                "Please Log Your Menstrual Cycle", icon="⚠️"
                            )
                            muac_details_container.markdown(
                                f'<span class="custom-h6-bmi">Current Menstrual Phase:</span><BR><B><span class="custom-font-size-bmi">NA</span></B> (Your Last Cycle has Ended)',
                                unsafe_allow_html=True,
                            )

                        else:
                            days_since_start = (today - start_date).days + 1

                            if (
                                days_since_start
                                <= logged_in_users_avg_periods_length + 1
                            ):
                                fertility = "low"
                                sidebar_container.success(
                                    "You've Low Chance of Pregnancy", icon="ℹ️"
                                )

                            elif (
                                days_since_start > logged_in_users_avg_periods_length
                            ) and (
                                days_since_start
                                <= (logged_in_users_avg_cycle_length / 2 - 2)
                            ):
                                sidebar_container.info(
                                    "Moderate Chance of Pregnancy", icon="ℹ️"
                                )

                            elif (
                                days_since_start
                                > (logged_in_users_avg_cycle_length / 2 - 2)
                            ) and (
                                days_since_start
                                <= (logged_in_users_avg_cycle_length / 2 + 2)
                            ):
                                sidebar_container.error(
                                    "You've High Chance of Pregnancy", icon="ℹ️"
                                )

                            elif (
                                days_since_start
                                > (logged_in_users_avg_cycle_length / 2 + 2)
                            ) and (
                                days_since_start
                                <= (
                                    logged_in_users_avg_cycle_length
                                    - logged_in_users_avg_periods_length
                                )
                            ):
                                sidebar_container.info(
                                    "Moderate Chance of Pregnancy", icon="ℹ️"
                                )

                            else:
                                sidebar_container.info(
                                    "Low Chance of Pregnancy", icon="ℹ️"
                                )

                            muac_details_container.markdown(
                                f'<span class="custom-h6-bmi">Current Menstrual Phase:</span><BR><span style="font-size: 20px;"></span><B><span class="custom-font-size-bmi">Day {days_since_start }</span></B> (Started on {datetime.datetime.strptime(start_date_str, "%Y-%m-%d").strftime("%b %d")})',
                                unsafe_allow_html=True,
                            )
                    except:
                        sidebar_container.warning(
                            "Please Log Your Menstrual Cycle", icon="⚠️"
                        )
                        muac_details_container.markdown(
                            f'<span class="custom-h6-bmi">Current Menstrual Phase:</span><BR><B><span class="custom-font-size-bmi">Unavailable</span></B>',
                            unsafe_allow_html=True,
                        )

                with st.container(border=True, height=212):
                    cyclesdb = CyclesDB()
                    last_10_cycles = cyclesdb.fetch_latest_cycles(
                        logged_in_username, 15
                    )

                    if len(last_10_cycles) > 4:
                        st.markdown(
                            "<H6>📅 Cycle Lengths - Last 15 Cycles</H6>",
                            unsafe_allow_html=True,
                        )

                        cycle_lengths = []
                        for cycle in last_10_cycles:
                            cycle_lengths.append([cycle[1], cycle[3]])

                        df = pd.DataFrame(
                            cycle_lengths, columns=["Start Date", "Cycle Length"]
                        )
                        df["Start Date"] = pd.to_datetime(df["Start Date"])
                        df.set_index("Start Date", inplace=True)

                        st.bar_chart(
                            df,
                            height=150,
                            use_container_width=True,
                        )
                    else:
                        sac.result(
                            label="Insights are not Available",
                            description="Log atleast 5 cycles to start seeing your insights",
                            status="empty",
                        )

            mid_ribbon_col_1, mid_ribbon_col_2 = st.columns(
                [
                    4.25,
                    1,
                ]
            )

            with mid_ribbon_col_1:
                st.markdown("<H4>Your Historical Data</H4>", unsafe_allow_html=True)

            with mid_ribbon_col_2:
                if st.button("🌡️ Log Symptoms", use_container_width=True):
                    log_symptoms_popup()

            (
                reports_and_plans_hero_section_1,
                reports_and_plans_hero_section_2,
            ) = st.columns([2, 1.05])

            with reports_and_plans_hero_section_1:
                with st.container(border=True, height=410):
                    tab_selection_visit_history_or_lab_reports = sac.tabs(
                        [
                            sac.TabsItem(label="Cycle History"),
                            sac.TabsItem(label="Periods History"),
                        ],
                        align="left",
                    )

                    if tab_selection_visit_history_or_lab_reports == "Cycle History":
                        cyclesdb = CyclesDB()
                        cycle_details = cyclesdb.fetch_latest_cycles(
                            logged_in_username, 4
                        )

                        if len(cycle_details) > 0:
                            try:
                                cycle_1_details = cycle_details[0]
                                cola, colb, colc, cold = st.columns(
                                    [0.75, 3.4, 1.4, 0.6]
                                )

                                with cola:
                                    all_icons = [
                                        "assets/app_graphics/trident_red.png",
                                    ]
                                    st.image(Image.open(all_icons[0]).resize((50, 50)))

                                with colb:
                                    st.markdown(
                                        f"<B>{datetime.datetime.strptime(cycle_1_details[1], '%Y-%m-%d').strftime('%b %d')} to {datetime.datetime.strptime(cycle_1_details[2], '%Y-%m-%d').strftime('%b %d, %Y')}</B><BR>You had a menstrual cycle of {cycle_1_details[3]} days",
                                        unsafe_allow_html=True,
                                    )

                                with colc:
                                    if st.button(
                                        f"View Details",
                                        use_container_width=True,
                                        key="_button_cycle_1_details",
                                    ):
                                        display_cycle_details(
                                            cycle_1_details[1],
                                            cycle_1_details[2],
                                            cycle_1_details[3],
                                        )

                                with cold:
                                    if st.button(
                                        "✏️",
                                        use_container_width=True,
                                        key="_button_cycle_1_details_edit",
                                    ):
                                        edit_cycle_details(
                                            cycle_1_details[1], cycle_1_details[2]
                                        )

                                st.markdown(
                                    """<hr style="height:1px;margin:0px;padding:0px;border:none;color:#111;background-color:#111;" /> """,
                                    unsafe_allow_html=True,
                                )

                            except Exception as err:
                                pass

                            try:
                                cycle_2_details = cycle_details[1]
                                cola, colb, colc, cold = st.columns(
                                    [0.75, 3.4, 1.4, 0.6]
                                )

                                with cola:
                                    all_icons = [
                                        "assets/app_graphics/trident_blue.png",
                                    ]
                                    st.image(Image.open(all_icons[0]).resize((50, 50)))

                                with colb:
                                    st.markdown(
                                        f"<B>{datetime.datetime.strptime(cycle_2_details[1], '%Y-%m-%d').strftime('%b %d')} to {datetime.datetime.strptime(cycle_2_details[2], '%Y-%m-%d').strftime('%b %d, %Y')}</B><BR>You had a menstrual cycle of {cycle_2_details[3]} days",
                                        unsafe_allow_html=True,
                                    )

                                with colc:
                                    if st.button(
                                        f"View Details",
                                        use_container_width=True,
                                        key="_button_cycle_2_details",
                                    ):
                                        display_cycle_details(
                                            cycle_2_details[1],
                                            cycle_2_details[2],
                                            cycle_2_details[3],
                                        )

                                with cold:
                                    if st.button(
                                        "✏️",
                                        use_container_width=True,
                                        key="_button_cycle_2_details_edit",
                                    ):
                                        edit_cycle_details(
                                            cycle_2_details[1], cycle_2_details[2]
                                        )

                                st.markdown(
                                    """<hr style="height:1px;margin:0px;padding:0px;border:none;color:#111;background-color:#111;" /> """,
                                    unsafe_allow_html=True,
                                )

                            except Exception as err:
                                pass

                            try:
                                cycle_3_details = cycle_details[2]
                                cola, colb, colc, cold = st.columns(
                                    [0.75, 3.4, 1.4, 0.6]
                                )

                                with cola:
                                    all_icons = [
                                        "assets/app_graphics/trident_yellow.png",
                                    ]
                                    st.image(Image.open(all_icons[0]).resize((50, 50)))

                                with colb:
                                    st.markdown(
                                        f"<B>{datetime.datetime.strptime(cycle_3_details[1], '%Y-%m-%d').strftime('%b %d')} to {datetime.datetime.strptime(cycle_3_details[2], '%Y-%m-%d').strftime('%b %d, %Y')}</B><BR>You had a menstrual cycle of {cycle_3_details[3]} days",
                                        unsafe_allow_html=True,
                                    )

                                with colc:
                                    if st.button(
                                        f"View Details",
                                        use_container_width=True,
                                        key="_button_cycle_3_details",
                                    ):
                                        display_cycle_details(
                                            cycle_3_details[1],
                                            cycle_3_details[2],
                                            cycle_3_details[3],
                                        )

                                with cold:
                                    if st.button(
                                        "✏️",
                                        use_container_width=True,
                                        key="_button_cycle_3_details_edit",
                                    ):
                                        edit_cycle_details(
                                            cycle_3_details[1], cycle_3_details[2]
                                        )

                                st.markdown(
                                    """<hr style="height:1px;margin:0px;padding:0px;border:none;color:#111;background-color:#111;" /> """,
                                    unsafe_allow_html=True,
                                )

                            except Exception as err:
                                pass

                            try:
                                cycle_4_details = cycle_details[3]
                                cola, colb, colc, cold = st.columns(
                                    [0.75, 3.4, 1.4, 0.6]
                                )
                                with cola:
                                    all_icons = [
                                        "assets/app_graphics/trident_green.png",
                                    ]
                                    st.image(Image.open(all_icons[0]).resize((50, 50)))

                                with colb:
                                    st.markdown(
                                        f"<B>{datetime.datetime.strptime(cycle_4_details[1], '%Y-%m-%d').strftime('%b %d')} to {datetime.datetime.strptime(cycle_4_details[2], '%Y-%m-%d').strftime('%b %d, %Y')}</B><BR>You had a menstrual cycle of {cycle_4_details[3]} days",
                                        unsafe_allow_html=True,
                                    )

                                with colc:
                                    if st.button(
                                        f"View Details",
                                        use_container_width=True,
                                        key="_button_cycle_4_details",
                                    ):
                                        display_cycle_details(
                                            cycle_4_details[1],
                                            cycle_4_details[2],
                                            cycle_4_details[3],
                                        )

                                with cold:
                                    if st.button(
                                        "✏️",
                                        use_container_width=True,
                                        key="_button_cycle_4_details_edit",
                                    ):
                                        edit_cycle_details(
                                            cycle_4_details[1], cycle_4_details[2]
                                        )

                            except Exception as err:
                                pass

                        else:
                            st.markdown("<BR>" * 2, unsafe_allow_html=True)
                            sac.result(
                                label="No Cycles Logged",
                                description="Details of your logged cycle will appear here",
                                status="empty",
                            )

                    else:
                        periodsdb = PeriodsDB()
                        four_latest_periods = periodsdb.fetch_latest_periods(
                            logged_in_username, 4
                        )

                        if len(four_latest_periods) > 0:
                            try:
                                period_1 = four_latest_periods[0]
                                cola, colb, colc = st.columns([0.75, 3.6, 1.9])

                                with cola:
                                    all_icons = [
                                        "assets/app_graphics/trident_red.png",
                                    ]
                                    st.image(Image.open(all_icons[0]).resize((50, 50)))

                                with colb:
                                    st.markdown(
                                        f"<B>{datetime.datetime.strptime(period_1[2], '%Y-%m-%d').strftime('%b %d')} to {datetime.datetime.strptime(period_1[3], '%Y-%m-%d').strftime('%b %d, %Y')}</B><BR>You logged periods of {period_1[4]} intensity",
                                        unsafe_allow_html=True,
                                    )

                                with colc:
                                    if st.button(
                                        f"✏️ Edit Details",
                                        use_container_width=True,
                                        key="_button_periods_1",
                                    ):
                                        edit_periods_details(
                                            period_1[2],
                                            period_1[3],
                                            period_1[4],
                                            period_1[5],
                                        )

                                st.markdown(
                                    """<hr style="height:1px;margin:0px;padding:0px;border:none;color:#111;background-color:#111;" /> """,
                                    unsafe_allow_html=True,
                                )

                            except Exception as err:
                                pass

                            try:
                                period_2 = four_latest_periods[1]
                                cola, colb, colc = st.columns([0.75, 3.6, 1.9])

                                with cola:
                                    all_icons = [
                                        "assets/app_graphics/trident_blue.png",
                                    ]
                                    st.image(Image.open(all_icons[0]).resize((50, 50)))

                                with colb:
                                    st.markdown(
                                        f"<B>{datetime.datetime.strptime(period_2[2], '%Y-%m-%d').strftime('%b %d')} to {datetime.datetime.strptime(period_2[3], '%Y-%m-%d').strftime('%b %d, %Y')}</B><BR>You logged periods of {period_2[4]} intensity",
                                        unsafe_allow_html=True,
                                    )

                                with colc:
                                    if st.button(
                                        f"✏️ Edit Details",
                                        use_container_width=True,
                                        key="_button_periods_2",
                                    ):
                                        edit_periods_details(
                                            period_2[2],
                                            period_2[3],
                                            period_2[4],
                                            period_2[5],
                                        )

                                st.markdown(
                                    """<hr style="height:1px;margin:0px;padding:0px;border:none;color:#111;background-color:#111;" /> """,
                                    unsafe_allow_html=True,
                                )

                            except Exception as err:
                                pass

                            try:
                                period_3 = four_latest_periods[2]
                                cola, colb, colc = st.columns([0.75, 3.6, 1.9])

                                with cola:
                                    all_icons = [
                                        "assets/app_graphics/trident_yellow.png",
                                    ]
                                    st.image(Image.open(all_icons[0]).resize((50, 50)))

                                with colb:
                                    st.markdown(
                                        f"<B>{datetime.datetime.strptime(period_3[2], '%Y-%m-%d').strftime('%b %d')} to {datetime.datetime.strptime(period_3[3], '%Y-%m-%d').strftime('%b %d, %Y')}</B><BR>You logged periods of {period_3[4]} intensity",
                                        unsafe_allow_html=True,
                                    )

                                with colc:
                                    if st.button(
                                        f"✏️ Edit Details",
                                        use_container_width=True,
                                        key="_button_periods_3",
                                    ):
                                        edit_periods_details(
                                            period_3[2],
                                            period_3[3],
                                            period_3[4],
                                            period_3[5],
                                        )

                                st.markdown(
                                    """<hr style="height:1px;margin:0px;padding:0px;border:none;color:#111;background-color:#111;" /> """,
                                    unsafe_allow_html=True,
                                )

                            except Exception as err:
                                pass

                            try:
                                period_4 = four_latest_periods[3]
                                cola, colb, colc = st.columns([0.75, 3.6, 1.9])

                                with cola:
                                    all_icons = [
                                        "assets/app_graphics/trident_green.png",
                                    ]
                                    st.image(Image.open(all_icons[0]).resize((50, 50)))

                                with colb:
                                    st.markdown(
                                        f"<B>{datetime.datetime.strptime(period_4[2], '%Y-%m-%d').strftime('%b %d')} to {datetime.datetime.strptime(period_4[3], '%Y-%m-%d').strftime('%b %d, %Y')}</B><BR>You logged periods of {period_4[4]} intensity",
                                        unsafe_allow_html=True,
                                    )

                                with colc:
                                    if st.button(
                                        f"✏️ Edit Details",
                                        use_container_width=True,
                                        key="_button_periods_4",
                                    ):
                                        edit_periods_details(
                                            period_4[2],
                                            period_4[3],
                                            period_4[4],
                                            period_4[5],
                                        )

                                st.markdown(
                                    """<hr style="height:1px;margin:0px;padding:0px;border:none;color:#111;background-color:#111;" /> """,
                                    unsafe_allow_html=True,
                                )

                            except Exception as err:
                                pass

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
                        <p align='justify'>Healthy vegetarian meal structured to provide a daily intake of approx 1800 calories, divided across four meals!!</p>
                        """,
                        unsafe_allow_html=True,
                    )

                    st.button(
                        "🥗 Download My Meal Plan",
                        use_container_width=True,
                        type="secondary",
                        key="_button_meal_plan",
                    )

                with st.container(border=True, height=189):
                    st.markdown(
                        "<H5>Exercise Routine</H5>",
                        unsafe_allow_html=True,
                    )

                    st.markdown(
                        """
                        <p align='justify'>Exclusive exercise routines, designed to complement your overall fitness.</p>
                        """,
                        unsafe_allow_html=True,
                    )

                    st.button(
                        "🏄‍♂️ Download Exercise Routine",
                        use_container_width=True,
                        key="_button_exercise_routine",
                    )

            bottom_ribbon_col_1, bottom_ribbon_col_2 = st.columns(
                [
                    4.75,
                    1,
                ]
            )
            st.markdown(
                """
                <style>
                a {
                    color: #FFFFFF;
                    text-decoration: none;
                }
                a:hover {
                    color: #FFC0CB;
                }
                </style>
                """,
                unsafe_allow_html=True,
            )

            with bottom_ribbon_col_1:
                st.markdown("<H4>Educational Resources</H4>", unsafe_allow_html=True)

            with st.container(border=True):
                cola, colb, colc = st.columns(3)

                with colb:
                    st.image(
                        Image.open(
                            "assets/application/educational_content_headers/blog_banner_3.jpg"
                        ),
                        use_column_width=True,
                    )
                    st.markdown(
                        "<H6><A HREF='https://medium.com/world-of-opportunity/its-time-for-action-period-298d8a353afc'>It's time for the action. Period</A></H6><P align='justify'>Leading philanthropists and companies call for increased action and investme...</P>",
                        unsafe_allow_html=True,
                    )

                with cola:
                    st.image(
                        Image.open(
                            "assets/application/educational_content_headers/blog_banner_2.jpg"
                        ),
                        use_column_width=True,
                    )
                    st.markdown(
                        "<H6><A HREF='https://thecaseforher.medium.com/introducing-a-new-definition-of-menstrual-health-bfd63aea12dc'>New definition of menstrual health</A></H6><P align='justify'>Global team of experts organized by the Global Menstrual Collective, has come...</P>",
                        unsafe_allow_html=True,
                    )

                with colc:
                    st.image(
                        Image.open(
                            "assets/application/educational_content_headers/blog_banner_1.jpg"
                        ),
                        use_column_width=True,
                    )
                    st.markdown(
                        "<H6><A HREF='https://medium.com/usaid-2030/dignified-menstruation-in-the-workplace-fe19afab97b2'>Dignified Menstruation at Work</A></H6><P align='justify'>Many people who menstruate every month cannot afford to buy a tampon...</P>",
                        unsafe_allow_html=True,
                    )

        elif selected_menu_item == "Flo Community":
            with st.sidebar:
                with st.container(height=325, border=False):
                    st.success(
                        "Stay hydrated and incorporate light exercises to reduce bloating & ease premenstrual symptoms.",
                        icon=":material/thread_unread:",
                    )

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

            ribbon_col_1, ribbon_col_2, ribbon_col_3 = st.columns([4.6, 1, 0.4])

            with ribbon_col_1:
                st.markdown("<H4>Flo Community</H4>", unsafe_allow_html=True)

            with ribbon_col_2:
                if st.button("🛍️ Marketplace", use_container_width=True):
                    st.switch_page("pages/marketplace.py")

            with ribbon_col_3:
                if st.button("🔔", use_container_width=True):
                    display_latest_notification()

            st.write(" ")

            mid_ribbon_col_1, mid_ribbon_col_2 = st.columns(
                [
                    2,
                    1,
                ]
            )

            with mid_ribbon_col_1:
                with st.expander("📝 Create and Share your Post", expanded=False):
                    with st.form("_create_post", border=False, clear_on_submit=True):
                        input_content = st.text_area(
                            "Type your post here",
                            placeholder="What's on your mind?",
                            label_visibility="collapsed",
                        )

                        uploaded_file = st.file_uploader(
                            "Attachment",
                            type=["png", "jpg"],
                            accept_multiple_files=False,
                            label_visibility="collapsed",
                        )

                        col_button, _, _ = st.columns([1.5, 1, 1])
                        with col_button:
                            button_publish_post = st.form_submit_button(
                                "Share my Post",
                                use_container_width=True,
                                type="primary",
                            )

                        if button_publish_post:
                            if uploaded_file is not None:
                                uploaded_filename = uploaded_file.name

                                image_file_path = os.path.join(
                                    "assets/application/community_posts",
                                    uploaded_filename,
                                )

                                with open(image_file_path, "wb") as f:
                                    f.write(uploaded_file.getbuffer())

                            else:
                                image_file_path = ""

                            postsdb = PostsDB()
                            postsdb.add_post(
                                logged_in_username, input_content, image_file_path
                            )

                            st.success(
                                "Your post has been successfully published.", icon="✔️"
                            )
                            time.sleep(5)
                            st.rerun()

            with mid_ribbon_col_2:
                with st.container(border=True):
                    st.markdown("<H6>🔥 Hot Topics</H6>", unsafe_allow_html=True)

                    trending_topics = [
                        "Managing Pain Naturally",
                        "Diet and Period Health",
                        "Eco-Friendly Solutions",
                        "Myths About Periods",
                        "Period Health Awareness",
                    ]

                    trending_topic_descriptions = [
                        "Natural periods remedies",
                        "Foods for better periods",
                        "Unending health options",
                        "Debunking period myths",
                        "Promoting periods health",
                    ]

                    icon_paths = [
                        "assets/app_graphics/comm_red.png",
                        "assets/app_graphics/comm_blue.png",
                        "assets/app_graphics/comm_yellow.png",
                        "assets/app_graphics/comm_green.png",
                        "assets/app_graphics/comm_purple.png",
                    ]

                    for topic_index in range(len(trending_topics)):
                        col1, col2 = st.columns([1, 3])
                        with col1:
                            st.image(
                                Image.open(icon_paths[topic_index]).resize((50, 50))
                            )
                        with col2:
                            st.markdown(
                                f"<B>{trending_topics[topic_index]}</B><BR>{trending_topic_descriptions[topic_index]}",
                                unsafe_allow_html=True,
                            )

                with st.container(border=True):
                    st.markdown("<H6>Sponsored</H6>", unsafe_allow_html=True)

                    col1, col2 = st.columns([1, 3])

                    with col1:
                        st.image(
                            Image.open("assets/app_graphics/sponsored_1.png").resize(
                                (50, 50)
                            )
                        )

                    with col2:
                        st.markdown(
                            f"<B>Organic Period Products</B><BR>Economical, Safe, Reliable",
                            unsafe_allow_html=True,
                        )
                        st.image(
                            Image.open("assets/app_graphics/adverts_1.jpg"),
                            use_column_width=True,
                        )

                with st.container(border=True):
                    st.markdown("<H6>🚀 Top Creators</H6>", unsafe_allow_html=True)

                    postsdb = PostsDB()
                    top_creators = postsdb.get_top_five_creators()

                    for creator in top_creators:
                        col1, col2 = st.columns([1, 3])
                        with col1:
                            st.image(
                                Image.open("assets/application/smiley_icon.png").resize(
                                    (50, 50)
                                )
                            )
                        with col2:
                            st.markdown(
                                f"<B>@{creator[0]}</B><BR>Shared {creator[1]} Posts recently",
                                unsafe_allow_html=True,
                            )

                with st.container(border=True):
                    st.markdown("<H6>Sponsored</H6>", unsafe_allow_html=True)

                    col1, col2 = st.columns([1, 3])

                    with col1:
                        st.image(
                            Image.open("assets/app_graphics/sponsored_2.png").resize(
                                (50, 50)
                            )
                        )

                    with col2:
                        st.markdown(
                            f"<B>Organic Cotton Pads</B><BR>Gentle, Eco-Friendly Pads",
                            unsafe_allow_html=True,
                        )
                        st.image(
                            Image.open("assets/app_graphics/adverts_2.jpg"),
                            use_column_width=True,
                        )

            postsdb = PostsDB()

            posts_per_page = 5
            total_posts_count = postsdb.get_number_of_pages(
                posts_per_page=posts_per_page
            )

            with mid_ribbon_col_1:
                community_posts_container = st.container(border=False)
                st.write(" ")
                page_number = sac.pagination(
                    total=total_posts_count,
                    page_size=posts_per_page,
                    align="center",
                    variant="light",
                    jump=True,
                    show_total=True,
                )

            community_post = postsdb.get_posts_for_given_range(
                page_number, posts_per_page
            )

            with community_posts_container:
                try:
                    community_post_1 = community_post[0]

                    with st.container(border=True):
                        col1, col2 = st.columns([1, 9])

                        userdb = UserDB()
                        (
                            _,
                            author_name,
                            _,
                            _,
                            _,
                            _,
                            _,
                            author_img_url,
                            _,
                            _,
                            _,
                            _,
                            _,
                        ) = userdb.get_user(community_post_1[1])

                        with col1:
                            st.image(
                                Image.open(
                                    f"assets/application/smiley_icon.png"
                                ).resize((33, 33)),
                                use_column_width=True,
                            )
                        with col2:
                            st.markdown(
                                f"<B>{author_name}</B><BR>{community_post_1[2]}",
                                unsafe_allow_html=True,
                            )

                        st.markdown(community_post_1[3])

                        try:
                            st.image(
                                Image.open(community_post_1[4]),
                                use_column_width=True,
                            )
                        except:
                            pass

                        cola, colb, colc, _, _, _, colx = st.columns(
                            [1, 1, 1, 1, 1, 1, 4]
                        )
                        postsdb = PostsDB()

                        with cola:
                            if st.button(
                                "👍",
                                use_container_width=True,
                                key=f"_like_button_{community_post_1[0]}",
                            ):
                                postsdb.increment_likes(community_post_1[0])

                        with colb:
                            if st.button(
                                "👎",
                                use_container_width=True,
                                key=f"_save_button_{community_post_1[0]}",
                            ):
                                postsdb.increment_dislikes(community_post_1[0])

                        with colx:
                            if st.button(
                                "⚠️ Report this Post",
                                use_container_width=True,
                                key=f"_report_post_button_{community_post_1[0]}",
                            ):
                                postsdb.increment_reports(community_post_1[0])

                except Exception as err:
                    pass

            with community_posts_container:
                try:
                    community_post_2 = community_post[1]

                    with st.container(border=True):
                        col1, col2 = st.columns([1, 9])

                        userdb = UserDB()
                        (
                            _,
                            author_name,
                            _,
                            _,
                            _,
                            _,
                            _,
                            author_img_url,
                            _,
                            _,
                            _,
                            _,
                            _,
                        ) = userdb.get_user(community_post_2[1])

                        with col1:
                            st.image(
                                Image.open(
                                    f"assets/application/smiley_icon.png"
                                ).resize((33, 33)),
                                use_column_width=True,
                            )
                        with col2:
                            st.markdown(
                                f"<B>{author_name}</B><BR>{community_post_2[2]}",
                                unsafe_allow_html=True,
                            )

                        st.markdown(community_post_2[3])

                        try:
                            st.image(
                                Image.open(community_post_2[4]),
                                use_column_width=True,
                            )
                        except:
                            pass

                        cola, colb, colc, _, _, _, colx = st.columns(
                            [1, 1, 1, 1, 1, 1, 4]
                        )
                        postsdb = PostsDB()

                        with cola:
                            if st.button(
                                "👍",
                                use_container_width=True,
                                key=f"_like_button_{community_post_2[0]}",
                            ):
                                postsdb.increment_likes(community_post_2[0])

                        with colb:
                            if st.button(
                                "👎",
                                use_container_width=True,
                                key=f"_save_button_{community_post_2[0]}",
                            ):
                                postsdb.increment_dislikes(community_post_2[0])

                        with colx:
                            if st.button(
                                "⚠️ Report this Post",
                                use_container_width=True,
                                key=f"_report_post_button_{community_post_2[0]}",
                            ):
                                postsdb.increment_reports(community_post_2[0])

                except Exception as err:
                    pass

            with community_posts_container:
                try:
                    community_post_3 = community_post[2]

                    with st.container(border=True):
                        col1, col2 = st.columns([1, 9])

                        userdb = UserDB()
                        (
                            _,
                            author_name,
                            _,
                            _,
                            _,
                            _,
                            _,
                            author_img_url,
                            _,
                            _,
                            _,
                            _,
                            _,
                        ) = userdb.get_user(community_post_3[1])

                        with col1:
                            st.image(
                                Image.open(
                                    f"assets/application/smiley_icon.png"
                                ).resize((33, 33)),
                                use_column_width=True,
                            )
                        with col2:
                            st.markdown(
                                f"<B>{author_name}</B><BR>{community_post_3[2]}",
                                unsafe_allow_html=True,
                            )

                        st.markdown(community_post_3[3])

                        try:
                            st.image(
                                Image.open(community_post_3[4]),
                                use_column_width=True,
                            )
                        except:
                            pass

                        cola, colb, colc, _, _, _, colx = st.columns(
                            [1, 1, 1, 1, 1, 1, 4]
                        )
                        postsdb = PostsDB()

                        with cola:
                            if st.button(
                                "👍",
                                use_container_width=True,
                                key=f"_like_button_{community_post_3[0]}",
                            ):
                                postsdb.increment_likes(community_post_3[0])

                        with colb:
                            if st.button(
                                "👎",
                                use_container_width=True,
                                key=f"_save_button_{community_post_3[0]}",
                            ):
                                postsdb.increment_dislikes(community_post_3[0])

                        with colx:
                            if st.button(
                                "⚠️ Report this Post",
                                use_container_width=True,
                                key=f"_report_post_button_{community_post_3[0]}",
                            ):
                                postsdb.increment_reports(community_post_3[0])

                except Exception as err:
                    pass

            with community_posts_container:
                try:
                    community_post_4 = community_post[3]

                    with st.container(border=True):
                        col1, col2 = st.columns([1, 9])

                        userdb = UserDB()
                        (
                            _,
                            author_name,
                            _,
                            _,
                            _,
                            _,
                            _,
                            author_img_url,
                            _,
                            _,
                            _,
                            _,
                            _,
                        ) = userdb.get_user(community_post_4[1])

                        with col1:
                            st.image(
                                Image.open(
                                    f"assets/application/smiley_icon.png"
                                ).resize((33, 33)),
                                use_column_width=True,
                            )
                        with col2:
                            st.markdown(
                                f"<B>{author_name}</B><BR>{community_post_4[2]}",
                                unsafe_allow_html=True,
                            )

                        st.markdown(community_post_4[3])

                        try:
                            st.image(
                                Image.open(community_post_4[4]),
                                use_column_width=True,
                            )
                        except:
                            pass

                        cola, colb, colc, _, _, _, colx = st.columns(
                            [1, 1, 1, 1, 1, 1, 4]
                        )
                        postsdb = PostsDB()

                        with cola:
                            if st.button(
                                "👍",
                                use_container_width=True,
                                key=f"_like_button_{community_post_4[0]}",
                            ):
                                postsdb.increment_likes(community_post_4[0])

                        with colb:
                            if st.button(
                                "👎",
                                use_container_width=True,
                                key=f"_save_button_{community_post_4[0]}",
                            ):
                                postsdb.increment_dislikes(community_post_4[0])

                        with colx:
                            if st.button(
                                "⚠️ Report this Post",
                                use_container_width=True,
                                key=f"_report_post_button_{community_post_4[0]}",
                            ):
                                postsdb.increment_reports(community_post_4[0])

                except Exception as err:
                    pass

            with community_posts_container:
                try:
                    community_post_5 = community_post[4]

                    with st.container(border=True):
                        col1, col2 = st.columns([1, 9])

                        userdb = UserDB()
                        (
                            _,
                            author_name,
                            _,
                            _,
                            _,
                            _,
                            _,
                            author_img_url,
                            _,
                            _,
                            _,
                            _,
                            _,
                        ) = userdb.get_user(community_post_5[1])

                        with col1:
                            st.image(
                                Image.open(
                                    f"assets/application/smiley_icon.png"
                                ).resize((33, 33)),
                                use_column_width=True,
                            )
                        with col2:
                            st.markdown(
                                f"<B>{author_name}</B><BR>{community_post_5[2]}",
                                unsafe_allow_html=True,
                            )

                        st.markdown(community_post_5[3])

                        try:
                            st.image(
                                Image.open(community_post_5[4]),
                                use_column_width=True,
                            )
                        except:
                            pass

                        cola, colb, colc, _, _, _, colx = st.columns(
                            [1, 1, 1, 1, 1, 1, 4]
                        )
                        postsdb = PostsDB()

                        with cola:
                            if st.button(
                                "👍",
                                use_container_width=True,
                                key=f"_like_button_{community_post_5[0]}",
                            ):
                                postsdb.increment_likes(community_post_5[0])

                        with colb:
                            if st.button(
                                "👎",
                                use_container_width=True,
                                key=f"_save_button_{community_post_5[0]}",
                            ):
                                postsdb.increment_dislikes(community_post_5[0])

                        with colx:
                            if st.button(
                                "⚠️ Report this Post",
                                use_container_width=True,
                                key=f"_report_post_button_{community_post_5[0]}",
                            ):
                                postsdb.increment_reports(community_post_5[0])

                except Exception as err:
                    pass

        elif selected_menu_item == "Chat with FloAI":
            with st.sidebar:
                with st.container(height=325, border=False):
                    st.warning(
                        "**⚠️ Our chatbots are experimental!** It may display inaccurate info. Kindly double-check, for response accuracy."
                    )

                if st.button("My Profile", use_container_width=True):
                    st.switch_page("pages/user_profile.py")

            st.write(" ")

            ribbon_col_1, ribbon_col_2, ribbon_col_3 = st.columns([4.6, 1, 0.4])

            with ribbon_col_1:
                st.markdown("<H4>Chat with Agent</H4>", unsafe_allow_html=True)

            with ribbon_col_2:
                if st.button("🛍️ Marketplace", use_container_width=True):
                    st.switch_page("pages/marketplace.py")

            with ribbon_col_3:
                if st.button("🔔", use_container_width=True):
                    display_latest_notification()

            st.write(" ")

            genai.configure(api_key=str(credentials.GEMINI_API_KEY))

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

                model = genai.GenerativeModel(model_name="gemini-pro")
                chat = model.start_chat()

                response_from_model = chat.send_message(
                    "You are a highly qualified menstrual health expert. Under 75 words, answer this user query:\n\nQuestion: "
                    + prompt,
                    stream=True,
                )

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
                        response = st.markdown("Sorry, I am unable to answer this.")

                st.session_state.messages.append(
                    {"role": "assistant", "content": response}
                )

    else:
        with st.sidebar:
            selected_menu_item = sac.menu(
                [
                    sac.MenuItem(
                        "Welcome to Flo",
                        icon="grid",
                    ),
                    sac.MenuItem(
                        "More About Flo",
                        icon="grid",
                    ),
                    sac.MenuItem(" ", disabled=True),
                    sac.MenuItem(type="divider"),
                ],
                open_all=True,
            )

            with st.expander("LogIn to your Flo account", expanded=True):
                username = st.text_input(
                    "Username", placeholder="Username", label_visibility="collapsed"
                )
                password = st.text_input(
                    "Password",
                    placeholder="Password",
                    type="password",
                    label_visibility="collapsed",
                )

                if st.button("LogIn to Flo", use_container_width=True):
                    credsdb = CredentialsDB()
                    is_verified = credsdb.verify_user(username, password)

                    if is_verified:
                        st.session_state.user_authentication_status = True
                        st.session_state.logged_in_username = username
                        st.rerun()

                    else:
                        st.warning("Incorrect LogIn Credentials", icon="⚠️")
                        time.sleep(3)
                        st.rerun()

        st.markdown("<BR>", unsafe_allow_html=True)
        st.markdown("<H2>Welcome to Flo</H2>", unsafe_allow_html=True)

        st.markdown(
            "Lorem ipsum dolor mit abeit ul adbar beden jam grainger loddol orem ipsum dolor mit abeit ul adbar beden jam grainger lod orem ipsum dolor mit abeit ul adbar beden jam grainger lod orem ipsum dolor mit abeit ul adbar beden jam grainger lod orem ipsum dol",
            unsafe_allow_html=True,
        )
        st.write(" ")

        with st.expander("Register Now to Create an Account", expanded=True):
            st.write(" ")

            registration_step = sac.steps(
                items=[
                    sac.StepsItem(title="Basic Details"),
                    sac.StepsItem(title="More About You"),
                    sac.StepsItem(title="Medical Details"),
                    sac.StepsItem(title="Account Setup"),
                ],
            )

            if registration_step == "Basic Details":
                cola, colb = st.columns(2)

                with cola:
                    if (
                        st.session_state.signup_full_name is None
                        or st.session_state.signup_full_name == ""
                    ):
                        st.session_state.signup_full_name = st.text_input(
                            "Full Name", placeholder="Enter your full name"
                        )
                    else:
                        st.session_state.signup_full_name = st.text_input(
                            "Full Name",
                            placeholder="Enter your full name",
                            value=st.session_state.signup_full_name,
                        )

                with colb:
                    st.session_state.signup_dob = st.date_input(
                        "Date of Birth",
                        datetime.datetime.today(),
                        min_value=datetime.datetime.strptime("1950-01-01", "%Y-%m-%d"),
                    )

                cola, colb, colc = st.columns(3)

                with cola:
                    if (
                        st.session_state.signup_height is None
                        or st.session_state.signup_height == ""
                    ):
                        st.session_state.signup_height = st.text_input(
                            "Height (in cm)", placeholder="Enter your height (in cm)"
                        )
                    else:
                        st.session_state.signup_height = st.text_input(
                            "Height (in cm)",
                            placeholder="Enter your height (in cm)",
                            value=st.session_state.signup_height,
                        )

                with colb:
                    if (
                        st.session_state.signup_weight is None
                        or st.session_state.signup_weight == ""
                    ):
                        st.session_state.signup_weight = st.text_input(
                            "Weight (in kg)", placeholder="Enter your weight (in kg)"
                        )
                    else:
                        st.session_state.signup_weight = st.text_input(
                            "Weight (in kg)",
                            placeholder="Enter your weight (in kg)",
                            value=st.session_state.signup_weight,
                        )

                with colc:
                    list_dietary_preferences = [
                        "Vegetarian",
                        "Non-Vegetarian",
                        "Ovo-Vegetarian (Eggs Only)",
                    ]

                    if (
                        st.session_state.signup_dietary_preferences is None
                        or st.session_state.signup_dietary_preferences == ""
                    ):
                        st.session_state.signup_dietary_preferences = st.selectbox(
                            "Dietary Preferences",
                            list_dietary_preferences,
                            placeholder="Select your Dietary Preferences",
                            index=None,
                        )
                    else:
                        st.session_state.signup_dietary_preferences = st.selectbox(
                            "Dietary Preferences",
                            list_dietary_preferences,
                            placeholder="Select your Dietary Preferences",
                            index=list_dietary_preferences.index(
                                st.session_state.signup_dietary_preferences
                            ),
                        )

            if registration_step == "More About You":
                cola, colb = st.columns(2)

                with cola:
                    if (
                        st.session_state.signup_address is None
                        or st.session_state.signup_address == ""
                    ):
                        st.session_state.signup_address = st.text_area(
                            "Registered Address",
                            placeholder="Enter your present address with pin code",
                            height=161,
                        )
                    else:
                        st.session_state.signup_address = st.text_area(
                            "Registered Address",
                            placeholder="Enter your present address with pin code",
                            height=161,
                            value=st.session_state.signup_address,
                        )

                with colb:
                    if (
                        st.session_state.signup_phone_no is None
                        or st.session_state.signup_phone_no == ""
                    ):
                        st.session_state.signup_phone_no = st.text_input(
                            "Phone Number", placeholder="Enter your phone no."
                        )
                    else:
                        st.session_state.signup_phone_no = st.text_input(
                            "Phone No.",
                            placeholder="Enter your phone no.",
                            value=st.session_state.signup_phone_no,
                        )

                    st.session_state.signup_uploaded_profile_pic = st.file_uploader(
                        "Profile Picture (Optional)", accept_multiple_files=False
                    )
                    st.write(" ")

            if registration_step == "Medical Details":
                cola, colb = st.columns(2)

                with cola:
                    list_allergies = allergies = [
                        "Peanuts",
                        "Tree Nuts",
                        "Shellfish",
                        "Fish",
                        "Eggs",
                        "Milk",
                        "Wheat",
                        "Soy",
                        "Gluten",
                        "Pollen",
                    ]

                    if (
                        st.session_state.signup_allergies is None
                        or st.session_state.signup_allergies == ""
                    ):
                        st.session_state.signup_allergies = st.multiselect(
                            "Allergies (Optional)",
                            list_allergies,
                            placeholder="Select allergies you have",
                        )
                    else:
                        st.session_state.signup_allergies = st.multiselect(
                            "Allergies (Optional)",
                            list_allergies,
                            placeholder="Select allergies you have",
                            default=st.session_state.signup_allergies,
                        )

                with colb:
                    list_medical_conditions = [
                        "Diabetes",
                        "Hypertension",
                        "Asthma",
                        "Heart Disease",
                        "Thyroid Disorders",
                        "PCOS (Polycystic Ovary Syndrome)",
                        "Endometriosis",
                        "Migraines",
                        "Anemia",
                        "Osteoporosis",
                    ]

                    if (
                        st.session_state.signup_medical_conditions is None
                        or st.session_state.signup_medical_conditions == ""
                    ):
                        st.session_state.signup_medical_conditions = st.multiselect(
                            "Medical Conditions (Optional)",
                            list_medical_conditions,
                            placeholder="Select any medical condition you have",
                        )
                    else:
                        st.session_state.signup_medical_conditions = st.multiselect(
                            "Medical Conditions (Optional)",
                            list_medical_conditions,
                            placeholder="Select any medical condition you have",
                            default=st.session_state.signup_medical_conditions,
                        )

                with cola:
                    if (
                        st.session_state.signup_cycle_length is None
                        or st.session_state.signup_cycle_length == ""
                    ):
                        st.session_state.signup_cycle_length = st.number_input(
                            "Enter your average Cycle Length",
                            placeholder="Average Cycle Length",
                            value=28,
                            min_value=20,
                            max_value=35,
                        )
                    else:
                        st.session_state.signup_cycle_length = st.number_input(
                            "Enter your average Cycle Length",
                            placeholder="Average Cycle Length",
                            value=st.session_state.signup_cycle_length,
                            min_value=20,
                            max_value=35,
                        )

                with colb:
                    if (
                        st.session_state.signup_periods_length is None
                        or st.session_state.signup_periods_length == ""
                    ):
                        st.session_state.signup_periods_length = st.number_input(
                            "Enter your average Period Length",
                            placeholder="Average Period Length",
                            value=4,
                            min_value=2,
                            max_value=7,
                        )
                    else:
                        st.session_state.signup_periods_length = st.number_input(
                            "Enter your average Period Length",
                            placeholder="Average Period Length",
                            value=st.session_state.signup_periods_length,
                            min_value=2,
                            max_value=7,
                        )

            if registration_step == "Account Setup":
                cola, colb = st.columns(2)

                with cola:
                    username = st.text_input(
                        "Username", placeholder="Enter your username"
                    )
                with colb:
                    password = st.text_input(
                        "Password", placeholder="Enter your password", type="password"
                    )

                checkbox_terms_and_conditions = sac.checkbox(
                    items=[
                        "By continuing, you agree to our community guidelines and terms of use. Read more here.",
                    ],
                    return_index=True,
                )

                if st.button("Create New Account"):
                    if len(checkbox_terms_and_conditions) > 0:
                        if (
                            (username is not None)
                            and (password is not None)
                            and (len(username) > 3)
                            and (len(password) > 7)
                            and (" " not in username)
                            and (" " not in password)
                        ):
                            if (
                                (st.session_state.signup_full_name is not None)
                                and (st.session_state.signup_full_name != "")
                                and (st.session_state.signup_height is not None)
                                and (st.session_state.signup_height != "")
                                and (st.session_state.signup_height.isdigit())
                                and (st.session_state.signup_weight is not None)
                                and (st.session_state.signup_weight != "")
                                and st.session_state.signup_weight.isdigit()
                                and (
                                    st.session_state.signup_dietary_preferences
                                    is not None
                                )
                            ):
                                if (
                                    (st.session_state.signup_address is not None)
                                    and (st.session_state.signup_address != "")
                                    and (st.session_state.signup_phone_no is not None)
                                    and (st.session_state.signup_phone_no != "")
                                    and (len(st.session_state.signup_phone_no) >= 10)
                                    and (len(st.session_state.signup_phone_no) <= 13)
                                ):
                                    try:
                                        if (
                                            st.session_state.signup_uploaded_profile_pic
                                            == None
                                        ):
                                            profile_pic_url = (
                                                "assets/user_profile/sample.png"
                                            )

                                        else:
                                            try:
                                                uploaded_filename = (
                                                    new_file_uploaded.name
                                                )
                                                profile_pic_url = os.path.join(
                                                    "assets/user_profile",
                                                    uploaded_filename,
                                                )

                                                with open(profile_pic_url, "wb") as f:
                                                    f.write(
                                                        new_file_uploaded.getbuffer()
                                                    )

                                            except:
                                                profile_pic_url = (
                                                    "assets/user_profile/sample.png"
                                                )

                                        if (
                                            st.session_state.signup_allergies
                                            is not None
                                        ):
                                            st.session_state.signup_allergies = (
                                                ", ".join(
                                                    st.session_state.signup_allergies
                                                )
                                            )

                                        if (
                                            st.session_state.signup_medical_conditions
                                            is not None
                                        ):
                                            st.session_state.signup_medical_conditions = ", ".join(
                                                st.session_state.signup_medical_conditions
                                            )

                                        userdb = UserDB()
                                        userdb.add_user(
                                            username,
                                            st.session_state.signup_full_name,
                                            st.session_state.signup_dob,
                                            st.session_state.signup_height,
                                            st.session_state.signup_weight,
                                            st.session_state.signup_phone_no,
                                            st.session_state.signup_address,
                                            profile_pic_url,
                                            st.session_state.signup_dietary_preferences,
                                            st.session_state.signup_allergies,
                                            st.session_state.signup_medical_conditions,
                                            st.session_state.signup_cycle_length,
                                            st.session_state.signup_periods_length,
                                        )

                                        credsdb = CredentialsDB()
                                        credsdb.add_credentials(username, password)

                                        st.success(
                                            "Your account has been created successfully",
                                            icon="✔️",
                                        )
                                        time.sleep(2)

                                        st.toast("LogIn with your new credentials")
                                        time.sleep(3)

                                        st.session_state.signup_periods_length = None
                                        st.session_state.signup_cycle_length = None
                                        st.session_state.signup_medical_conditions = []
                                        st.session_state.signup_allergies = []
                                        st.session_state.signup_phone_no = None
                                        st.session_state.signup_profile_pic = None
                                        st.session_state.signup_address = None
                                        st.session_state.signup_dietary_preferences = (
                                            None
                                        )
                                        st.session_state.signup_weight = None
                                        st.session_state.signup_height = None
                                        st.session_state.signup_dob = None
                                        st.session_state.signup_full_name = None
                                        st.session_state.signup_uploaded_profile_pic = (
                                            None
                                        )

                                        st.rerun()

                                    except Exception as err:
                                        st.error(err, icon="🚨")

                                else:
                                    display_warning = st.warning(
                                        "Kindly check your entries for Step 2: More About You",
                                        icon="⚠️",
                                    )
                                    time.sleep(2)
                                    display_warning.empty()
                            else:
                                display_warning = st.warning(
                                    "Kindly check your entries for Step 1: Basic Details",
                                    icon="⚠️",
                                )
                                time.sleep(2)
                                display_warning.empty()
                        else:
                            display_warning = st.warning(
                                "Kindly double check your username and password",
                                icon="⚠️",
                            )
                            time.sleep(2)
                            display_warning.empty()
                    else:
                        display_warning = st.warning(
                            "Please agree to the terms and conditions", icon="⚠️"
                        )
                        time.sleep(2)
                        display_warning.empty()

        st.markdown("<BR>Read about Menstrual Health here →", unsafe_allow_html=True)
