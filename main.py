from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy,query
from flask_marshmallow import Marshmallow
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from sqlalchemy import update
import os

# Init App
app = Flask(__name__)
app.app_context().push()
basedir = os.path.abspath(os.path.dirname(__file__))

# Database Config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'user.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Init db
db = SQLAlchemy(app)

# Init marshmallow
ma = Marshmallow(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    password = db.Column(db.String)
    email = db.Column(db.String, unique=True)
    groups = db.relationship('Group', backref='creator')

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'username': self.username,
            'password': self.password,
            'email': self.email
        }

    def __int__(self, username = username, password= password, email=  email):
        self.username = username
        self.password = password
        self.email = email


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, db.ForeignKey('user.username'))
    groupName = db.Column(db.String)
    members =db.relationship('Member', backref='group')

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'username': self.username,
            'groupName': self.groupName,
        }

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    groupName = db.Column(db.String, db.ForeignKey('group.groupName'))
    member = db.Column(db.String)
    transaction = db.Column(db.Text)
    paidBy = db.Column(db.Integer)
    money = db.Column(db.Integer)
    settle = db.Column(db.Integer)


    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'groupName': self.groupName,
            'member': self.member,
            'transaction': self.transaction,
            'username': self.username,
            'money': self.money,
            'settle':self.settle,
            'paidBy':self.paidBy
        }



# User Schema
class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'username', 'password', 'email')


# init Schema
user_schema = UserSchema()
users_schema = UserSchema(many=True)


@app.route('/signup', methods=['POST'])
def signup():
    if request.method == 'POST':
        username = request.json['username']
        password = request.json['password']
        email = request.json['email']

        new_user = User(username=username,password= password,email= email)
        db.session.add(new_user)
        db.session.commit()
        return user_schema.jsonify(new_user)



@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        username = request.json['username']
        password = request.json['password']
        email = request.json['email']
        user = db.session.query(User).filter_by(username = username , password = password , email = email).first()
        return jsonify( user = user.serialize)


@app.route('/group', methods=['POST'])
def create_group():
    user = request.get_json()
    name = user['username']
    grpname = user['groupName']
    crea = db.session.query(User).filter(User.username == name).first()
    group = Group(groupName=grpname, creator=crea)
    db.session.add(group)
    db.session.commit()
    print(user)
    que = db.session.query(Group).filter(Group.username == name).all()
    return jsonify(group=[i.serialize for i in que])

@app.route('/getGroups', methods=['POST'])
def getGroup():
    user = request.get_json()
    name = user['username']
    que = db.session.query(Group).filter(Group.username == name).all()
    return jsonify(group=[i.serialize for i in que])

@app.route('/addMember', methods=['POST'])
def addMember():
    name = request.get_json()
    uName = name['uname']
    gName = name['gname']
    mname = name['mname']
    member = Member(groupName=gName, member=mname , username=uName)
    db.session.add(member)
    db.session.commit()
    que = db.session.query(Member).filter(Member.member == mname).all()
    return jsonify(member=[i.serialize for i in que])

@app.route('/getMember' , methods=['POST'])
def getMember():
    name = request.get_json()
    gName = name['gname']
    uName = name['uname']
    que = db.session.query(Member).filter(Member.groupName == gName , Member.username == uName).all()
    return jsonify(member=[i.serialize for i in que])

@app.route('/addTransaction' , methods=['POST'])
def addTransaction():
    data = request.get_json()
    uName = data['uname']
    gName = data['gname']
    member = data['member']
    transaction = data['transaction']
    money = data['money']
    paidBy = data['paidBy']
    txn = Member(username = uName ,groupName= gName ,member = member ,  transaction = transaction , paidBy = paidBy, money= money, settle=0 )
    db.session.add(txn)
    db.session.commit()
    que = db.session.query(Member).all()
    return jsonify(member=[i.serialize for i in que])

@app.route('/getTransaction' , methods=['POST'])
def getTransaction():
    data = request.get_json()
    uName = data['uname']
    gName = data['gname']
    que = db.session.query(Member).filter(Member.paidBy == '1' , Member.username == uName , Member.groupName == gName)
    return jsonify(member=[i.serialize for i in que])


@app.route('/getExpense' , methods = ['POST'])
def getExpense():
    data = request.get_json()
    uName = data['uname']
    gName = data['gname']
    tName = data['transaction']
    que = db.session.query(Member).filter(Member.transaction == tName , Member.username == uName , Member.groupName == gName)
    return jsonify(member=[i.serialize for i in que])


@app.route('/update' , methods=['PUT'])
def updated():
    data = request.get_json()
    uName = data['uname']
    gName = data['gname']
    mName = data['member']
    tName = data['transaction']
    udt = Member.query.filter(Member.member == mName , Member.groupName == gName , Member.transaction == tName, Member.username == uName).first()
    udt.settle = 1
    db.session.commit()
    return jsonify(udt.serialize)







if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)