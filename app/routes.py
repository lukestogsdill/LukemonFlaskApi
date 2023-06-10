from app import app
from .models import User, PokeHash, Lukemon, PostFight
from flask import jsonify, request, g
from .auth import basic_auth, token_auth    

@app.route('/token')
@basic_auth.login_required()
def create_token():
    token = g.current_user.get_token()
    return{'token': token}

@app.route('/logout', methods=['POST'])
@token_auth.login_required
def logout():
    pass

@app.route('/register', methods=['POST'])
def register():
    new_user_data = {
        'img_url': request.json.get('url',None),
        'username': request.json.get('username', None),
        'password': request.json.get('password', None),
        'tickets': 10,
        'money': 100
    }
    confirmPassword = request.json.get('confirmPassword', None)
    
    user_exists = User.query.filter_by(username = new_user_data['username']).first()
    print(user_exists)
    if new_user_data['password'] != confirmPassword:
        return{'msg': 'Passwords did not match'}, 400
    if user_exists:
        return {"msg": "Username already taken"}, 400
    
    
    new_user = User()
    new_user.from_dict(new_user_data)
    new_user.save_to_db()

    return{'msg': 'Successfully registered!'}, 200

@app.route('/roll', methods = ['POST'])
@token_auth.login_required
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
@token_auth.login_required
def catch():
    poke_name = request.json.get('poke_name')
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
    g.current_user.add_to_inventory(new_lukemon)
    return jsonify({'msg': f'{new_lukemon.lukemon.poke_name} successfully caught'})

@app.route('/saveTeam', methods=['POST'])
@token_auth.login_required
def saveTeam():
    queried_usermon = g.current_user.inventory.all()
    for lukemon in queried_usermon:
        lukemon.remove_from_team()
    ids = request.json.get('ids')
    for i,x in enumerate(ids):
        queried_lukemon = Lukemon.query.filter_by(id=x).first()
        queried_lukemon.add_to_team(i)
        queried_lukemon.update_to_db()
    return {'msg': 'Successfully saved!'}

@app.route('/getInv')
@token_auth.login_required
def getInv():
    inv_data = []
    queried_inv = g.current_user.inventory.all()
    for i in queried_inv:
        inv_data.append(i.to_dict())
    print(inv_data)
    return inv_data

@app.route('/getTeam/<int:bankerId>')
@token_auth.login_required
def getTeam(bankerId):
    team_data = []
    queried_inv = User.query.filter_by(id=bankerId).first().inventory.all()
    for i in queried_inv:
        if i.onTeam != None:
            team_data.append(i.to_dict())
    print(team_data)
    return team_data

@app.route('/getPlayerTeam')
@token_auth.login_required
def getPlayerTeam():
    queried_inv = g.current_user.inventory.all()
    team_data = []
    for i in queried_inv:
        if i.onTeam != None:
            team_data.append(i.to_dict())
    print(team_data)
    return team_data

@app.route('/postFight', methods=['POST'])
@token_auth.login_required
def postFight():
    post_data = {
        'caption': request.json.get('caption'),
        'user_id': g.current_user.id
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
@token_auth.login_required
def getUserData():
    user_data = g.current_user.to_dict()
    return user_data


@app.route('/fightReward')
@token_auth.login_required
def fightReward():
    current_user = g.current_user
    current_user.fight_reward()
    current_user.save_to_db()
    return jsonify({'msg':'Congrats here is 10 Money!'})

@app.route('/delPoke/<int:pokeId>', methods=['GET'])
@token_auth.login_required
def del_poke(pokeId):
    poke = Lukemon.query.filter_by(id=pokeId).first()
    poke.del_poke()
    return {'msg': 'Successfully Deleted'}

@app.route('/updateCurr', methods=['POST'])
@token_auth.login_required
def update_curr():
    current_user = g.current_user
    curr_data = {
        'tickets': request.json.get('tickets'),
        'money': request.json.get('money')
    }
    current_user.update_curr(curr_data)
    current_user.save_to_db()
    return {'msg': 'curr updated'}