import time
import datetime
import numpy as np
import pandas as pd
from PIL import Image
import google.generativeai as genai

import streamlit as st
import streamlit_antd_components as sac

from backend.database import UserDB, PostsDB, NotificationsDB
from backend.genai_engine import FloAI


st.set_page_config(
    page_title="Flo: Profile",
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


@st.experimental_dialog("Edit Your Post")
def popup_edit_post(postid, content, created_on):
    new_content = st.text_area(
        "Post Content", value=content, label_visibility="collapsed"
    )
    button_publish_changes = st.button("✏️ Publish Changes")

    if button_publish_changes:
        postsdb = PostsDB()
        new_created_on = created_on

        if "Edited" not in created_on:
            new_created_on = str(created_on) + " • Edited"

        postsdb.edit_post(postid, content=new_content, created_on=new_created_on)

        st.success("Changes saved successfully", icon="✔️")
        time.sleep(5)
        st.rerun()


if __name__ == "__main__":
    st.write(" ")
    logged_in_username = st.session_state.logged_in_username

    if 1 == 1:
        with st.sidebar:
            profile_pic_container = st.container(height=495, border=False)

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

        ribbon_col_1, ribbon_col_2, ribbon_col_3 = st.columns([4.6, 1, 0.4])

        with ribbon_col_1:
            st.markdown("<H4>Manage your Profile</H4>", unsafe_allow_html=True)

        with ribbon_col_2:
            if st.button("❌ LogOut", use_container_width=True):
                st.session_state.logged_in_username = None
                st.session_state.user_authentication_status = None

                st.switch_page("main.py")

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

        st.markdown(
            "<P align='justify'>Welcome to your profile! Here you can update your personal details, including dietary preferences and medical conditions. Engage with the community by sharing your experience and make the most of your journey towards better menstrual health and wellness</P>",
            unsafe_allow_html=True,
        )

        userdb = UserDB()
        (
            _,
            logged_in_users_full_name,
            logged_in_users_dob,
            logged_in_users_height,
            logged_in_users_weight,
            logged_in_users_phone_number,
            logged_in_users_address,
            logged_in_users_profile_pic_url,
            logged_in_users_dietary_preferences,
            logged_in_users_allergies,
            logged_in_users_medical_conditions,
            logged_in_users_avg_cycle_length,
            logged_in_users_avg_periods_length,
        ) = userdb.get_user(logged_in_username)

        selected_profile_tab = sac.tabs(
            [
                sac.TabsItem(label="Personal Details"),
                sac.TabsItem(label="Published Posts"),
            ],
            variant="outline",
        )

        if selected_profile_tab == "Personal Details":
            with st.container(border=True):
                st.markdown(
                    "<H6>🛠️ Edit Your Personal Details</H6>", unsafe_allow_html=True
                )

                cola, colb = st.columns(2)

                with cola:
                    new_name = st.text_input(
                        "Full Name", value=logged_in_users_full_name
                    )
                with colb:
                    new_dob = st.date_input(
                        "Date of Birth",
                        datetime.datetime.strptime(logged_in_users_dob, "%Y-%m-%d"),
                        min_value=datetime.datetime.strptime("1950-01-01", "%Y-%m-%d"),
                    )

                cola, colb, colc = st.columns(3)

                with cola:
                    new_height = st.text_input(
                        "Height (in cm)", value=logged_in_users_height
                    )
                with colb:
                    new_weight = st.text_input(
                        "Weight (in kg)", value=logged_in_users_weight
                    )
                with colc:
                    new_phone_number = st.text_input(
                        "Phone No.", value=logged_in_users_phone_number
                    )

                cola, colb = st.columns(2)

                with cola:
                    new_address = st.text_area(
                        "Registered Address", value=logged_in_users_address, height=161
                    )
                with colb:
                    new_file_uploaded = st.file_uploader(
                        "Profile Picture", accept_multiple_files=False
                    )

                    with profile_pic_container:
                        st.image(
                            Image.open(logged_in_users_profile_pic_url),
                            use_column_width=True,
                        )

                    list_dietary_preferences = [
                        "Vegetarian",
                        "Non-Vegetarian",
                        "Ovo-Vegetarian (Eggs Only)",
                    ]

                    pre_selected_dietary_preferences_index = (
                        list_dietary_preferences.index(
                            logged_in_users_dietary_preferences
                        )
                    )

                    new_dietary_preference = st.selectbox(
                        "Dietary Preferences",
                        list_dietary_preferences,
                        placeholder="Select your Dietary Preferences",
                        index=pre_selected_dietary_preferences_index,
                    )

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

                    pre_selected_allergies = [
                        allergy.strip()
                        for allergy in logged_in_users_allergies.split(",")
                    ]

                    if (len(pre_selected_allergies) == 1) and (
                        (pre_selected_allergies[0] == "None")
                        or (pre_selected_allergies[0] == "")
                    ):
                        pre_selected_allergies = None

                    new_allergies = st.multiselect(
                        "List your Allergies",
                        list_allergies,
                        default=pre_selected_allergies,
                        placeholder="Select allergies you have",
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

                    pre_selected_medical_conditions = [
                        medical_condition.strip()
                        for medical_condition in logged_in_users_medical_conditions.split(
                            ","
                        )
                    ]

                    if (len(pre_selected_medical_conditions) == 1) and (
                        (pre_selected_medical_conditions[0] == "None")
                        or (pre_selected_medical_conditions[0] == "")
                    ):
                        pre_selected_medical_conditions = None

                    new_medical_conditions = st.multiselect(
                        "List Medical Conditions",
                        list_medical_conditions,
                        default=pre_selected_medical_conditions,
                        placeholder="Select any medical condition you have",
                    )

                cola, _, _ = st.columns(3)
                with cola:
                    button_save_user_details = st.button(
                        "Save your Changes", use_container_width=True
                    )

                if button_save_user_details:
                    if new_file_uploaded:
                        try:
                            if new_file_uploaded is not None:
                                uploaded_filename = new_file_uploaded.name

                                image_file_path = os.path.join(
                                    "assets/user_profile", uploaded_filename
                                )

                                with open(image_file_path, "wb") as f:
                                    f.write(new_file_uploaded.getbuffer())

                        except:
                            image_file_path = logged_in_users_profile_pic_url

                    else:
                        image_file_path = logged_in_users_profile_pic_url

                    userdb = UserDB()
                    userdb.edit_user(
                        logged_in_username,
                        name=new_name,
                        dob=new_dob,
                        height=new_height,
                        weight=new_weight,
                        phone=new_phone_number,
                        address=new_address,
                        profile_pic_url=image_file_path,
                        dietary_preferences=new_dietary_preference,
                        allergies=", ".join(new_allergies),
                        medical_conditions=", ".join(new_medical_conditions),
                    )

                    st.success("Changes saved successfully", icon="✔️")
                    time.sleep(5)
                    st.rerun()

        else:
            with profile_pic_container:
                st.image(
                    Image.open(logged_in_users_profile_pic_url),
                    use_column_width=True,
                )

            mid_ribbon_col_1, mid_ribbon_col_2 = st.columns(
                [
                    2,
                    1,
                ]
            )

            with mid_ribbon_col_2:
                with st.container(border=True):
                    st.markdown("<H6>💡 Your Analytics</H6>", unsafe_allow_html=True)

                    postsdb = PostsDB()
                    posts_made_by_user = (
                        postsdb.get_total_likes_dislikes_reports_posts_count(
                            logged_in_username
                        )
                    )

                    col1, col2 = st.columns([1, 3])
                    with col1:
                        st.image(
                            Image.open("assets/app_graphics/comm_red.png").resize(
                                (50, 50)
                            )
                        )
                    with col2:
                        if posts_made_by_user[3] == 0:
                            st.markdown(
                                f"<B>Total Posts</B><BR>No posts shared yet",
                                unsafe_allow_html=True,
                            )
                        else:
                            st.markdown(
                                f"<B>Total Posts</B><BR>You've shared {posts_made_by_user[3]} Posts",
                                unsafe_allow_html=True,
                            )

                    with col1:
                        st.image(
                            Image.open("assets/app_graphics/comm_blue.png").resize(
                                (50, 50)
                            )
                        )
                    with col2:
                        if posts_made_by_user[0] == None:
                            st.markdown(
                                f"<B>Upvotes</B><BR>No likes received",
                                unsafe_allow_html=True,
                            )
                        else:
                            st.markdown(
                                f"<B>Upvotes</B><BR>You've received {posts_made_by_user[0]} likes",
                                unsafe_allow_html=True,
                            )

                    with col1:
                        st.image(
                            Image.open("assets/app_graphics/comm_green.png").resize(
                                (50, 50)
                            )
                        )
                    with col2:
                        if posts_made_by_user[1] == None:
                            st.markdown(
                                f"<B>Upvotes</B><BR>No dislikes received",
                                unsafe_allow_html=True,
                            )
                        else:
                            st.markdown(
                                f"<B>Downvotes</B><BR>Received {posts_made_by_user[1]} dislikes",
                                unsafe_allow_html=True,
                            )

                    with col1:
                        st.image(
                            Image.open("assets/app_graphics/comm_yellow.png").resize(
                                (50, 50)
                            )
                        )
                    with col2:
                        if posts_made_by_user[2] == None:
                            st.markdown(
                                f"<B>Upvotes</B><BR>No posts reported",
                                unsafe_allow_html=True,
                            )
                        else:
                            st.markdown(
                                f"<B>Reported</B><BR>Posts reported {posts_made_by_user[2]} times",
                                unsafe_allow_html=True,
                            )

            with mid_ribbon_col_1:
                postsdb = PostsDB()
                posts_made_by_user = postsdb.get_post_by_userid(logged_in_username)

                if len(posts_made_by_user) < 1:
                    st.markdown("<BR>" * 2, unsafe_allow_html=True)
                    sac.result(
                        label="No Posts Shared",
                        description="Posts created by you will appear here",
                        status="empty",
                    )

                for post in posts_made_by_user:
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
                        ) = userdb.get_user(post[1])

                        with col1:
                            st.image(
                                Image.open(author_img_url).resize((33, 33)),
                                use_column_width=True,
                            )
                        with col2:
                            st.markdown(
                                f"<B>{author_name}</B><BR>{post[2]}",
                                unsafe_allow_html=True,
                            )

                        st.markdown(post[3])

                        try:
                            st.image(Image.open(post[4]), use_column_width=True)
                        except Exception as error:
                            pass

                        cola, colc, _, _, _, colx = st.columns([2, 1, 1, 1, 1, 4])

                        with cola:
                            button_edit_post = st.button(
                                "✏️ Edit",
                                use_container_width=True,
                                key=f"_like_button_{post[0]}",
                            )

                        with colx:
                            button_delete_post = st.button(
                                "❌ Delete this Post",
                                use_container_width=True,
                                key=f"_report_post_button_{post[0]}",
                            )

                        if button_edit_post:
                            popup_edit_post(post[0], post[3], post[2])

                        if button_delete_post:
                            postsdb = PostsDB()
                            postsdb.delete_post(post[0])

                            st.success("Your post has been deleted", icon="✔️")
                            time.sleep(5)
                            st.rerun()

            with mid_ribbon_col_2:
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

        with profile_pic_container:
            with st.expander("👩‍⚕️ Update your Cycle details", expanded=False):
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

                new_cycle_length = st.number_input(
                    "Average Cycle Length", value=int(logged_in_users_avg_cycle_length)
                )
                new_period_length = st.number_input(
                    "Average Period Length",
                    value=int(logged_in_users_avg_periods_length),
                )

                if st.button("Update Details", use_container_width=True):
                    userdb.edit_user(
                        logged_in_username, avg_cycle_length=new_cycle_length
                    )

                    st.success("Cycle Details Updated Successfully", icon="✔️")
                    try:
                        notifdb = NotificationsDB()
                        message = "Menstrual cycle data has been updated"
                        notifdb.add_notification(
                            logged_in_username,
                            datetime.datetime.today().date(),
                            message,
                        )
                    except:
                        pass

                    time.sleep(5)
                    st.rerun()

            with st.expander("🥗 Generate 7-Day Meal Plan", expanded=False):
                cola, colb = st.columns(2)

                with cola:
                    todays_date = datetime.datetime.utcnow() + datetime.timedelta(
                        hours=5, minutes=30
                    )
                    start_date = st.date_input("Start Date", todays_date)

                with colb:
                    end_date = st.date_input(
                        "End Date",
                        start_date + datetime.timedelta(days=6),
                        disabled=True,
                    )

                if st.button(
                    "Generate Meal Plan",
                    use_container_width=True,
                ):
                    try:
                        floai = FloAI()
                        floai.generate_meal_plan_and_exercise_routine(
                            start_date, end_date, logged_in_username
                        )

                        st.success("New meal plan generated!", icon="✔️")
                        time.sleep(1)

                        st.toast("Download your meal plan from your dashboard")

                        try:
                            notifdb = NotificationsDB()
                            message = "New meal plan generated for you"
                            notifdb.add_notification(
                                logged_in_username,
                                datetime.datetime.today().date(),
                                message,
                            )
                        except:
                            pass

                        time.sleep(4)
                        st.rerun()

                    except Exception as error:
                        st.warning("Unable to generate meal plan", icon="⚠️")
                        time.sleep(2)
                        st.rerun()

            st.info(
                "Your exercie routine will be auto adjusted to match the meal plan",
                icon="ℹ️",
            )
