import re
import sqlite3
import string
from datetime import datetime, timezone, timedelta

import google.generativeai as genai

from backend.database import UserDB
from configs import credentials


class FloAI:
    def __init__(self):
        genai.configure(api_key=str(credentials.GEMINI_API_KEY))

    def analyze_symptoms(self, query):
        model = genai.GenerativeModel("gemini-1.5-flash")

        prompt = f"""
        "Users will enter their symptoms and ask questions related to menstrual health.
        Respond with informative, empathetic, and accurate answers in under 20 words 
        based on the symptoms and questions provided. Include possible causes, recommended 
        actions, and when to seek medical advice. Ensure the tone is supportive and professional."

        Example Input:
        "I've been experiencing irregular periods and severe cramps. What could be the cause and what should I do?"

        Example Output:
        "Consult a doctor. Possible causes: hormonal imbalances, PCOS, or stress. Track symptoms for diagnosis"

        User Query: {query}
        """
        response = model.generate_content(prompt)
        print(response)
        return response.text

    def generate_meal_plan_and_exercise_routine(
        self, start_date, end_date, logged_in_username
    ):
        userdb = UserDB()
        (
            _,
            logged_in_users_full_name,
            logged_in_users_dob,
            logged_in_users_height,
            logged_in_users_weight,
            _,
            _,
            _,
            dietary_preferences,
            allergies,
            medical_conditions,
            logged_in_users_avg_cycle_length,
            logged_in_users_avg_periods_length,
        ) = userdb.get_user(logged_in_username)

        model = genai.GenerativeModel("gemini-1.5-flash")

        meal_plan_prompt = f"""
            I need a five-day meal plan for a women named {logged_in_users_full_name}. Please consider the following factors:
            
            Date Range for Meal Plan: {str(start_date)} to {str(end_date)}
            Daily Routine and Meal Patterns: 4 meals per day (One Breakfast, One Lunch, One Snacks, and One Dinner)

            ## Patient Information:
            - **Date of Birth:** {logged_in_users_dob}
            - **Gender:** Female
            - **Weight:** {logged_in_users_weight} kg
            - **Height:** {logged_in_users_height} cm
            - **Medical Conditions:** {medical_conditions}
            - **Metabolic Rate:** Basal Metabolic Rate (BMR) of 1800 kcal/day

            ## Dietary Needs and Restrictions:
            - **Food Allergies and Intolerances:** {allergies}
            - **Meal Type:** Indian {dietary_preferences}

            ## Lifestyle Factors:
            - **Physical Activity Level:** Moderate
            - **Socioeconomic Status:** Moderate food budget

            Note: The women could be menstruating. Do consider that when generating the meal plan.

            Using this information, please generate a personalized and nutritionally balanced seven-day meal plan.
            IMPORTANT: The output shall be in a Readable format as described below (This sample is for only one day). Strictly follow this structure to generate the seven day meal plan. 
            
            EXAMPLE FORMAT TO BE USED:

            July 07, 2024
            - Breakfast: 2 Idlis with Sambar and Coconut Chutney
            - Lunch: Chicken Curry with Chapati and Raita
            - Snacks: Fruit Salad with Yogurt
            - Dinner: Vegetable Biryani with Raita

            Also include Notes and Important points to keep in mind at the end of the file            
        """

        completion = model.generate_content(meal_plan_prompt)

        meal_plan_path = f"assets/meal_plans/{logged_in_username}_meal_plan.txt"
        with open(meal_plan_path, "w") as file:
            file.write(completion.text)

        exercise_plan_prompt = f"""
            I need a seven-day exercise plan for a woman named {logged_in_users_full_name}. Please consider the following factors:

            Date Range for Exercise Plan: {str(start_date)} to {str(end_date)}

            ## Patient Information:
            - **Date of Birth:** {logged_in_users_dob}
            - **Gender:** Female
            - **Weight:** {logged_in_users_weight} kg
            - **Height:** {logged_in_users_height} cm
            - **Medical Conditions:** {medical_conditions}
            - **Fitness Goal:** Maintain overall fitness and flexibility

            ## Physical Activity Level:
            - **Current Activity Level:** Moderate
            - **Exercise Preferences:** Prefer activities that can be done at home or outdoors
            - **Weekly Exercise Goal:** At least 150 minutes of moderate-intensity aerobic activity

            ## Exercise Plan Structure:
            - Include warm-up and cool-down sessions for each day
            - Focus on a variety of exercises to target different muscle groups
            - Consider activities suitable for menstruation phases if applicable

            Note: The women could be menstruating. Do consider that when generating the exercise plan.

            Using this information, please generate a personalized and balanced seven-day exercise plan. 
            Ensure each day includes exercise types, duration, and intensity appropriate for the user's fitness level.
            
            EXAMPLE FORMAT TO BE USED:
            
            July 07, 2024
            - Morning: 45-minute Cardio
            - Evening: 45-minute strength training (bodyweight exercises)

            Also include Notes and Important points to keep in mind at the end of the file.
            """
        completion = model.generate_content(exercise_plan_prompt)

        exercise_plan_path = (
            f"assets/exercise_plans/{logged_in_username}_exercise_plan.txt"
        )
        with open(exercise_plan_path, "w") as file:
            file.write(completion.text)
