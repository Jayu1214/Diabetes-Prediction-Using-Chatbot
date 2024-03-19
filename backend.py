from flask import Flask, render_template, request, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Initialize Flask app
app = Flask(__name__)

# Connect to MySQL database
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="W7301@jqir#",
    database="pbl1"
)

# Initialize tokenizer and model for chatbot
tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")

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

        # Hash the password before storing it in the database
        hashed_password = generate_password_hash(password)

        # Insert the new user's information into the database
        cursor = mydb.cursor()
        cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, hashed_password))
        mydb.commit()  # Commit the transaction

        return redirect(url_for('login'))  # Redirect to login page after successful registration

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
    # Let's chat for 5 lines
    for step in range(5):
        # encode the new user input, add the eos_token and return a tensor in Pytorch
        new_user_input_ids = tokenizer.encode(str(text) + tokenizer.eos_token, return_tensors='pt')

        # append the new user input tokens to the chat history
        bot_input_ids = torch.cat([chat_history_ids, new_user_input_ids], dim=-1) if step > 0 else new_user_input_ids

        # generated a response while limiting the total chat history to 1000 tokens, 
        chat_history_ids = model.generate(bot_input_ids, max_length=1000, pad_token_id=tokenizer.eos_token_id)

        # pretty print last ouput tokens from bot
        return tokenizer.decode(chat_history_ids[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
