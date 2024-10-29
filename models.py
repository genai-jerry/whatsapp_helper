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
    comment = db.Column(db.Text, nullable=True)
    ad_name = db.Column(db.String(250))
    ad_id = db.Column(db.String(250))
    ad_fbp = db.Column(db.String(500))
    ad_fbc = db.Column(db.String(500))
    ad_placement = db.Column(db.String(250))
    ad_account = db.Column(db.String(250))
    medium = db.Column(db.String(250))
    lead_event_fired = db.Column(db.Boolean, nullable=True)
    submit_application_event_fired = db.Column(db.Boolean, nullable=True)
    sale_event_fired = db.Column(db.Boolean, nullable=True)
    video_watched = db.Column(db.Boolean, nullable=False, default=False)
    gender = db.Column(db.String(10), nullable=True)
    register_time = db.Column(db.DateTime, nullable=False)
    last_register_time = db.Column(db.DateTime, nullable=True)
    address = db.Column(db.String(500), nullable=True)
    same_state = db.Column(db.Boolean, nullable=True)
    gst = db.Column(db.String(50), nullable=True)
    opportunity_status = db.Column(db.Integer, db.ForeignKey('opportunity_status.id'))
    call_status = db.Column(db.Integer, db.ForeignKey('lead_call_status.id'))
    call_setter = db.Column(db.Integer, db.ForeignKey('sales_agent.id'))
    optin_caller = db.Column(db.Integer, db.ForeignKey('sales_agent.id'))
    company_type = db.Column(db.Integer, db.ForeignKey('company_type.id'))
    challenge_type = db.Column(db.Integer, db.ForeignKey('challenge_type.id'))
    assigned_to = db.Column(db.Integer, db.ForeignKey('sales_agent.id'), nullable=True)
    last_updated = db.Column(db.DateTime, nullable=True)
    last_updated_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

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
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

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
    name = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime)

class UserRole(db.Model):
    __tablename__ = 'user_role'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), Primary_key=True)

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)

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
    appointment_number = db.Column(db.String(15), nullable=False)
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
    is_initial_discussion = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    verified = db.Column(db.Boolean, nullable=False)
    conflicted = db.Column(db.Boolean, nullable=True)
    canceled = db.Column(db.Boolean, nullable=True)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    status = db.Column(db.Integer, db.ForeignKey('opportunity_status.id'), nullable=True)
    

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

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    currency = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

class Sale(db.Model):
    __tablename__ = 'sale'
    
    id = db.Column(db.Integer, primary_key=True)
    sale_value = db.Column(db.Integer, nullable=False)
    total_paid = db.Column(db.Integer, nullable=False)
    currency = db.Column(db.String(255), nullable=True)
    note = db.Column(db.String(255), nullable=True)
    sale_date = db.Column(db.DateTime)
    is_final = db.Column(db.Boolean, nullable=False, default=False)
    opportunity_id = db.Column(db.Integer, db.ForeignKey('opportunity.id'))
    sales_agent = db.Column(db.Integer, db.ForeignKey('sales_agent.id'))
    call_setter = db.Column(db.Integer, db.ForeignKey('sales_agent.id'))
    product = db.Column(db.Integer, db.ForeignKey('products.id'))
    cancelled = db.Column(db.Boolean, nullable=False, default=False)
    
class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    payor_email = db.Column(db.String(255), nullable=False)
    payor_phone = db.Column(db.String(255), nullable=False)
    payment_value = db.Column(db.Integer, nullable=False)
    charges = db.Column(db.Integer, nullable=False)
    payment_mode_reference = db.Column(db.String(255), nullable=True)
    currency = db.Column(db.String(255), nullable=True)
    payment_date = db.Column(db.DateTime, nullable=False)
    is_deposit = db.Column(db.Boolean, nullable=False, default=False)
    invoice_link = db.Column(db.String(255), nullable=True)
    sale = db.Column(db.Integer, db.ForeignKey('sale.id'))
    opportunity = db.Column(db.Integer, db.ForeignKey('opportunity.id'))
    accountant = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    payment_mode = db.Column(db.Integer, db.ForeignKey('payment_mode.id'))
    payment_method = db.Column(db.String(255), nullable=True)
    refunded = db.Column(db.Boolean, nullable=False, default=False)

class PaymentMode(db.Model):
    __tablename__ = 'payment_mode'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=True)

class PaymentDue(db.Model):
    __tablename__ = 'payment_due'
    
    id = db.Column(db.Integer, primary_key=True)
    payment_value = db.Column(db.Integer, nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)
    sale_id = db.Column(db.Integer, db.ForeignKey('sale.id'))
    paid = db.Column(db.Boolean, nullable=False, default=False)
    cancelled = db.Column(db.Boolean, nullable=False, default=False)

class Task(db.Model):
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    due_date = db.Column(db.DateTime, nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    last_updated = db.Column(db.DateTime, nullable=True)
    opportunity_id = db.Column(db.Integer, db.ForeignKey('opportunity.id'), nullable=True)

class Comment(db.Model):
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    opportunity_id = db.Column(db.Integer, db.ForeignKey('opportunity.id'), nullable=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=True)

class Win(db.Model):
    __tablename__ = 'wins'
    
    id = db.Column(db.Integer, primary_key=True)
    win_type = db.Column(db.Integer, db.ForeignKey('win_types.id'), nullable=True)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class WinType(db.Model):
    __tablename__ = 'win_types'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    
class Employee(db.Model):
    __tablename__ = 'employees'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    email = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(255), nullable=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))

class Department(db.Model):
    __tablename__ = 'departments'
    
    id = db.Column(db.Integer, primary_key=True)
    department_key = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    active = db.Column(db.Boolean, nullable=False, default=True)


class SalesProjections(db.Model):
    __tablename__ = 'sales_projections'
    
    id = db.Column(db.Integer, primary_key=True)
    month = db.Column(db.String(50), nullable=False)
    year = db.Column(db.String(50), nullable=False)
    sale_price = db.Column(db.Integer, nullable=False)
    total_call_slots = db.Column(db.Integer, nullable=False)
    closure_percentage_goal = db.Column(db.Integer, nullable=False)
    closure_percentage_projected = db.Column(db.Integer, nullable=False)
    sales_value_projected = db.Column(db.Integer, nullable=False, default=0)
    sales_value_goal = db.Column(db.Integer, nullable=False, default=0)
    actual_sales_value = db.Column(db.Integer, nullable=False, default=0)
    total_calls_made = db.Column(db.Integer, nullable=False, default=0)
    total_calls_scheduled = db.Column(db.Integer, nullable=False, default=0)
    total_sales_closed = db.Column(db.Integer, nullable=False, default=0)
    total_deposits_collected = db.Column(db.Integer, nullable=False, default=0)
    commission_percentage = db.Column(db.Integer, nullable=False, default=0)
    sales_agent_id = db.Column(db.Integer, db.ForeignKey('sales_agent.id'))

class SalesProjectionConfig(db.Model):
    __tablename__ = 'sales_projection_config'
    
    id = db.Column(db.Integer, primary_key=True)
    cost_per_lead = db.Column(db.Integer, nullable=False)
    sale_price = db.Column(db.Integer, nullable=False)
    show_up_rate_goal = db.Column(db.Integer, nullable=False)
    show_up_rate_projection = db.Column(db.Integer, nullable=False)
    appointment_booked_goal = db.Column(db.Integer, nullable=False)
    appointment_booked_projection = db.Column(db.Integer, nullable=False)
    month = db.Column(db.String(50), nullable=False)
    year = db.Column(db.String(50), nullable=False)
    marketing_spend = db.Column(db.Integer, nullable=True, default=0)
    marketing_spend_updated_at = db.Column(db.DateTime, nullable=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))

class FacebookAdAccount(db.Model):
    __tablename__ = 'facebook_ad_accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    ad_account_id = db.Column(db.String(255), nullable=False)
    ad_account_name = db.Column(db.String(255), nullable=False)
    ad_account_access_token = db.Column(db.String(255), nullable=False)
    ad_account_currency = db.Column(db.String(255), nullable=False)
    app_id = db.Column(db.String(255), nullable=False)
    app_secret = db.Column(db.String(255), nullable=False)
    last_updated = db.Column(db.DateTime, nullable=True)