from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def index():
    return "Welcome to the Diabetic Patient Care Chatbot!"

@app.route("/process-message", methods=["POST"])
def process_message():
    data = request.get_json()
    user_message = data["message"]

    # Add your logic to process the user message and generate a bot response here
    # For demonstration purposes, let's just echo back the user message
    bot_response = "You said: " + user_message

    return jsonify({"message": bot_response})

if __name__ == "__main__":
    app.run(debug=True)
