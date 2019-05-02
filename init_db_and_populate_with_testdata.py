from app import db, User, Customer, Agent, Message, IssueTicket

db.drop_all()
db.create_all()

customer_names = [
    'Joe',
    'John',
    'Frank'
]

customers = []
for name in customer_names:
    customer = Customer(name=name)
    db.session.add(customer)
    customers.append(customer)
db.session.commit()

agent_names = [
    'Ben',
    'Mike'
]

agents = []
for name in agent_names:
    agent = Agent(name=name)
    db.session.add(agent)
    agents.append(agent)
db.session.commit()

tickets = [
    ("opened", customers[0].id, agents[0].id, "Test Opened"),
    ("in_progress", customers[0].id, agents[0].id, "Test In Progress"),
    ("closed", customers[0].id, agents[0].id, "Test Closed"),
]
created_tickets = []
for ticket in tickets:
    issue_ticket = IssueTicket(
        ticket_status=ticket[0],
        customer_id=ticket[1],
        created_by=ticket[2],
        summary="Test",
        details=ticket[3]
    )
    db.session.add(issue_ticket)
    created_tickets.append(issue_ticket)
    print(issue_ticket)
db.session.commit()


threads = [
    [
        'Hello, I need help',
        'How can I help you?',
        'I need a loan'
    ],
    [
        'I\'m just spamming'
    ]
]
for thread_idx, thread in enumerate(threads):
    print(thread)
    # Pick customers and agents in a round robin fashion
    customer = customers[thread_idx % len(customers)]
    agent = agents[thread_idx % len(agents)]
    print(customer)
    print(agent)
    for msg_idx, msg_body in enumerate(thread):
        # Every other message is by an agent. If the message is by a customer,
        # the agent reference is set to None
        msg = Message(customer=customer,
                      agent=agent if msg_idx % 2 == 1 else None,
                      body=msg_body)
        db.session.add(msg)

db.session.commit()
