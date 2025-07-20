from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from email_validator import validate_email, EmailNotValidError

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///grants.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class GrantRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    reason = db.Column(db.Text)
    approved = db.Column(db.Boolean, default=False)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    contact = request.form['contact']
    amount = request.form['amount']

    name = contact  # assuming contact = name or email
    email = contact
    reason = f"Requested Grant Amount: ${amount}"

    try:
        validate_email(email)
    except EmailNotValidError:
        flash('Invalid email address.', 'error')
        return redirect(url_for('index'))

    existing_user = GrantRequest.query.filter_by(email=email).first()
    if existing_user:
        flash('Email already submitted.', 'error')
        return redirect(url_for('index'))

    grant = GrantRequest(name=name, email=email, reason=reason)
    db.session.add(grant)
    db.session.commit()
    return redirect(url_for('thank_you'))

@app.route('/admin')
def admin():
    grants = GrantRequest.query.all()
    return render_template('admin.html', grants=grants)

@app.route('/approve/<int:id>')
def approve(id):
    grant = GrantRequest.query.get_or_404(id)
    grant.approved = True
    db.session.commit()
    flash('User approved. Please send email manually.')
    return redirect(url_for('admin'))

@app.route('/thank-you')
def thank_you():
    return render_template('thank_you.html')

if __name__ == '__main__':
    app.run(debug=True)
