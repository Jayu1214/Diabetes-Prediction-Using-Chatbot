from flask import Flask, render_template, request, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import pandas as pd
import re

# Initialize Flask app
app = Flask(__name__)

# Connect to MySQL database
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="W7301@jqir#",
    database="pbl1"
)

# Password pattern for validation
PASSWORD_PATTERN = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%?&])[A-Za-z\d@$!%?&]{8,}$'

# Initialize tokenizer and model for chatbot
tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")

# Load the preprocessed diabetes data
diabetes_data = pd.read_csv(r"C:\Users\KRISH PANCHAL\Documents\SIT Assignments\PBL-1\Project Theory\Datasets\diabetes.csv")
diabetes_data.dropna(inplace=True)

# Define global variables to track conversation progress
gender_age=False
age_provided = False
glucose_provided = False
bp_provided = False
pregnancies_provided = False
skin_thickness_provided = False
bmi_provided = False
insulin_provided = False
polyuria_provided = False
family_history_provided= False
general_info_provided= False
polydipsia_provided = False
final_assessment_provided=False

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None  # Initialize error message variable

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Authenticate user against MySQL database
        cursor = mydb.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user[3], password):  # Assuming hashed password is stored in the fourth column
            print("User logged in successfully!")
            return redirect(url_for('index'))  # Redirect to index page on successful login
        else:
            error = "Invalid username or password"
            print("Invalid username or password!")

    return render_template('login.html', error=error)


# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

    # Validate password
        if not re.match(PASSWORD_PATTERN, password):
            message = "Password must be at least 8 characters long and include an uppercase letter, a lowercase letter, a number, and a special character."
            return render_template('login.html', message=message)
        
        # Hash the password before storing it in the database
        hashed_password = generate_password_hash(password)

        # Insert the new user's information into the database
        cursor = mydb.cursor()
        cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, hashed_password))
        mydb.commit()  # Commit the transaction

        return redirect(url_for('index'))  # Redirect to index page after successful registration

    return render_template('register.html')

# Index route
@app.route("/")
def index():
    return render_template('index.html')

# Chat route
@app.route("/get", methods=["POST"])
def chat():
    msg = request.form["msg"]
    return get_Chat_response(msg)

def get_Chat_response(text):
    global gender_age, age_provided, glucose_provided, bp_provided, pregnancies_provided, skin_thickness_provided, bmi_provided, insulin_provided, polyuria_provided, family_history_provided, general_info_provided, polydipsia_provided, final_assessment_provided

    # Welcome message and initial prompt
    if "hello" in text.lower():
        return "Hello and welcome to Diabetic Patient Care! How can I assist you today? Please type 'Start' to begin."
    if "start" in text.lower():
        return "Great! Let's get started. Please provide your gender (Male/Female) and age (in years) in the format: 'Gender: [Male/Female], Age: [age]'."

    # Gender and age input
    if "gender" in text.lower() and "age" in text.lower():
        gender_age = re.findall(r'gender:\s*(\w+),\s*age:\s*(\d+)', text, flags=re.IGNORECASE)
        if gender_age:
            gender = gender_age[0][0].capitalize()
            age = int(gender_age[0][1])
            if gender and age:
                age_provided = True
                return f"Thank you. Your gender is {gender} and your age is {age}. Please enter your blood glucose level."
            else:
                return "Sorry, I didn't get your gender and age. Please provide both your gender and age in the format: 'Gender: [Male/Female], Age: [age]'."

    # Glucose input
    if age_provided and not glucose_provided:
        glucose_levels = re.findall(r'\b\d+\b', text)
        if glucose_levels:
            glucose_provided = True
            glucose_level = int(glucose_levels[0])
            # Logic to classify diabetes type based on glucose level
            if glucose_level > diabetes_data['Glucose'].mean() and glucose_level > 126:
                diabetes_type = "Your glucose level is very high, indicating type 1 diabetes associated with hyperglycemia, where blood glucose levels are chronically elevated due to a lack of insulin production.<br><br> \
                You should take care of yourself by:<br> \
                &bull; Monitor blood sugar regularly to track fluctuations and adjust treatment accordingly.<br> \
                &bull; Follow a balanced diet rich in fiber, low in carbohydrates, and moderate in protein and healthy fats.<br> \
                &bull; Engage in regular physical activity to improve insulin sensitivity and lower blood sugar levels."
            elif glucose_level < diabetes_data['Glucose'].mean() and glucose_level < 70:
                diabetes_type ="Your glucose level is low, indicating the possibility of Type 2 diabetes.<br><br> \
                You should take care of yourself by:<br> \
                &bull; Immediately consume fast-acting carbohydrates such as fruit juice, glucose tablets, or candy to raise blood sugar levels.<br> \
                &bull; Follow up with a small snack containing protein and carbohydrates to help stabilize blood sugar levels.<br> \
                &bull; Monitor blood sugar closely and adjust medication or insulin dosage as directed by a healthcare professional."
            else:
                diabetes_type = "Normal Glucose level, no need to worry."
            return f"Based on your blood glucose level, your diagnosis is:<br><br>{diabetes_type}<br><br>Please enter your blood pressure."

        else:
            return "Sorry, I didn't get your glucose level. Please enter your glucose level."
    # Blood pressure input
    if glucose_provided and not bp_provided:
        bp_provided = True
        blood_pressure_levels = re.findall(r'\b\d+\b', text)
        if blood_pressure_levels:
            blood_pressure_level = int(blood_pressure_levels[0])
            # Logic to assess blood pressure and its relation to diabetes
            if blood_pressure_level < diabetes_data['BloodPressure'].mean() and blood_pressure_level < 80:
                bp_diagnosis = "Low Blood Pressure.<br> \
                    1. Increase fluid and salt intake to help raise blood pressure.<br> \
                    2. Eat smaller, more frequent meals to prevent postprandial hypotension (low blood pressure after eating).<br> \
                    3. Avoid sudden changes in position, such as standing up quickly, to prevent dizziness or fainting."
            elif blood_pressure_level > diabetes_data['BloodPressure'].mean() and blood_pressure_level > 140:
                bp_diagnosis = "High Blood Pressure (Hypertension). Hypertension stage 1 between 130-139, and stage 2 above 140<br> \
                            You should take care of yourself by:<br> \
                            &bull; Limit sodium intake by avoiding processed and high-sodium foods.<br> \
                            &bull; Increase consumption of fruits, vegetables, and whole grains rich in potassium and magnesium, which help lower blood pressure.<br> \
                            &bull; Engage in regular physical activity, such as brisk walking or swimming, to help reduce blood pressure and improve overall cardiovascular health."
            else:
                bp_diagnosis = "Normal Blood Pressure"
            return f"Based on your blood pressure, your diagnosis is {bp_diagnosis}. Please enter your number of pregnancies (if applicable), if not applicable press '00' to skip."
        else:
            return "Sorry, I didn't get your blood pressure level. Please enter your blood pressure level."

    if bp_provided and not pregnancies_provided:
        pregnancies_provided = True
        pregnancies = re.findall(r'\b\d+\b', text)
        if pregnancies:
            num_pregnancies = int(pregnancies[0])
            # Logic to assess the impact of pregnancies on diabetes risk (if applicable)
            if num_pregnancies != 00:
                if num_pregnancies == 0:
                    pregnancy_diagnosis = "No Previous Pregnancies, so no risk of Gestational Diabetes."
                elif num_pregnancies == 1:
                    pregnancy_diagnosis = "Single Previous Pregnancy, so no risk of Gestation Diabetes."
                elif num_pregnancies == 2:
                    pregnancy_diagnosis = "Low Risk as your pregnancies number are normal. For precautionary measures, kindly do check-up."
                elif num_pregnancies >= 3:
                    pregnancy_diagnosis = "Higher Risk Due to Many Previous Pregnancies.<br> \
                        Women who have had multiple pregnancies, particularly if they've had GDM  in previous pregnancies, are at a higher risk of developing GDM in subsequent pregnancies.<br> \
                        &bull; GDM stands for Gestational Diabetes Mellitus. It's a type of diabetes that develops during pregnancy and usually resolves after giving birth.<br> \
                        &bull; In GDM, the body either cannot produce enough insulin to meet the increased needs during pregnancy, or the body's cells become resistant to insulin. This leads to high blood sugar levels, which can pose risks to both the mother and the baby."
                return f"Based on your number of pregnancies, your diagnosis is {pregnancy_diagnosis}. Please enter your skin thickness, if you know about it, otherwise you can skip it by typing 0."
            else:
                return "You've chosen to skip providing the number of pregnancies. Please enter your Skin Thickness or type '000' to skip."

    # Skin thickness input
    if pregnancies_provided and not skin_thickness_provided:
        skin_thickness_provided = True
        skin_thicknesses = re.findall(r'\b\d+\b', text)
        if skin_thicknesses:
            skin_thickness = int(skin_thicknesses[0])
            # Logic to assess skin thickness and its relation to diabetes
            if skin_thickness != 000:
                if skin_thickness < diabetes_data['SkinThickness'].mean():
                    skin_diagnosis = "Normal Skin Thickness"
                elif skin_thickness > diabetes_data['SkinThickness'].mean():
                    skin_diagnosis = "High Skin Thickness"
                else:
                    skin_diagnosis = "Average Skin Thickness"
                return f"Based on your skin thickness, your diagnosis is {skin_diagnosis}. Please enter your BMI (Body Mass Index)."
            else:
                return "You've chosen to skip providing your skin thickness. Please enter your BMI (Body Mass Index)."
        else:
            return "Sorry, I didn't get your skin thickness. Please enter your skin thickness, or type 000 to skip."

    # BMI input
    if skin_thickness_provided and not bmi_provided:
        bmi_provided = True
        bmis = re.findall(r'\b\d+\b', text)
        if bmis:
            bmi = int(bmis[0])
            # Logic to assess BMI and its relation to diabetes
            if bmi < 18.5:
                bmi_diagnosis = "Low BMI, you are underweight. <br> \
                    If you have low BMI, you should follow: <br> \
                    &bull; Focus on consuming nutrient-dense foods that are high in calories and protein to support healthy weight gain.<br> \
                    &bull; Incorporate strength training exercises into their fitness routine to build muscle mass and increase overall body weight.<br> \
                    &bull; Consult with a healthcare professional or dietitian to create a personalized meal plan to meet their caloric and nutritional needs for weight gain."
            elif bmi > 24.5:
                bmi_diagnosis = "High BMI (Obese). You might be at higher risk of Type 2 diabetes as Type 2 diabetes is often associated with obesity or overweight, particularly abdominal obesity.<br> \
                    If you have high BMI, you should follow: <br> \
                    &bull; Mindful Eating Practices: Encourage mindfulness during meals by slowing down eating pace, chewing food thoroughly, and paying attention to hunger and fullness cues. This can help prevent overeating and promote better digestion.<br> \
                    &bull; Portion Control with Visual Aids: Utilize visual aids like smaller plates, bowls, and utensils to control portion sizes. Research suggests that using smaller dishware can lead to decreased food intake without sacrificing satisfaction.<br> \
                    &bull; Incorporate Intermittent Fasting: Experiment with intermittent fasting protocols, such as the 16/8 method (fasting for 16 hours and eating within an 8-hour window) or alternate-day fasting. These approaches may help regulate appetite and improve metabolic health.  "
            else:
                bmi_diagnosis = "Normal BMI"
            return f"Based on your BMI, your diagnosis is {bmi_diagnosis}. Please enter your insulin level."
        else:
            return "Sorry, I didn't get your bmi. Please enter your bmi."

    # Insulin input
    if bmi_provided and not insulin_provided:
        insulin_provided = True
        insulin_levels = re.findall(r'\b\d+\b', text)
        if insulin_levels:
            insulin_level = int(insulin_levels[0])
            # Logic to assess insulin level and its relation to diabetes
            if insulin_level < diabetes_data['Insulin'].mean():
                insulin_diagnosis = "Low Insulin Level<br> \
                    For low Insulin level, you should follow: <br> \
                    &bull; Follow a low-carbohydrate diet to minimize the need for insulin and help stabilize blood sugar levels.<br> \
                    &bull; Engage in regular physical activity to improve insulin sensitivity and promote glucose uptake by cells.<br> \
                    &bull; Monitor blood sugar levels closely and work with a healthcare provider to adjust medication dosage as needed to maintain optimal blood sugar control."
            elif insulin_level > diabetes_data['Insulin'].mean():
                insulin_diagnosis = "High Insulin Level. Type 2 diabetes initially involves high insulin levels due to insulin resistance, but over time, insulin production may decline.<br> \
                    For low Insulin level, you should follow: <br> \
                        &bull; Focus on a balanced diet rich in whole foods, emphasizing fiber, lean protein, and healthy fats to help regulate insulin levels.<br> \
                        &bull; Engage in regular physical activity, including both aerobic exercise and strength training, to improve insulin sensitivity and lower blood sugar levels.<br> \
                        &bull; Monitor carbohydrate intake and aim to spread it out evenly throughout the day to prevent spikes in insulin production."
            else:
                insulin_diagnosis = "Average Insulin Level"
            return f"Based on your insulin level, your diagnosis is {insulin_diagnosis}. Are you experiencing polyuria (frequent urination)? (Please answer 'yes' or 'no')."
        else:
            return "Sorry, I didn't get your insulin level. Please enter your insulin level."

    # Polyuria input
    if insulin_provided and not polyuria_provided:
        polyuria_provided = True
        if "yes" in text.lower():
            return "Polyuria, or excessive urination, is a common symptom of diabetes. This is a major indication that you might have diabetes.Is there any history of diabetes in your family members ? (Please answer 'yes' or 'no')<br>\
                &bull; If 'yes' than which members of your family have had history of diabetes?"
        elif "no" in text.lower():
            return "Thank you for the information. Is there any history of diabetes in your family members ? (Please answer 'yes' or 'no')<br>\
                &bull; If 'yes' than which members of your family have had history of diabetes?"
        else:
            return "I'm sorry, I didn't understand your response. Please answer 'yes' or 'no'."

    if polyuria_provided and not family_history_provided:
        family_history_provided= True
        if "yes" in text.lower():
            return "Family Diabetes History is a major indication that you might have diabetes, as people with family diabetes history are more prone to diabetes. Are your wounds and cuts slow to heal? (Please answer 'yes' or 'no')."
        elif "no" in text.lower():
            return "Thank you for the information.  Are your wounds and cuts slow to heal? (Please answer 'yes' or 'no')."
        else:
            return "I'm sorry, I didn't understand your response. Please answer 'yes' or 'no'."

    if family_history_provided and not general_info_provided:
        general_info_provided=True
        if "yes" in text.lower():
            return "Slow healing of wounds and cuts can be an indication of diabetes.<br> \
                 &bull;In diabetes, high blood sugar levels can damage blood vessels and affect circulation, which impairs the body's ability to heal wounds properly. Additionally, diabetes can weaken the immune system, making it harder for the body to fight off infections that may further delay healing. <br> \
                 &bull; Are you experiencing polydipsia (constant thirst)? (Please answer 'yes' or 'no')."
        elif "no" in text.lower():
            return "Thank you for the information. Are you experiencing polydipsia (constant thirst)? (Please answer 'yes' or 'no')."
        else:
            return "I'm sorry, I didn't understand your response. Please answer 'yes' or 'no'."
   
    # Polydipsia input
    if general_info_provided and not polydipsia_provided:
        polydipsia_provided = True
        if "yes" in text.lower():
            return "Polydipsia, or excessive thirst, is another common symptom of diabetes. This is a major indication that you might have diabetes. Please enter your glucose, insulin level, blood pressure, and body mass index (bmi) for final assessment, assistance as well as suggestions."
        elif "no" in text.lower():
            return "Thank you for the information. Please enter your glucose, insulin level, blood pressure, and body mass index (bmi) for final assessment, assistance as well as suggestions.(Do not use commas)"
        else:
            return "I'm sorry, I didn't understand your response. Please answer 'yes' or 'no'."

    if polydipsia_provided and not final_assessment_provided:
        final_assessment_provided = True
        glucose_levels = re.findall(r'\b\d{2,3}\b', text)
        insulin_levels = re.findall(r'\b\d{2,3}\b', text)
        blood_pressure_levels = re.findall(r'\b\d{2,3}\b', text)
        bmis = re.findall(r'\b\d{2}\b', text)

        glucose_provided = True
        insulin_provided = True
        bmi_provided = True
        bp_provided = True

        print("Glucose levels:", glucose_levels)
        print("Insulin levels:", insulin_levels)
        print("Blood pressure levels:", blood_pressure_levels)
        print("BMI levels:", bmis)

        if glucose_levels and insulin_levels and blood_pressure_levels and bmis:
            glucose_level = int(glucose_levels[0])  # Corrected assignment
            insulin_level = int(insulin_levels[1])  # Corrected assignment
            bmi = int(bmis[-1])  # Corrected assignment (assuming BMI is the last value)
            blood_pressure_level = int(blood_pressure_levels[-2])  # Corrected assignment

            print("Glucose level:", glucose_level)
            print("Insulin level:", insulin_level)
            print("BMI:", bmi)
            print("Blood pressure:", blood_pressure_level)

            if insulin_level > diabetes_data['Insulin'].mean() and glucose_level > diabetes_data['Glucose'].mean() and glucose_level > 130 and blood_pressure_level > 135 and bmi > 29:
                return "Based on your inputs, you might have type 2 diabetes. Please type 'Type 2' for further assistance on Type 2 diabetes."

            elif insulin_level < diabetes_data['Insulin'].mean() and insulin_level<40 and glucose_level > diabetes_data['Glucose'].mean() and glucose_level > 180 and blood_pressure_level > 130 and bmi <= 25:
                return "Based on your inputs, you might have type 1 diabetes. Please type 'Type 1' for further assistance on Type 1 diabetes."

            else:
                return "Based on your inputs, you are perfectly fit and fine person, no need to worry, stay healthy stay safe."

        else:
            return "Please provide glucose, insulin, blood pressure levels, and BMI for final assessment."

    if "type 1" in text.lower():
        return "Based on your inputs you might have Type 1 diabetes. Here are some suggestions:<br> \
                1. Insulin Therapy:<br> \
                - Work closely with a healthcare provider to determine the appropriate type of insulin, dosage, and injection schedule.<br> \
                - Utilize resources such as patient assistance programs or community health clinics to access affordable insulin and supplies if needed.<br> \
                2. Blood Glucose Monitoring:<br> \
                - Regularly monitor blood glucose levels using a glucometer or continuous glucose monitoring (CGM) system.<br> \
                - Take note of patterns and trends in blood glucose levels to adjust insulin doses as necessary.<br> \
                3. Physical Activity:<br> \
                - Engage in regular physical activity, such as walking, jogging, cycling, or dancing, to help improve insulin sensitivity and overall health.<br> \
                - Choose activities that are enjoyable and feasible to incorporate into daily life.<br> \
                4. Healthy Diet:<br> \
                - Focus on a balanced diet that includes a variety of nutrient-rich foods, such as fruits, vegetables, whole grains, lean proteins, and healthy fats.<br> \
                - Limit the intake of processed foods, sugary snacks, and beverages high in added sugars.<br> \
                - Monitor carbohydrate intake and distribute it evenly throughout meals to help manage blood glucose levels.<br> \
                - Consider affordable sources of protein, such as beans, lentils, tofu, eggs, and canned fish.<br> \
                5. Meal Planning:<br> \
                - Plan meals and snacks ahead of time to ensure balanced nutrition and proper carbohydrate counting.<br> \
                - Experiment with budget-friendly recipes and meal ideas that incorporate affordable ingredients.<br> \
                - Use resources such as community cooking classes, online recipes, and nutrition education programs to learn how to prepare healthy and affordable meals at home.<br> \
                6. Hydration:<br> \
                - Stay hydrated by drinking plenty of water throughout the day.<br> \
                - Limit the consumption of sugary beverages and opt for water, herbal teas, or infused water instead.<br> \
                7. Support and Education:<br> \
                - Seek support from diabetes support groups, online communities, or local organizations to connect with others living with type 1 diabetes.<br> \
                - Take advantage of educational resources, workshops, and seminars to learn more about diabetes management and self-care.<br> \
                <br> \
                -Press 'Ok' to continue"

    if "type 2" in text.lower():
        return "Based on your inputs you might have Type 2 diabetes. Here are some suggestions:<br> \
                1. Blood Glucose Monitoring:<br> \
                - Regularly monitor blood glucose levels using a glucometer or continuous glucose monitoring (CGM) system.<br> \
                - Take note of patterns and trends in blood glucose levels to make informed decisions about diet and medication.<br> \
                2. Healthy Diet:<br> \
                - Focus on a balanced diet that includes a variety of nutrient-rich foods, such as fruits, vegetables, whole grains, lean proteins, and healthy fats.<br> \
                - Limit the intake of processed foods, sugary snacks, and beverages high in added sugars.<br> \
                - Monitor portion sizes and carbohydrate intake to help manage blood glucose levels.<br> \
                3. Physical Activity:<br> \
                - Engage in regular physical activity, such as walking, jogging, swimming, or cycling, to help improve insulin sensitivity and lower blood glucose levels.<br> \
                - Aim for at least 150 minutes of moderate-intensity aerobic activity per week, spread throughout the week.<br> \
                4. Medication and Treatment:<br> \
                - Work closely with a healthcare provider to determine the most appropriate medication and treatment plan for your individual needs.<br> \
                - Take medications as prescribed and follow up regularly with your healthcare team to monitor progress and make adjustments as needed.<br> \
                5. Weight Management:<br> \
                - Aim for a healthy weight by following a balanced diet and engaging in regular physical activity.<br> \
                - Set realistic goals for weight loss or weight maintenance, and track progress over time.<br> \
                - Consider seeking support from a registered dietitian or certified diabetes educator for personalized guidance and support.<br> \
                6. Stress Management and Mental Health:<br> \
                - Practice stress-reduction techniques such as deep breathing, meditation, or yoga to help manage stress levels.<br> \
                - Prioritize self-care and make time for activities that bring you joy and relaxation.<br> \
                - Seek support from friends, family, or mental health professionals if you're experiencing emotional or psychological challenges related to diabetes management.<br> \
                    <br> \
                -Press 'Ok' to continue"

    
    if "ok" in text.lower():
        return "Your consultation is completed, we hope that you follow all the steps we mentioned.<br> \
            &bull;Chatbot is for informational, immediate assistance and early detection purpose only.<br> \
            &bull;Early detection and management of diabetes are crucial for preventing complications and maintaining overall health.<br> \
            &bull;Kindly consult a doctor or visit a clinic for complete in detail check-up and proper advice."
    return "I'm sorry, I didn't understand your request. Please try again."
# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
