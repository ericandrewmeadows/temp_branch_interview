from flask import (
    Flask,
    render_template,
    abort,
    request,
    flash,
    session,
    redirect,
    url_for,
)
from flask_sqlalchemy import SQLAlchemy

from datetime import datetime

from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    created_at = db.Column(db.DateTime(timezone=True), index=True,
                           default=datetime.utcnow)
    modified_at = db.Column(db.DateTime(timezone=True), index=True,
                            default=datetime.utcnow, onupdate=datetime.utcnow)
    discriminator = db.Column('type', db.String(50))
    __mapper_args__ = {'polymorphic_on': discriminator}


class Customer(User):
    __tablename__ = 'customer'
    __mapper_args__ = {'polymorphic_identity': 'customer'}
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)

    def __repr__(self):
        return '<Customer %r>' % self.name


class Agent(User):
    __tablename__ = 'agent'
    __mapper_args__ = {'polymorphic_identity': 'agent'}
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)

    def __repr__(self):
        return '<Agent %r>' % self.name


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Every message is associated with a single customer.
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'),
                            nullable=False)
    customer = db.relationship('Customer',
        backref=db.backref('messages', lazy=True))

    # This is only set if the message was sent by the agent. For messages sent
    # by the customer, it is NULL.
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.id'), nullable=True)
    agent = db.relationship('Agent',
                            backref=db.backref('messages', lazy=True))


    body = db.Column(db.String, nullable=False)

    created_at = db.Column(db.DateTime(timezone=True), index=True,
                           default=datetime.utcnow)
    modified_at = db.Column(db.DateTime(timezone=True), index=True,
                            default=datetime.utcnow, onupdate=datetime.utcnow)


import enum
class TicketStatus(enum.Enum):
    opened = 1
    in_progress = 2
    closed = 3


class IssueTicket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticket_status = db.Column(db.Enum(TicketStatus))
    summary = db.Column(db.String(100), nullable=False)
    details = db.Column(db.String(), nullable=False)

    customer_id = db.Column(
        db.Integer, db.ForeignKey('customer.id'), nullable=False)
    customer = db.relationship('Customer',
        backref=db.backref('tickets', lazy=True), foreign_keys=[customer_id])

    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_by_user = db.relationship('User',
        backref=db.backref('tickets_created_by', lazy=True), foreign_keys=[created_by])

    created_at = db.Column(db.DateTime(timezone=True), index=True,
                           default=datetime.utcnow)
    modified_at = db.Column(db.DateTime(timezone=True), index=True,
                            default=datetime.utcnow, onupdate=datetime.utcnow)


@app.route('/')
def index():
    return 'Hello World'


@app.route('/login', methods=['GET', 'POST'])
def login():
    agents = Agent.query.all()

    if request.method == 'POST':
        # TODO (Eric):  switch from agent_id to user_id and then if statement
        # for redirect to user or agent pages
        session['user_id'] = request.form['agent_id']
        return redirect(url_for('view_customers'))
    return render_template('login.html', agents=agents)


@app.route('/customer_test', methods=['GET', 'POST'])
def customer_test():
    customers = Customer.query.all()

    if request.method == 'POST':
        msg_body = request.form.get('message')
        customer_id = int(request.form.get('customer_id', 0))
        customer_name = request.form.get('customer_name')

        if customer_id:
            customer = Customer.query.get(customer_id)
        else:
            customer = Customer(name=customer_name)
            db.session.add(customer)

        msg = Message(customer=customer, body=msg_body)
        db.session.add(msg)
        db.session.commit()
        flash('Sent message "%s" for customer %s (id %d)' % (
            msg_body, customer.name, customer.id))

    return render_template('customer_test.html', customers=customers)


@app.route('/admin/customers')
def view_customers():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    customers = Customer.query.all()
    agent = Agent.query.get(user_id)
    return render_template('customers.html', customers=customers)

@app.route('/admin/customer/<int:id>', methods=['GET', 'POST'])
def view_customer(id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    customer = Customer.query.get(id)
    agent = Agent.query.get(user_id)

    if request.method == 'POST':
        msg_body = request.form.get('message')
        agent_id = int(request.form.get('agent'))
        agent = Agent.query.get(agent_id)
        msg = Message(customer=customer, agent=agent, body=msg_body)
        db.session.add(msg)
        db.session.commit()


    return render_template('agent_to_customer_messaging.html', customer=customer,
                           agent=agent)

@app.route('/admin/customer/create_ticket', methods=['POST'])
def create_ticket():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    customer_id = request.form.get('customer_id')
    summary = request.form.get('summary')
    details = request.form.get('details')

    ticket = IssueTicket(
        ticket_status="opened",
        summary=summary,
        details=details,
        customer_id=customer_id,
        created_by=user_id
    )
    db.session.add(ticket)
    db.session.commit()

    tickets = IssueTicket.query.all()

    return redirect(url_for('view_customer', id=customer_id))
