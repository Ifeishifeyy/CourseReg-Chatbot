import nltk
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from chat import get_response
import json
import secrets

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

app = Flask(__name__)
CORS(app)
#app.secret_key = secrets.token_hex(32)

with open('courses.json', 'r') as f:
    courses = json.load(f)

@app.get("/")
def index_get():
    return render_template('base.html')


@app.post("/predict")
@app.post("/predict")
def predict():
    data = request.get_json()
    text = data.get("message")
    program = data.get("program")
    level = data.get("level")
    option = data.get("option", None)

    if not text:
        return jsonify({"response": "Please provide a valid message."}), 400
        
    try:
        # At the start of your prediction handler
        if program == "industrial mathematics" and option:
            option = option.lower()
        if option == "computer science":
            option = "Computer Science"
        elif option == "pure":
            option = "Pure"
        elif option == "statistics":
            option = "Statistics"

        if option and option.lower() == "computer science":
            option = "Computer Science" 

        if program and program.lower() == "industrial mathematics" and option is None:
            return {
                "response": "Please specify your option in Industrial Mathematics:",
                "buttons": [
                    {"label": "Pure", "value": "Pure"},
                    {"label": "Statistics", "value": "Statistics"},
                    { "label": "Computer Science (Maths)", "value": "Computer Science" }
                ]
        }
        
        response = get_response(text, program, level, option)
        
        # If response is a string, return it as plain text
        if isinstance(response, str):
            return jsonify({"response": response})
        # If response is a dict (with buttons), return as-is
        else:
            return jsonify(response)
            
    except Exception as e:
        return jsonify({"response": f"Error: {str(e)}"}), 500
    
if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0', port=5001)