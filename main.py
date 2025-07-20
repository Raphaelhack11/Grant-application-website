from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///grants.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class GrantRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contact = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    method = db.Column(db.String(50), nullable=False)
    approved = db.Column(db.Boolean, default=False)

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/apply', methods=['POST'])
def apply():
    contact = request.form['contact']
    amount = request.form['amount']
    method = request.form['method']
    new_request = GrantRequest(contact=contact, amount=amount, method=method)
    db.session.add(new_request)
    db.session.commit()
    return redirect(url_for('thank_you'))

@app.route('/admin')
def admin():
    requests = GrantRequest.query.all()
    return render_template('admin.html', requests=requests)

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
