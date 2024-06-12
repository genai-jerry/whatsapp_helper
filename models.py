from flask_sqlalchemy import SQLAlchemy
from app import db

class AlembicVersion(db.Model):
    __tablename__ = 'alembic_version'

    version_num = db.Column(db.String(32), primary_key=True)


class Instances(db.Model):
    __tablename__ = 'instances'

    id = db.Column(db.Integer, primary_key=True)
    mobile_number = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    sms_idea_api_key = db.Column(db.String(50), nullable=False)


class LeadCallStatus(db.Model):
    __tablename__ = 'lead_call_status'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    color_code = db.Column(db.String(25))
    text_color = db.Column(db.String(25))

class LeadCommunication(db.Model):
    __tablename__ = 'lead_communication'

    id = db.Column(db.BigInteger, primary_key=True)
    template_id = db.Column(db.Integer, db.ForeignKey('templates.id'))
    sent_date = db.Column(db.DateTime, server_default=db.func.now())
    template_name = db.Column(db.String(255))


class Messages(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(10), nullable=False)
    sender = db.Column(db.String(20), nullable=False)
    receiver = db.Column(db.String(20), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('opportunity.id'))
    message = db.Column(db.Text, nullable=False)
    template = db.Column(db.String(255))
    status = db.Column(db.String(10), nullable=False)
    error_message = db.Column(db.String(255))
    create_time = db.Column(db.DateTime, server_default=db.func.now())
    update_time = db.Column(db.DateTime)


class Opportunity(db.Model):
    __tablename__ = 'opportunity'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    phone = db.Column(db.String(15), nullable=False, unique=True)
    comment = db.Column(db.String(250))
    ad_name = db.Column(db.String(250))
    ad_id = db.Column(db.String(250))
    ad_fbp = db.Column(db.String(500))
    ad_fbc = db.Column(db.String(500))
    medium = db.Column(db.String(250))
    gender = db.Column(db.String(10), nullable=True)
    register_time = db.Column(db.DateTime, nullable=False)
    reregister_time = db.Column(db.DateTime, nullable=True)
    opportunity_status = db.Column(db.Integer, db.ForeignKey('opportunity_status.id'))
    call_status = db.Column(db.Integer, db.ForeignKey('lead_call_status.id'))
    sales_agent = db.Column(db.Integer, db.ForeignKey('sales_agent.id'))
    company_type = db.Column(db.Integer, db.ForeignKey('company_type.id'))
    challenge_type = db.Column(db.Integer, db.ForeignKey('challenge_type.id'))
    sales_date = db.Column(db.DateTime)  # New column

class CompanyType(db.Model):
    __tablename__ = 'company_type'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

class ChallengeType(db.Model):
    __tablename__ = 'challenge_type'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

class OpportunityStatus(db.Model):
    __tablename__ = 'opportunity_status'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    color_code = db.Column(db.String(25))
    text_color = db.Column(db.String(25))

class SalesAgent(db.Model):
    __tablename__ = 'sales_agent'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    color_code = db.Column(db.String(25))
    text_color = db.Column(db.String(25))

class Templates(db.Model):
    __tablename__ = 'templates'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    active = db.Column(db.Boolean, nullable=False)
    template_text = db.Column(db.Text)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime)

class ApiKey(db.Model):
    __tablename__ = 'api_key'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(64), index=True, unique=True)

class Appointment(db.Model):
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    telephone = db.Column(db.String(15), nullable=False)
    career_challenge = db.Column(db.String(255), nullable=False)
    challenge_description = db.Column(db.Text, nullable=False)
    urgency = db.Column(db.String(255), nullable=False)
    salary_range = db.Column(db.String(255), nullable=False)
    expected_salary = db.Column(db.String(255), nullable=False)
    current_employer = db.Column(db.String(255), nullable=False)
    financial_situation = db.Column(db.String(255), nullable=False)
    grade = db.Column(db.String(255), nullable=False)
    mentor_id = db.Column(db.Integer, db.ForeignKey('sales_agent.id'))
    opportunity_id = db.Column(db.Integer, db.ForeignKey('opportunity.id'))
    appointment_time = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    verified = db.Column(db.Boolean, nullable=False)
    conflicted = db.Column(db.Boolean, nullable=True)
    canceled = db.Column(db.Boolean, nullable=True)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    

class MaxScore(db.Model):
    __tablename__ = 'max_scores'

    id = db.Column(db.Integer, primary_key=True)
    score_name = db.Column(db.String(255))
    score_value = db.Column(db.Integer)
    category = db.Column(db.String(255), nullable=False)

class Config(db.Model):
    __tablename__ = 'configs'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    value = db.Column(db.String(255), nullable=False)