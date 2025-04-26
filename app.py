from flask import Flask, render_template, request, flash, redirect, url_for
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename
from model import GlaucomaModel
import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
# Load environment variables from .env
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Secret key for sessions (flash messages)
app.secret_key = os.getenv('SECRET_KEY') or 'super-secret-key-12345'

# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('EMAIL_USER')
app.config['MAIL_PASSWORD'] = os.getenv('EMAIL_PASS')

mail = Mail(app)

# Initialize Glaucoma Model (lazy loaded)
glaucoma_model = None

def get_model():
    global glaucoma_model
    if glaucoma_model is None:
        glaucoma_model = GlaucomaModel('glaucoma_model.h5')
    return glaucoma_model

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/project')
def project():
    return render_template('project.html')

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        if 'eye_image' not in request.files:
            flash('No file uploaded', 'error')
            return redirect(request.url)
        
        file = request.files['eye_image']
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)
        
        if file:
            try:
                model = get_model()
                img_bytes = file.read()
                probability = model.predict(img_bytes)
                
                result = "Positive" if probability > 0.5 else "Negative"
                confidence = probability if result == "Positive" else 1 - probability
                
                return render_template('predict.html', 
                                    result=result,
                                    confidence=f"{confidence*100:.2f}%",
                                    show_result=True)
            except Exception as e:
                app.logger.error(f"Prediction error: {str(e)}")
                flash('Error processing image. Please try another.', 'error')
    
    return render_template('predict.html', show_result=False)
@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        message = request.form["message"]

        # Compose the email
        subject = "New Contact Form Submission"
        body = f"Name: {name}\nEmail: {email}\nMessage: {message}"
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = "your_email@example.com"
        msg["To"] = "your_email@example.com"  # Your receiving email

        try:
            # SMTP configuration
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login("your_email@example.com", "your_app_password")
                server.send_message(msg)

            flash("Message sent successfully!", "success")
        except Exception as e:
            flash(f"Failed to send message. Error: {e}", "danger")

    return render_template("contact.html")

if __name__ == '__main__':
    app.run(debug=True)