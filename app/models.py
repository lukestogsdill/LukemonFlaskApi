from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

inventory=db.Table('inventory',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('lukemon_id', db.Integer, db.ForeignKey('lukemon.id'))
    )

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    img_url = db.Column(db.String, nullable=True)
    username = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    tickets = db.Column(db.Integer, nullable=False)
    money = db.Column(db.Integer, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow())
    token = db.Column(db.String, unique=True)
    post_fight = db.relationship('PostFight', backref='author', lazy='dynamic')
    inventory = db.relationship('Lukemon', secondary=inventory, backref='inventory', lazy='dynamic') 

    # hashes our password
    def hash_password(self, original_password):
        return generate_password_hash(original_password)
    
    # check password hash
    def check_hash_password(self, login_password):
        return check_password_hash(self.password, login_password)
    
    # use this method to register our user attributes
    def from_dict(self, data):
        self.img_url = data['img_url']
        self.username = data['username']
        self.email = data['email']
        self.password = self.hash_password(data['password'])
        self.tickets = data['tickets']
        self.money = data['money']

    def to_dict(self):
        data = {
            'img_url': self.img_url,
            'username': self.username,
            'tickets': self.tickets,
            'money': self.money
        }
        return data
    
    def get_token(self):
        if self.token:
            return self.token
        self.token = secrets.token_urlsafe(32)
        self.save_to_db()
        return self.token
    
    def check_token(token):
        user = User.query.filter_by(token=token).first()
        if not user:
            return None
        return user

    def update_from_dict(self, data):
        self.img_url = data['img_url']
        self.username = data['username']

    def fight_reward(self):
        self.money += 10

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def update_to_db(self):
        db.session.commit()
    
    def add_to_inventory(self, lukemon):
        self.inventory.append(lukemon)
        db.session.commit()
    
    def remove_from_inventory(self, lukemon):
        self.inventory.remove(lukemon)
        db.session.commit()

    def add_to_bank(self, data):
        self.money = data['money']
    
    def add_to_tickets(self, data):
        self.tickets = data['tickets']

class PokeHash(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    poke_name = db.Column(db.String, nullable=False)
    poke_type = db.Column(db.String, nullable=False)
    sprite_url = db.Column(db.String, nullable=False)
    hp = db.Column(db.Integer, nullable=False)
    att = db.Column(db.Integer, nullable=False)
    defe = db.Column(db.Integer, nullable=False)
    speed = db.Column(db.Integer, nullable=False)
    lukemon = db.relationship('Lukemon', backref='lukemon', lazy='dynamic')
    
    def from_dict(self, data):
        self.poke_name = data['poke_name']
        self.poke_type = data['poke_type']
        self.sprite_url = data['sprite_url']
        self.hp = data['hp']
        self.att = data['att'] 
        self.defe = data['defe'] 
        self.speed = data['speed']

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
    
    
class Lukemon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    damage = db.Column(db.Integer, nullable=False)
    crit = db.Column(db.Float, nullable=False)
    accuracy = db.Column(db.Float, nullable=False)
    onTeam = db.Column(db.Integer)
    isAlive = db.Column(db.Boolean)
    poke_hash_id = db.Column(db.Integer, db.ForeignKey('poke_hash.id'))

    def from_dict(self, data):
        self.damage = data['damage']
        self.crit = data['crit']
        self.accuracy = data['accuracy']
        self.isAlive = True
        self.poke_hash_id = data['poke_hash_id']
    
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
    
    def to_dict(self):
        data = {
            'lukemon_id': self.id,
            'damage': self.damage,
            'crit': self.crit,
            'accuracy': self.accuracy,
            'onTeam': self.onTeam,
            'isAlive': self.isAlive,
            'poke_hash': {
                'poke_name': self.lukemon.poke_name,
                'poke_type': self.lukemon.poke_type,
                'sprite_url': self.lukemon.sprite_url,
                'hp': self.lukemon.hp,
                'att': self.lukemon.att,
                'defe': self.lukemon.defe,
                'speed': self.lukemon.speed
            }
        }
        return data
    
    def add_to_team(self, data):
        self.onTeam = data

    def remove_from_team(self):
        self.onTeam = None
    
    def update_to_db(self):
        db.session.commit()
    

class PostFight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    caption = db.Column(db.String)
    date_created = db.Column(db.DateTime, default=datetime.utcnow())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def from_dict(self, data):
        self.caption = data['caption']
        self.user_id = data['user_id']

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_post(self):
        db.session.delete(self)
        db.session.commit()

    def to_dict(self):
        data = {
            'caption': self.caption,
            'date_created':  self.date_created,
            'user_id': self.user_id,
            'username': self.author.username,
            'user_img': self.author.img_url
        }
        return data