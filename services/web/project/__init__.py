import datetime
import uuid

from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy.sql import func, text


app = Flask(__name__)
app.config.from_object("project.config.Config")
db = SQLAlchemy(app)


class Income(db.Model):
    __tablename__ = "incomes"

    id = db.Column(db.Uuid, primary_key=True)
    name = db.Column(db.String, unique=False, nullable=False)
    value = db.Column(db.Integer, unique=False, nullable=False)
    event_at = db.Column(db.DateTime, unique=False, nullable=False)

    def __init__(self, name: str, value:int, event_at):
        self.id = uuid.uuid4()
        self.name = name
        self.value = value
        self.event_at = event_at


def get_total_value(from_at, to_at):
    query = text(
        """
            SELECT sum(value) AS total_value
            FROM incomes
            WHERE event_at >= :start_event_at
              AND event_at <= :end_event_at
        """
    )
    params = dict(
        start_event_at=from_at,
        end_event_at=to_at,
    )
    result = db.session.execute(query, params=params)
    total = result.all()
    return total[0][0]


@app.route('/', methods=['GET'])
def get_value_hanlder():
    from_at = request.args.get('from', datetime.datetime.now() - datetime.timedelta(days=1000))
    if not from_at:
        from_at = datetime.datetime.now() - datetime.timedelta(days=1000)

    to_at = request.args.get('to', datetime.datetime.now())
    if not to_at:
        to_at = datetime.datetime.now()

    total_value = get_total_value(from_at, to_at)
    return render_template('index.html', total_income=f'{total_value}')


@app.route('/', methods=['POST'])
def submit_handler():
    name = request.form['name']
    value = int(request.form['value'])
    event_at = request.form['event_at']
    db.session.add(Income(name=name, value=value, event_at=event_at))
    db.session.commit()
    return get_value_hanlder()
