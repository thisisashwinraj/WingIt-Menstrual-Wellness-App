import time
import datetime
import numpy as np
import pandas as pd
from PIL import Image
import google.generativeai as genai

import streamlit as st
import streamlit_antd_components as sac

from backend.database import UserDB, CyclesDB, PeriodsDB, SymptomsDB


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

@st.experimental_dialog("Edit Cycle Details")
def edit_periods_details(start_date, end_date, flow_intensity, notes):
    with st.form("_edit_period_details_form", clear_on_submit=False, border=True):
        st.markdown("<H4>Edit Periods Details</H4>", unsafe_allow_html=True)

        colx, coly = st.columns(2)

        with colx:
            start_date = st.date_input("Start Date", datetime.datetime.strptime(start_date, '%Y-%m-%d'), disabled=True)
        with coly:
            new_end_date = st.date_input("End Date", datetime.datetime.strptime(end_date, '%Y-%m-%d'))
                
        flow_intensity_list = ['Light', 'Medium', 'Heavy']
        flow_intensity_pre_selected_option = flow_intensity_list.index(flow_intensity)

        new_flow_intensity = st.selectbox("Flow Intensity", flow_intensity_list, index=flow_intensity_pre_selected_option)
        new_notes = st.text_area("Observations", value=notes)

        colb3, colb4 = st.columns([1, 1.75])
        with colb3:
            save_changes_button = st.form_submit_button("💾 Save Changes", use_container_width=True)

        if save_changes_button:
            periodsdb = PeriodsDB()
            periodsdb.edit_period(logged_in_username, start_date, end_date=new_end_date, flow_intensity=new_flow_intensity, notes=new_notes)

            st.success("Your changes have been saved successfully!", icon="✔️")
            time.sleep(5)
            st.rerun()

        with colb4:
            if st.form_submit_button("❌"):
                st.rerun()


@st.experimental_dialog("Edit Cycle Details")
def edit_cycle_details(start_date, end_date):
    st.markdown(f"Editing details for the menstrual cycle starting on {datetime.datetime.strptime(start_date, '%Y-%m-%d').strftime('%B %d')}", unsafe_allow_html=True)

    with st.container(border=True):
        colx, coly = st.columns(2)

        with colx:
            new_start_date = st.date_input("Start Date", datetime.datetime.strptime(start_date, '%Y-%m-%d'), disabled=True)
        with coly:
            new_end_date = st.date_input("End Date", datetime.datetime.strptime(end_date, '%Y-%m-%d'))
        
        calculated_cycle_length = (new_end_date - new_start_date).days + 1
        new_cycle_length = st.text_input("Cycle Length", value=str(calculated_cycle_length), disabled=True)

        colb1, colb2 = st.columns([1, 1.75])

        with colb1:
            save_changes_button = st.button("💾 Save Changes", use_container_width=True)
        
        if save_changes_button:
            cyclesdb = CyclesDB()
            cyclesdb.edit_cycle(logged_in_username, start_date, end_date=new_end_date, cycle_length=new_cycle_length)
                
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
        st.markdown(f"<H4>{datetime.datetime.strptime(start_date, '%Y-%m-%d').strftime('%b %d')} to {datetime.datetime.strptime(end_date, '%Y-%m-%d').strftime('%b %d, %Y')}</H4>You logged a complete menstrual cycle of {cycle_length} days", unsafe_allow_html=True)
        st.markdown("<BR>", unsafe_allow_html=True)

    selected_tab = sac.tabs([
        sac.TabsItem(label='Periods Details'),
        sac.TabsItem(label='Logged Symptoms'),
    ], variant='outline')


    if selected_tab == 'Periods Details':
        cola, colb = st.columns([7, 1])

        periodsdb = PeriodsDB()
        _, _, periods_start_date, periods_end_date, flow_intensity, notes = periodsdb.get_period(logged_in_username, start_date)

        with cola:
            st.markdown(f"<H4>You had periods from {datetime.datetime.strptime(periods_start_date, '%Y-%m-%d').strftime('%b %d')} to {datetime.datetime.strptime(periods_end_date, '%Y-%m-%d').strftime('%b %d, %Y')}</H4><B>• Intensity:</B> {flow_intensity}<BR><B>• Notes Logged by User:</B> {notes}<BR><BR>", unsafe_allow_html=True)            

    else:
        symptomsdb = SymptomsDB()
        symptoms_logged_between_two_dates = symptomsdb.get_symptoms_between_two_dates(logged_in_username, start_date, end_date)

        if len(symptoms_logged_between_two_dates) >= 1:
            for symptom in symptoms_logged_between_two_dates:
                st.markdown(f"<B>{datetime.datetime.strptime(symptom[2], '%Y-%m-%d').strftime('%B %d')}</B><BR> • Physical Symptoms: {symptom[3]} <BR> • Energy level: {symptom[4]} <BR> • Sleep Quality: {symptom[5]} <BR> • Emotional Symptoms: {symptom[6]}<BR>", unsafe_allow_html=True)
        
        else:
            sac.result(
                label="No Symptoms logged",
                description="Help us keep track of your health by logging your symptoms",
                status="empty",
            )


@st.experimental_dialog("Log Symptoms")
def log_symptoms_popup():
    ist_date = datetime.datetime.utcnow() + datetime.timedelta(hours=5, minutes=30)
    logged_date = st.date_input("Date of First Period", ist_date.date())

    physical_symptoms_list = ['Cramps', 'Headache', 'Bloating', 'Breast Tenderness', 'Fatigue', 'Back Pain', 'Acne', 'Nausea', 'Appetite Changes', 'Digestive Issues']
    logged_physical_symptoms = st.multiselect("Physical Symptoms", physical_symptoms_list, placeholder='Physical Symptoms', label_visibility='collapsed')

    cola, colb = st.columns(2)
    with cola:
        logged_energy_level = st.selectbox("Energy levels", ['High', 'Moderate', 'Low'], index=None, placeholder="Energy levels", label_visibility='collapsed')
    with colb:
        logged_sleep_quality = st.selectbox("Sleep quality", ['Good', 'Average', 'Poor'], index=None, placeholder="Sleep Quality", label_visibility='collapsed')

    emotional_symptoms_list = ['Mood Swings', 'Irritation', 'Anxiety', 'Depression', 'Stress']
    logged_emotional_symptoms = st.multiselect("Emotional Symptoms", emotional_symptoms_list, placeholder='Emotional Symptoms', label_visibility='collapsed')

    if st.button("Log my Symptoms"):
        logged_physical_symptoms = ", ".join(logged_physical_symptoms)
        logged_emotional_symptoms = ", ".join(logged_emotional_symptoms)

        symptomsdb = SymptomsDB()
        symptomsdb.add_symptoms(logged_in_username, logged_date, physical_symptoms=logged_physical_symptoms, energy_level=logged_energy_level, sleep_quality=logged_sleep_quality, emotional_symptoms=logged_emotional_symptoms)
        
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
        notes_first_period = st.text_area("Notes", placeholder="Additional comments or observation", label_visibility='collapsed')
        
        if st.button("Log Cycle Beginning"):
            userdb = UserDB()
            _, _, _, _, _, _, _, _, _, _, _, logged_in_users_avg_cycle_length, logged_in_users_avg_periods_length = userdb.get_user(logged_in_username)

            date_last_period = date_first_period + datetime.timedelta(days=logged_in_users_avg_periods_length)

            periodsdb = PeriodsDB()
            generated_periods_id = periodsdb.add_period(logged_in_username, date_first_period.strftime("%Y-%m-%d"), date_last_period.strftime("%Y-%m-%d"))
            
            date_last_cycle = date_first_period + datetime.timedelta(days=logged_in_users_avg_cycle_length)

            cyclesdb = CyclesDB()
            cyclesdb.add_cycle(date_first_period.strftime("%Y-%m-%d"), date_last_cycle.strftime("%Y-%m-%d"), generated_periods_id, logged_in_username)

            st.success("Your Cycle has been logged successfully", icon="✔️")
            time.sleep(5)
            st.rerun()

    elif tab_log_menstrual_cycle == "Periods End Reporting":       
        periodsdb = PeriodsDB()
        period1, period2, period3 = periodsdb.fetch_latest_periods(logged_in_username, 3)

        recently_logged_start_dates = [period1[2], period2[2], period3[2]]
        date_first_period = st.selectbox("Date of First Period", recently_logged_start_dates, index=None,)

        if date_first_period:
            cola, colb = st.columns(2)

            periodsdb = PeriodsDB()
            _, _, _, logged_end_date, logged_flow_intenity, logged_notes = periodsdb.get_period(logged_in_username, date_first_period)

            with cola:
                new_period_end_date = st.date_input("Date of Last Period", datetime.datetime.strptime(logged_end_date, '%Y-%m-%d'))
            with colb:
                flow_intensity_list = ['Light', 'Medium', 'Heavy']
                flow_intensity_pre_selected_option = flow_intensity_list.index(logged_flow_intenity)

                new_flow_intensity = st.selectbox("Flow Intensity", flow_intensity_list, index=flow_intensity_pre_selected_option)

            new_notes = st.text_area("Observations", value=logged_notes)
            
            if st.button("Log Periods Details"):
                periodsdb = PeriodsDB()
                periodsdb.edit_period(logged_in_username, date_first_period, end_date=new_period_end_date, flow_intensity=new_flow_intensity, notes=new_notes)
                    
                st.success("Changes saved successfully", icon="✔️")
                time.sleep(5)
                st.rerun()
 
        else:
            st.info("You can edit details of only the last three period cycles", icon='ℹ️')


if __name__ == "__main__":
    
    #####################################################
    logged_in_username = 'bhavnamukherjee'              #
    #####################################################

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
            sidebar_container = st.container(height=325, border=False)
            with sidebar_container:
                with st.expander("Analyze Symptoms", expanded=False):
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

        userdb = UserDB()
        _, logged_in_users_full_name, logged_in_users_dob, logged_in_users_height, logged_in_users_weight, _, _, logged_in_users_profile_pic_url, _, _, _, logged_in_users_avg_cycle_length, logged_in_users_avg_periods_length = userdb.get_user(logged_in_username)
        
        with ribbon_col_1:
            st.markdown(f"<H4>Hey, Hello {logged_in_users_full_name.split()[0]}</H4>", unsafe_allow_html=True)
        
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

            patient_details_container.image(
                logged_in_users_profile_pic_url, use_column_width=True
            )
            patient_details_container.markdown(
                f"""<H5 style="padding: 0px 0px;"><center>{logged_in_users_full_name}</H5></center>""", unsafe_allow_html=True
            )
            patient_details_container.markdown(
                f"""<center>Flo Username: {logged_in_username}</center>""", unsafe_allow_html=True
            )

            dob = datetime.datetime.strptime(logged_in_users_dob, "%Y-%m-%d")
            today = datetime.datetime.today()
            logged_in_users_age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

            total_inches = logged_in_users_height * 0.393701

            patient_details_container.markdown(
                f"<center>Age: {logged_in_users_age} • Height: {int(total_inches // 12)}'{int(total_inches % 12)}\" • Weight: {int(logged_in_users_weight)} kg</center>", unsafe_allow_html=True
            )
            patient_details_container.write(" ")
            with patient_details_container:
                if st.button("Log Menstrual Cycle", use_container_width=True):
                    log_menstrual_cycle_popup(logged_in_username)

        with dashboard_hero_section_2:
            dashboard_hero_section_2a, dashboard_hero_section_2b = st.columns([1, 1])

            # Homepage - Cycle Length Card
            with dashboard_hero_section_2a:
                bmi_details_container = st.container(border=True)
                bmi_details_container.image(
                    Image.open("assets/application/smiley_icon.png").resize((33, 33))
                )

                bmi_details_container.markdown(
                    f'<span class="custom-h6-bmi">Average Cycle Length:</span><BR><span class="custom-font-size-bmi"><B>{logged_in_users_avg_cycle_length}</span> Days</B> (Periods Length: {logged_in_users_avg_periods_length} days)',
                    unsafe_allow_html=True,
                )

            # Homepage - Fertility Score Card
            with dashboard_hero_section_2b:
                muac_details_container = st.container(border=True)

                muac_details_container.image(
                    Image.open("assets/application/smiley_icon.png").resize((33, 33))
                )

                cyclesdb = CyclesDB()
                _, start_date_str, end_date_str, cycle_length, _, _ = cyclesdb.fetch_latest_cycles(logged_in_username, 1)[0]
                
                start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").date()
                end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date()

                today = datetime.datetime.utcnow() + datetime.timedelta(hours=5, minutes=30)
                today = today.date()

                if today > end_date:
                    sidebar_container.warning("Please Log Your Menstrual Cycle", icon='⚠️')
                    muac_details_container.markdown(
                        f'<span class="custom-h6-bmi">Current Menstrual Phase:</span><BR><B><span class="custom-font-size-bmi">NA</span></B> (Your Last Cycle has Ended)',
                        unsafe_allow_html=True,
                    )

                else:
                    days_since_start  = (today - start_date).days + 1

                    if days_since_start <= logged_in_users_avg_periods_length + 1:
                        fertility = 'low'
                        sidebar_container.info("Low Chance of Pregnancy", icon='ℹ️')

                    elif (days_since_start > logged_in_users_avg_periods_length) and (days_since_start <= (logged_in_users_avg_cycle_length / 2 - 2)):
                        sidebar_container.info("Moderate Chance of Pregnancy", icon='ℹ️')
                    
                    elif (days_since_start > (logged_in_users_avg_cycle_length / 2 - 2)) and (days_since_start <= (logged_in_users_avg_cycle_length / 2 + 2)):
                        sidebar_container.info("High Chance of Pregnancy", icon='ℹ️')

                    elif (days_since_start > (logged_in_users_avg_cycle_length / 2 + 2)) and (days_since_start <= (logged_in_users_avg_cycle_length - logged_in_users_avg_periods_length)):
                        sidebar_container.info("Moderate Chance of Pregnancy", icon='ℹ️')
                    
                    else:
                        sidebar_container.info("Low Chance of Pregnancy", icon='ℹ️')


                    muac_details_container.markdown(
                        f'<span class="custom-h6-bmi">Current Menstrual Phase:</span><BR><span style="font-size: 20px;">#</span><B><span class="custom-font-size-bmi">{days_since_start }</span></B> (Cycle started on {start_date_str})',
                        unsafe_allow_html=True,
                    )

            with st.container(border=True, height=212):
                st.markdown(
                    "<H6>Cycle Lengths - Last 15 Cycles</H6>", unsafe_allow_html=True
                )

                cyclesdb = CyclesDB()
                last_10_cycles = cyclesdb.fetch_latest_cycles(logged_in_username, 15)
                cycle_lengths = []

                for cycle in last_10_cycles:
                    cycle_lengths.append([cycle[1], cycle[3]])

                df = pd.DataFrame(cycle_lengths, columns=['Start Date', 'Cycle Length'])
                df['Start Date'] = pd.to_datetime(df['Start Date'])
                df.set_index('Start Date', inplace=True)

                st.bar_chart(
                    df,
                    color="#FFC0CB",
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
            [2, 1.05]
        )

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
                    cycle_1_details, cycle_2_details, cycle_3_details, cycle_4_details = cyclesdb.fetch_latest_cycles(logged_in_username, 4)

                    # Cycle 1
                    cola, colb, colc, cold = st.columns([0.75, 3.4, 1.4, 0.6])
                    with cola:
                        all_icons = [
                            "assets/application/smiley_icon.png",
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
                            key="_button_cycle_1_details"
                        ):
                            display_cycle_details(cycle_1_details[1], cycle_1_details[2], cycle_1_details[3])

                    with cold:
                        if st.button("✏️", use_container_width=True, key="_button_cycle_1_details_edit"):
                            edit_cycle_details(cycle_1_details[1], cycle_1_details[2])

                    st.markdown(
                        """<hr style="height:1px;margin:0px;padding:0px;border:none;color:#111;background-color:#111;" /> """,
                        unsafe_allow_html=True,
                    )

                    # Cycle 2
                    cola, colb, colc, cold = st.columns([0.75, 3.4, 1.4, 0.6])
                    with cola:
                        all_icons = [
                            "assets/application/smiley_icon.png",
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
                            key="_button_cycle_2_details"
                        ):
                            display_cycle_details(cycle_2_details[1], cycle_2_details[2], cycle_2_details[3])

                    with cold:
                        if st.button("✏️", use_container_width=True, key="_button_cycle_2_details_edit"):
                            edit_cycle_details(cycle_2_details[1], cycle_2_details[2])

                    st.markdown(
                        """<hr style="height:1px;margin:0px;padding:0px;border:none;color:#111;background-color:#111;" /> """,
                        unsafe_allow_html=True,
                    )

                    # Cycle 3
                    cola, colb, colc, cold = st.columns([0.75, 3.4, 1.4, 0.6])
                    with cola:
                        all_icons = [
                            "assets/application/smiley_icon.png",
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
                            key="_button_cycle_3_details"
                        ):
                            display_cycle_details(cycle_3_details[1], cycle_3_details[2], cycle_3_details[3])

                    with cold:
                        if st.button("✏️", use_container_width=True, key="_button_cycle_3_details_edit"):
                            edit_cycle_details(cycle_3_details[1], cycle_3_details[2])

                    st.markdown(
                        """<hr style="height:1px;margin:0px;padding:0px;border:none;color:#111;background-color:#111;" /> """,
                        unsafe_allow_html=True,
                    )

                    # Cycle 4
                    cola, colb, colc, cold = st.columns([0.75, 3.4, 1.4, 0.6])
                    with cola:
                        all_icons = [
                            "assets/application/smiley_icon.png",
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
                            key="_button_cycle_4_details"
                        ):
                            display_cycle_details(cycle_4_details[1], cycle_4_details[2], cycle_4_details[3])

                    with cold:
                        if st.button("✏️", use_container_width=True, key="_button_cycle_4_details_edit"):
                            edit_cycle_details(cycle_4_details[1], cycle_4_details[2])

                else:
                    periodsdb = PeriodsDB()
                    four_latest_periods = periodsdb.fetch_latest_periods(logged_in_username, 4)

                    if len(four_latest_periods) > 0:
                        # PERIOD 1
                        period_1 = four_latest_periods[0]
                        cola, colb, colc = st.columns([0.75, 3.6, 1.9])
                        
                        with cola:
                            all_icons = [
                                "assets/application/smiley_icon.png",
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
                                key="_button_periods_1"
                            ):
                                edit_periods_details(period_1[2], period_1[3], period_1[4], period_1[5])

                        st.markdown(
                            """<hr style="height:1px;margin:0px;padding:0px;border:none;color:#111;background-color:#111;" /> """,
                            unsafe_allow_html=True,
                        )

                        # PERIOD 2
                        period_2 = four_latest_periods[1]
                        cola, colb, colc = st.columns([0.75, 3.6, 1.9])
                        
                        with cola:
                            all_icons = [
                                "assets/application/smiley_icon.png",
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
                                key="_button_periods_2"
                            ):
                                edit_periods_details(period_2[2], period_2[3], period_2[4], period_2[5])

                        st.markdown(
                            """<hr style="height:1px;margin:0px;padding:0px;border:none;color:#111;background-color:#111;" /> """,
                            unsafe_allow_html=True,
                        )

                        # PERIOD 3
                        period_3 = four_latest_periods[2]
                        cola, colb, colc = st.columns([0.75, 3.6, 1.9])
                        
                        with cola:
                            all_icons = [
                                "assets/application/smiley_icon.png",
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
                                key="_button_periods_3"
                            ):
                                edit_periods_details(period_3[2], period_3[3], period_3[4], period_3[5])

                        st.markdown(
                            """<hr style="height:1px;margin:0px;padding:0px;border:none;color:#111;background-color:#111;" /> """,
                            unsafe_allow_html=True,
                        )

                        # PERIOD 4
                        period_4 = four_latest_periods[3]
                        cola, colb, colc = st.columns([0.75, 3.6, 1.9])
                        
                        with cola:
                            all_icons = [
                                "assets/application/smiley_icon.png",
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
                                key="_button_periods_4"
                            ):
                                edit_periods_details(period_4[2], period_4[3], period_4[4], period_4[5])

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
                    <p align='justify'>Healthy vegetarian meal structured to provide a daily intake of approx 1800 calories, divided across four meals!!</p>
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
                    <p align='justify'>Exclusive exercise routines, designed to complement your overall fitness.</p>
                    """,
                    unsafe_allow_html=True,
                )

                st.button("Download Exercise Routine", use_container_width=True, key="_button_exercise_routine")

        bottom_ribbon_col_1, bottom_ribbon_col_2 = st.columns([4.75, 1,])
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
            unsafe_allow_html=True
        )

        with bottom_ribbon_col_1:
            st.markdown("<H4>Educational Resources</H4>", unsafe_allow_html=True)

        with st.container(border=True):

            cola, colb, colc = st.columns(3)

            with colb:
                st.image(Image.open("assets/application/educational_content_headers/blog_banner_3.jpg"), use_column_width=True)
                st.markdown(
                    "<H6><A HREF='https://medium.com/world-of-opportunity/its-time-for-action-period-298d8a353afc'>It's time for the action. Period</A></H6><P align='justify'>Leading philanthropists and companies call for increased action and investme...</P>",
                    unsafe_allow_html=True,
                )

            with cola:
                st.image(Image.open("assets/application/educational_content_headers/blog_banner_2.jpg"), use_column_width=True)
                st.markdown(
                    "<H6><A HREF='https://thecaseforher.medium.com/introducing-a-new-definition-of-menstrual-health-bfd63aea12dc'>New definition of menstrual health</A></H6><P align='justify'>Global team of experts organized by the Global Menstrual Collective, has come...</P>",
                    unsafe_allow_html=True,
                )

            with colc:
                st.image(Image.open("assets/application/educational_content_headers/blog_banner_1.jpg"), use_column_width=True)
                st.markdown(
                    "<H6><A HREF='https://medium.com/usaid-2030/dignified-menstruation-in-the-workplace-fe19afab97b2'>Dignified Menstruation at Work</A></H6><P align='justify'>Many people who menstruate every month cannot afford to buy a tampon...</P>",
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
