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


class LeadCallStatus(db.Model):
    __tablename__ = 'lead_call_status'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    color_code = db.Column(db.String(25))


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
    register_time = db.Column(db.DateTime, nullable=False)
    opportunity_status = db.Column(db.Integer, db.ForeignKey('opportunity_status.id'))
    call_status = db.Column(db.Integer, db.ForeignKey('lead_call_status.id'))
    sales_agent = db.Column(db.Integer, db.ForeignKey('sales_agent.id'))
    sales_date = db.Column(db.DateTime)  # New column


class OpportunityStatus(db.Model):
    __tablename__ = 'opportunity_status'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    color_code = db.Column(db.String(25))


class SalesAgent(db.Model):
    __tablename__ = 'sales_agent'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    color_code = db.Column(db.String(25))


class Templates(db.Model):
    __tablename__ = 'templates'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    active = db.Column(db.Boolean, nullable=False)
    template_text = db.Column(db.Text)