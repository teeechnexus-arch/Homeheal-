from flask import Flask, render_template, request, jsonify, session
from datetime import timedelta
import os

app = Flask(__name__)
app.secret_key = "healhome_secret_key_2026"
app.permanent_session_lifetime = timedelta(hours=24)

# Create uploads folder if it doesn't exist
if not os.path.exists("uploads"):
    os.makedirs("uploads")

# Simple user database (in production, use a real database)
user_db = {
    "admin": "password123",
    "john": "john456",
    "sarah": "sarah789"
}

# Symptom → response database
symptom_db = {
    "fever": "You may have a fever. Take rest, drink fluids, and monitor temperature.",
    "cold": "Common cold detected. Warm fluids and rest are recommended.",
    "cough": "Cough symptoms detected. Avoid cold drinks and consult a doctor if severe.",
    "headache": "Headache detected. Could be stress or dehydration.",
    "stomach": "Stomach pain detected. Avoid oily food and drink water.",
    "pain": "Pain detected. Please specify the location for better guidance."
}

medicine_dosage = {
    "paracetamol": "500 mg – Twice a day after food",
    "crocin": "500 mg – Twice a day",
    "azithromycin": "500 mg – Once a day",
    "amoxicillin": "250 mg – Three times a day",
    "cetirizine": "10 mg – Once at night",
    "ibuprofen": "400 mg – Twice a day after meals"
}

# Medicine side effects and solutions
medicine_solutions = {
    "paracetamol": "• Take with food to avoid stomach upset\n• Stay hydrated\n• Monitor liver function if taken long-term",
    "crocin": "• Take with milk or antacid if stomach issues\n• Do not exceed 3g/day\n• Rest and stay warm",
    "azithromycin": "• Take on empty stomach for better absorption\n• Complete full course\n• May cause nausea - eat light meals",
    "amoxicillin": "• Take with food to prevent stomach upset\n• Complete full course\n• Report any allergic reactions",
    "cetirizine": "• May cause drowsiness - avoid driving\n• Take at night for best results\n• Drink plenty of water",
    "ibuprofen": "• Always take with food\n• Maximum 2400mg/day\n• Avoid if you have stomach ulcers"
}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    
    if username in user_db and user_db[username] == password:
        session["user"] = username
        return jsonify({"success": True, "message": f"Welcome {username}!"})
    else:
        return jsonify({"success": False, "message": "Invalid username or password!"})

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "").lower().strip()

    if not user_message:
        return jsonify({"reply": "Please tell me your symptoms."})

    for keyword, response in symptom_db.items():
        if keyword in user_message:
            return jsonify({
                "reply": f"I understand your concern. {response}"
            })

    return jsonify({
        "reply": "I could not clearly identify your symptoms. Please explain again or consult a doctor."
    })

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("file")
    if not file:
        return jsonify({"message": "No file uploaded", "solutions": ""})
    
    try:
        # Save the file
        filename = file.filename
        filepath = os.path.join("uploads", filename)
        file.save(filepath)
        
        # Analyze prescription file
        analysis_message = analyze_prescription(filename)
        solutions = get_prescription_solutions(filename)
        
        return jsonify({
            "message": f"✓ Prescription uploaded: {filename}\n{analysis_message}",
            "solutions": solutions
        })
    except Exception as e:
        return jsonify({"message": f"Error processing prescription: {str(e)}", "solutions": ""})

def analyze_prescription(filename):
    """Analyze prescription file and extract medicine information"""
    analysis = "📋 Prescription Analysis:\n"
    
    # Convert filename to lowercase for keyword matching
    file_lower = filename.lower()
    
    found_medicines = []
    for medicine in medicine_dosage.keys():
        if medicine in file_lower:
            found_medicines.append(medicine)
    
    if found_medicines:
        analysis += f"Detected medicines: {', '.join([m.capitalize() for m in found_medicines])}\n"
        analysis += f"For detailed dosage and precautions, refer to the medicine section."
    else:
        analysis += "Prescription file received. Unable to detect specific medicines from filename.\n"
        analysis += "Please ensure prescription file name includes medicine name for automatic detection."
    
    return analysis

def get_prescription_solutions(filename):
    """Get health solutions and precautions for detected medicines"""
    file_lower = filename.lower()
    solutions = "🏥 Health Solutions & Precautions:\n\n"
    
    found_medicines = []
    for medicine in medicine_dosage.keys():
        if medicine in file_lower:
            found_medicines.append(medicine)
    
    if found_medicines:
        for medicine in found_medicines:
            solutions += f"<b>{medicine.upper()}</b>\n"
            solutions += f"• Dosage: {medicine_dosage[medicine]}\n"
            solutions += f"• Precautions:\n{medicine_solutions[medicine]}\n\n"
    else:
        solutions = "💊 General Prescription Guidelines:\n"
        solutions += "1. Always take medicines with food unless advised otherwise\n"
        solutions += "2. Complete the full course even if you feel better\n"
        solutions += "3. Report any side effects to your doctor\n"
        solutions += "4. Keep medicines away from children\n"
        solutions += "5. Store at room temperature away from moisture"
    
    return solutions

@app.route("/set-reminder", methods=["POST"])
def set_reminder():
    data = request.get_json()
    medicine = data.get("medicine")
    time = data.get("time")

    dosage = medicine_dosage.get(medicine, "Follow doctor's prescription")

    return jsonify({
        "message": f"Reminder set for {medicine.capitalize()} at {time}",
        "dosage": dosage
    })

if __name__ == "__main__":
    app.run(debug=True)
