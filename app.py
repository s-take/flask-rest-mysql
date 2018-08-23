import json
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from os import environ

# Flask本体
api = Flask(__name__)
api.config['SQLALCHEMY_DATABASE_URI'] = environ['MYSQL_URL']
api.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# SQLAlchemyの初期化
db = SQLAlchemy(api)

# Userスキーマの定義
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False)

    def __init__(self,name,email):
        self.value = name
        self.email = email

    def __repr__(self):
        return '<User {}>'.format(self.name)

def createUser(name,email):
    create_user = User(name,email)
    db.session.add(create_user) 
    try: 
        db.session.commit()
        return create_user
    except:  
        print("this user is already registered user.")
        return {"error": "this user is already registered user."}

def deleteUser(user_id):
    try:
        user = db.session.query(User).filter_by(id=user_id).first()
        db.session.delete(user)
        db.session.commit()
        return user
    except:
        db.session.rollback()
        print("failed to delete this user.")
        return {"error": "failed to delete this user."}

def updateUser(user_id,name,email):
    try:
        user = db.session.query(User).filter_by(id=user_id).first()
        user.name = name
        user.email = email
        db.session.add(user)
        db.session.commit()
        return user
    except:
        db.session.rollback()
        print("failed to update this user.")
        return {"error": "failed to update this user."}

def getUser():
    return User.query.all()

@api.route('/api')
def api_index():
            return jsonify({'message': "This is the User api."})

@api.route('/api/users', methods=['GET'])
def users():
    users = []
    for user in getUser():
        user = {"id": user.id, "name": user.name,"email": user.email}
        users.append(user)

    return jsonify({"users":users})

@api.route('/api/users', methods=['POST'])
def create():
    name = request.json["name"]
    email = request.json["email"]
    create_user = createUser(name,email)
    if isinstance(create_user,dict):
        return jsonify({"error": create_user["error"]})
    else:
        return jsonify({"created_user": create_user.name})

@api.route('/api/users/<int:user_id>',methods=['PUT'])
def update_email(user_id):
    name = request.json["name"]
    email = request.json["email"]
    update_user = updateUser(user_id,name,email)
    if isinstance(update_user,dict):
        return jsonify({"error": update_user["error"]})
    else:
        return jsonify({"updated_user": update_user.name})

@api.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete(user_id):
    delete_user = deleteUser(user_id)
    if isinstance(delete_user,dict):
        return jsonify({"error": delete_user["error"]})
    else:
        return jsonify({"deleted_user": delete_user.name})

@api.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'})

if __name__ == '__main__':
    db.drop_all()
    db.create_all()
    api.run(host='0.0.0.0', port=5000)
