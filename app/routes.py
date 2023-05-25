from app import app
from .models import User, PokeHash, Lukemon, PostFight
from flask import jsonify, request
from werkzeug.security import check_password_hash
from flask_jwt_extended import create_access_token, get_jwt_identity, unset_jwt_cookies, jwt_required

@app.route('/token', methods=['POST'])
def create_token():
    email = request.json.get('email', None)
    password = request.json.get('password', None)
    queried_user = User.query.filter_by(email=email).first()
    if queried_user and check_password_hash(queried_user.password, password):
        access_token = create_access_token(identity=email, fresh=True)
        response = jsonify(access_token=access_token)
        return response
    return {'msg': 'Wrong email or password'}, 401

@app.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    response = jsonify({'msg': 'logout successful'})
    unset_jwt_cookies(response)
    return response

@app.route('/register', methods=['POST'])
def register():
    new_user_data = {
        'img_url': request.json.get('url',None),
        'email': request.json.get('email', None),
        'username': request.json.get('username', None),
        'password': request.json.get('password', None),
        'tickets': 10,
        'money': 100
    }
    confirmPassword = request.json.get('confirmPassword', None)
    
    print(new_user_data)
    user_exists = User.query.filter_by(email = new_user_data['email']).first()
    print(user_exists)
    if user_exists:
        return {"success": False, "msg": "Email already taken"}, 402
    
    if new_user_data['password'] != confirmPassword:
        return{'success': False, 'msg': 'Passwords did not match'}, 402
    
    new_user = User()
    new_user.from_dict(new_user_data)
    new_user.save_to_db()

    return{'success': True, 'msg': 'Successfully registered!'}, 200

@app.route('/roll', methods = ['POST'])
@jwt_required()
def roll():
    new_poke_data = {
        'poke_name': request.json.get('poke_name', None),
        'poke_type': request.json.get('poke_type', None),
        'sprite_url': request.json.get('sprite_url', None),
        'hp': request.json.get('hp', None),
        'att': request.json.get('att', None),
        'defe': request.json.get('defe', None),
        'speed':request.json.get('speed', None)
    }

    poke_check = PokeHash.query.filter_by(poke_name=new_poke_data['poke_name']).first()
    if poke_check == None:
        new_poke_hash = PokeHash()
        new_poke_hash.from_dict(new_poke_data)
        new_poke_hash.save_to_db()
    print(new_poke_data)
    return jsonify({'msg': f'{new_poke_data["poke_name"]} sucessfully caught'})

@app.route('/catch', methods = ['POST'])
@jwt_required()
def catch():
    current_user = get_jwt_identity()
    poke_name = request.json.get('poke_name')
    queried_user = User.query.filter_by(email=current_user).first()
    queried_poke = PokeHash.query.filter_by(poke_name=poke_name).first()
    new_catch_data = {
        'damage': request.json.get('damage'),
        'crit': request.json.get('crit'),
        'accuracy': request.json.get('accuracy'),
        'poke_hash_id': queried_poke.id,
    }
    print(queried_poke.id)
    new_lukemon = Lukemon()
    new_lukemon.from_dict(new_catch_data)
    new_lukemon.save_to_db()
    queried_user.add_to_inventory(new_lukemon)
    return jsonify({'msg': f'successfully caught'})

@app.route('/saveTeam', methods=['POST'])
@jwt_required()
def saveTeam():
    current_user = get_jwt_identity()
    queried_usermon = User.query.filter_by(email=current_user).first().inventory.all()
    for lukemon in queried_usermon:
        lukemon.remove_from_team()
    ids = request.json.get('ids')
    for i,x in enumerate(ids):
        queried_lukemon = Lukemon.query.filter_by(id=x).first()
        queried_lukemon.add_to_team(i)
        queried_lukemon.update_to_db()
    return {'msg': 'Successfully saved!'}

@app.route('/getInv', methods=['GET'])
@jwt_required()
def getInv():
    inv_data = []
    current_user = get_jwt_identity()
    queried_inv = User.query.filter_by(email=current_user).first().inventory.all()
    for i in queried_inv:
        inv_data.append(i.to_dict())
    print(inv_data)
    return inv_data

@app.route('/getTeam/<int:bankerId>', methods=['GET'])
@jwt_required()
def getTeam(bankerId):
    team_data = []
    queried_inv = User.query.filter_by(id=bankerId).first().inventory.all()
    for i in queried_inv:
        if i.onTeam != None:
            team_data.append(i.to_dict())
    print(team_data)
    return team_data

@app.route('/postFight', methods=['POST'])
@jwt_required()
def postFight():
    current_user = get_jwt_identity()
    queried_user = User.query.filter_by(email=current_user).first()
    post_data = {
        'caption': request.json.get('caption'),
        'user_id': queried_user.id
    }
    print(post_data)
    new_post = PostFight()
    new_post.from_dict(post_data)
    new_post.save_to_db()
    return {'msg': 'Fight Posted!'}

@app.route('/getFeed', methods=['GET'])
def getFeed():
    feedData = []
    query_posts = PostFight().query.all()
    for i in query_posts:
        feedData.append(i.to_dict())
    return feedData

@app.route('/getUserData')
@jwt_required()
def getUserData():
    current_user = get_jwt_identity()
    queried_user = User.query.filter_by(email=current_user).first()
    user_data = queried_user.to_dict()
    return user_data