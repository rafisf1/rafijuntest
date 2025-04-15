from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
import os
import logging
from datetime import datetime
from models import db, Alumni
import csv
from io import StringIO

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Use environment variable for database URL with a fallback
database_url = os.getenv('DATABASE_URL', 'sqlite:///alumni.db')
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev')

db.init_app(app)

@app.route('/')
def home():
    try:
        logger.debug("Accessing home route")
        alumni = Alumni.query.all()
        logger.debug(f"Found {len(alumni)} alumni records")
        return render_template('index.html', alumni=alumni)
    except Exception as e:
        logger.error(f"Error in home route: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            data = request.get_json()
            new_alumni = Alumni(
                name=data['name'],
                graduation_year=data['graduationYear'],
                major=data['major'],
                email=data['email'],
                linkedin_url=data.get('linkedinUrl'),
                current_company=data.get('currentCompany'),
                current_position=data.get('currentPosition')
            )
            db.session.add(new_alumni)
            db.session.commit()
            return jsonify({"message": "Registration successful"}), 201
        except Exception as e:
            logging.error(f"Error in register route: {str(e)}")
            return jsonify({"error": str(e)}), 400
    return render_template('register.html')

@app.route('/admin')
def admin():
    try:
        alumni = Alumni.query.all()
        return render_template('admin.html', alumni=alumni)
    except Exception as e:
        logging.error(f"Error in admin route: {str(e)}")
        return "An error occurred", 500

@app.route('/api/export-csv')
def export_csv():
    try:
        si = StringIO()
        cw = csv.writer(si)
        cw.writerow(['Name', 'Graduation Year', 'Major', 'Email', 'LinkedIn URL', 'Current Company', 'Current Position'])
        
        alumni = Alumni.query.all()
        for alum in alumni:
            cw.writerow([
                alum.name,
                alum.graduation_year,
                alum.major,
                alum.email,
                alum.linkedin_url,
                alum.current_company,
                alum.current_position
            ])
        
        output = si.getvalue()
        si.close()
        
        return output, 200, {
            'Content-Type': 'text/csv',
            'Content-Disposition': 'attachment; filename=alumni.csv'
        }
    except Exception as e:
        logging.error(f"Error exporting CSV: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/import-csv', methods=['POST'])
def import_csv():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not file.filename.endswith('.csv'):
            return jsonify({"error": "File must be a CSV"}), 400
        
        stream = StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_input = csv.DictReader(stream)
        
        records_added = 0
        for row in csv_input:
            alumni = Alumni(
                name=row['Name'],
                graduation_year=int(row['Graduation Year']) if row['Graduation Year'] else None,
                major=row['Major'],
                email=row['Email'],
                linkedin_url=row['LinkedIn URL'],
                current_company=row['Current Company'],
                current_position=row['Current Position']
            )
            db.session.add(alumni)
            records_added += 1
        
        db.session.commit()
        return jsonify({"message": f"Successfully imported {records_added} records"}), 200
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error importing CSV: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.before_first_request
def initialize_database():
    try:
        logger.debug("Initializing database")
        db.create_all()
        logger.debug("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}", exc_info=True)
        raise

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='127.0.0.1', port=3000, debug=True) 