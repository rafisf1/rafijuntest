from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Alumni(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    graduation_year = db.Column(db.Integer)
    major = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)
    linkedin_url = db.Column(db.String(200))
    current_company = db.Column(db.String(100))
    current_position = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    def __repr__(self):
        return f'<Alumni {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'graduation_year': self.graduation_year,
            'major': self.major,
            'email': self.email,
            'linkedin_url': self.linkedin_url,
            'current_company': self.current_company,
            'current_position': self.current_position
        } 