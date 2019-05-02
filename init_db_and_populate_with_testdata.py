from app import db, User, Customer, Agent, Message

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
