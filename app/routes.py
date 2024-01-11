from app import app
import requests
from .models import User, PokeHash, Lukemon, PostFight
from datetime import datetime
from flask import jsonify, request, g
from .auth import basic_auth, token_auth
import math
import random

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
    
    user_exists = User.query.filter_by(username = new_user_data['username']).first()
    if user_exists:
        return {"msg": "Username already taken"}, 400
    
    
    new_user = User()
    new_user.from_dict(new_user_data)
    new_user.save_to_db()

    return{'msg': 'Successfully registered!'}, 200

@app.route('/getBulkPokeHash', methods=['POST'])
def get_bulk_poke_hash():
    try:
        data = request.get_json()
        poke_names = data.get('pokeNames', [])

        if not poke_names:
            return jsonify({'error': 'No Pokémon names provided'}), 400

        queried_pokes = []
        for poke_name in poke_names:
            poke = PokeHash.query.filter_by(id=poke_name).first()
            if poke:
                queried_pokes.append(poke.to_dict())

        if not queried_pokes:
            return jsonify({'error': 'No Pokémon found'}), 404

        return jsonify(queried_pokes)
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/catch', methods = ['POST'])
@token_auth.login_required
def catch():
    poke_name = request.json.get('poke_name')
    queried_poke = PokeHash.query.filter_by(id=poke_name).first()
    new_catch_data = {
        'damage': request.json.get('damage'),
        'crit': request.json.get('crit'),
        'accuracy': request.json.get('accuracy'),
        'poke_hash_id': queried_poke.id,
        'shiny': request.json.get('shiny'),
    }

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
    return inv_data

@app.route('/getTeam/<int:bankerId>')
@token_auth.login_required
def getTeam(bankerId):
    team_data = []
    queried_inv = User.query.filter_by(id=bankerId).first().inventory.all()
    for i in queried_inv:
        if i.onTeam != None:
            team_data.append(i.to_dict())
    return team_data

@app.route('/getPlayerTeam')
@token_auth.login_required
def getPlayerTeam():
    queried_inv = g.current_user.inventory.all()
    team_data = []
    for i in queried_inv:
        if i.onTeam != None:
            team_data.append(i.to_dict())
    return team_data

@app.route('/postFight', methods=['POST'])
@token_auth.login_required
def postFight():
    user_id = g.current_user.id
    post_exists = PostFight().query.filter_by(user_id=user_id).first()
    if post_exists:
        post_exists.caption = request.json.get('caption')
        post_exists.team_urls = request.json.get('team_urls')
        post_exists.team_value = request.json.get('team_value')
        post_exists.date_created = datetime.utcnow()
        post_exists.update_to_db()
        print(post_exists.team_urls)
        return {'msg': 'Post Successfully Updated!'}, 200
    
    post_data = {
        'caption': request.json.get('caption'),
        'team_urls': request.json.get('team_urls'),
        'team_value': request.json.get('team_value'),
        'user_id': g.current_user.id
    }
    new_post = PostFight()
    new_post.from_dict(post_data)
    new_post.save_to_db()
    return {'msg': 'Fight Posted!'}

@app.route('/getFeed')
def get_feed():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    query_posts = PostFight.query.order_by(PostFight.date_created.asc()).paginate()
    print(query_posts.items)
    feed_data = {
        'posts': [post.to_dict() for post in query_posts.items],
        'total_pages': query_posts.pages,
        'current_page': query_posts.page,
        'total_posts': query_posts.total
    }
    return feed_data

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

@app.route('/invCount')
@token_auth.login_required
def invCount():
    inv_count = len(g.current_user.inventory.all())
    return { 'inv_count':inv_count}

@app.route('/create_guest', methods=['POST'])
def create_guest():
    num = int(random.random()*10000)
    new_user_data = {
        'img_url': 'https://i.imgur.com/mpLsi9t.jpg',
        'username': f'Guest{num}',
        'password': request.json.get('password'),
        'tickets': 10,
        'money': 100
    }
    
    user_exists = User.query.filter_by(username = new_user_data['username']).first()
    if user_exists:
        return {"msg": "Failed to generate new user, please try again"}, 400
    
    new_user = User()
    new_user.from_dict(new_user_data)
    new_user.save_to_db()

    return{'username': new_user_data['username']}, 200

# this hashes all the pokemon info used for lukemon from poke.api
@app.route('/pokeHaul', methods=['GET'])
def pokeHaul():
    i = 1
    pokeDict = {}
    while i <= 649:
        req = requests.get(f'https://pokeapi.co/api/v2/pokemon/{i}')
        data = req.json()
        types_array = []
        for entry in data['types']:
            types_array.append(entry['type']['name'])
        pokeDict = {
            'poke_name': data['name'],
            'poke_type': types_array,
            'sprite_url': data['sprites']['versions']['generation-v']['black-white']['animated']['front_default'],
            'value': math.ceil(data['base_experience'] / 20),
            'hp': int(data['stats'][0]['base_stat']*1.75),
            'att': data['stats'][1]['base_stat'] + data['stats'][3]['base_stat'],
            'defe': data['stats'][2]['base_stat'] + data['stats'][4]['base_stat'],
            'speed': data['stats'][5]['base_stat'],
            'shiny_url': data['sprites']['versions']['generation-v']['black-white']['animated']['front_shiny'],
        }
        pokemon = PokeHash()
        pokemon.from_dict(pokeDict)
        pokemon.save_to_db()
        print(pokemon.poke_name)
        i+=1
    return 'done'