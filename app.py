from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy as sa
import sqlalchemy.orm as so
from sqlalchemy import asc
import os

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
db = SQLAlchemy(app)

class Score(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    time: so.Mapped[float] = so.mapped_column(sa.Float, index=True)
    def __init__(self, p_name, p_score):
        self.name = p_name
        self.time = p_score
    def __repr__(self):
        return '<User {}><Score {}>'.format(self.username, self.time)

@app.route('/')
@app.route('/index')
def index():
    #go to the score table and query it, order it by the score value descending, limit 5 and serve up all of those items I asked for as a list.
	results = Score.query.order_by(asc('time')).all()
	scores = []
	
	for i, result in enumerate(results):
		score_dict = {'place': str(i + 1), 'name':result.name, 'time':result.time}
		scores.append(score_dict)

	return render_template('index.html', scores = scores)

@app.route('/score', methods=['POST'])
def submit_score():
    json = request.get_json()
    name = json["name"]
    time = json["time"]
    if Score.query.filter_by(name=name).first() != None:
        Score.query.filter_by(name=name).first().time = time
        db.session.commit()
    else:
        new_score = Score(name, time)
        db.session.add(new_score)
        db.session.commit()
    place = Score.query.filter_by(name=name).first()
    return jsonify({"place": place.id})

@app.route('/leaderboard', methods=['GET'])
def get_top_five():
    leaders = Score.query.order_by(asc('time')).all()
    scores = []
    for leader in leaders:
        scores.append({"name": leader.name, "time": leader.time})
    return jsonify(scores)