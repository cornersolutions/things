from flask import request, jsonify, make_response
import jwt
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import uuid

from src.app_init import app
from src.dbs.dbs import setup_session, session_scope, User, Thing, Description, Inventory, Group, GroupUser, GroupThing, db

# http://127.0.0.1:8081/ On both docker and locally.


######################################################
# Registration and Login info from 
# https://www.geeksforgeeks.org/using-jwt-for-user-authentication-in-flask/
######################################################
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # jwt is passed in the request header
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        # return 401 if token is not passed
        if not token:
            return jsonify({'message' : 'Token is missing !!'}), 401
  
        try:
            # decoding the payload to fetch the stored details
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms="HS256")
            current_user = User.query\
                .filter_by(public_id = data['public_id'])\
                .first()
        except:
            return jsonify({
                'message' : 'Token is invalid !!'
            }), 401
        # returns the current logged in users contex to the routes
        return  f(current_user, *args, **kwargs)
  
    return decorated

# User Database Route
# this route sends back list of users users
@app.route('/user', methods =['GET'])
@token_required
def get_all_users(current_user):
    # querying the database
    # for all the entries in it
    users = User.query.all()
    # converting the query objects
    # to list of jsons
    output = []
    for user in users:
        # appending the user data json
        # to the response list
        output.append({
            'public_id': user.public_id,
            'name' : user.name,
            'email' : user.email
        })
  
    return jsonify({'users': output})
  
# route for loging user in
@app.route('/login', methods =['POST'])
def login():
    # creates dictionary of form data
    auth = request.form
  
    if not auth or not auth.get('name') or not auth.get('password'):
        # returns 401 if any email or / and password is missing
        return make_response(
            'Could not verify',
            401,
            {'WWW-Authenticate' : 'Basic realm ="Login required !!"'}
        )
  
    user = User.query\
        .filter_by(name = auth.get('name'))\
        .first()
  
    if not user:
        # returns 401 if user does not exist
        return make_response(
            'Could not verify',
            401,
            {'WWW-Authenticate' : 'Basic realm ="User does not exist !!"'}
        )
  
    if check_password_hash(user.password, auth.get('password')):
        # generates the JWT Token
        token = jwt.encode({
            'public_id': user.public_id,
            'exp' : datetime.utcnow() + timedelta(minutes = 30)
        }, app.config['SECRET_KEY'],
        algorithm="HS256")
  
        return make_response(jsonify({'token' : token}), 201)
    # returns 403 if password is wrong
    return make_response(
        'Could not verify',
        403,
        {'WWW-Authenticate' : 'Basic realm ="Wrong Password !!"'}
    )
  
# signup route
@app.route('/signup', methods =['POST'])
def signup():
    # creates a dictionary of the form data
    data = request.form
  
    # gets name, email and password
    name, email = data.get('name'), data.get('email')
    password = data.get('password')
  
    # checking for existing user
    user = User.query\
        .filter_by(email = email)\
        .first()
    if not user:
        # database ORM object
        user = User(
            public_id = str(uuid.uuid4()),
            name = name,
            email = email,
            password = generate_password_hash(password)
        )
        # insert user
        db.session.add(user)
        db.session.commit()
  
        return make_response('Successfully registered.', 201)
    else:
        # returns 202 if user already exists
        return make_response('User already exists. Please Log in.', 202)

@app.route('/')
def index():
    setup_session()
    return 'hello world'


@app.route('/create_thing/<thing_name>/<thing_description>')
@token_required
def create_thing(current_user, thing_name, thing_description):
    setup_session()
    with session_scope() as session:
        thng = Thing.get_unique(session, thing_name=thing_name)
        thng.description = Description(description=thing_description)
        session.add(thng)
        session.commit()
        thng_dict = thng.get_class_table_vals()
    return jsonify(thng_dict)


@app.route('/add_inventory/<thing_id>')
@token_required
def add_inventory(current_user, thing_id):
    setup_session()
    with session_scope() as session:
        inv = Inventory.get_unique(session, inventory_user_id=current_user.id, inventory_thing_id=thing_id)
        session.add(inv)
        session.commit()
        inv_dict = inv.get_class_table_vals()
    return jsonify(inv_dict)


@app.route('/get_inventory')
@token_required
def get_inventory(current_user):
    setup_session()
    #TODO: Can we use an association table relationship to make this query easier (inventory is association table)?
    with session_scope() as session:
        inventory = session.query(Thing.thing_name,
                                  Description.description).\
            join(Inventory, Inventory.inventory_thing_id == Thing.thing_id).\
            join(User, User.id == Inventory.inventory_user_id).\
            join(Description, Description.description_id == Thing.thing_description_id).\
            filter(User.id == current_user.id).all()
        inventory = [{'thing': x, 'description': y} for x, y in inventory]
    return jsonify(inventory)


# @app.route('/add_group/<group_name>/<user_id>')
# @token_required
# def add_group(group_name, user_id):
#     with session_scope() as session:
#         grp = Group(group_name=group_name)
#         if user_id == -1:  # Allow to pass -1 if do not want to setup as a user owned group
#             grp.user_owned_group = False
#         else:
#             grp.user_owned_group = True
#             usr = User.get_unique(session=session, id=user_id)
#             grp_usr = GroupUser()
#             grp_usr.user = usr
#             grp_usr.group = grp
#         session.add(grp)
#         session.add(grp_usr)
#         session.commit()
#         grp_dict = grp.get_class_table_vals()
#     return jsonify(grp_dict)


# @app.route('/add_group_user/<group_id>/<user_id>')
# @token_required
# def add_group_user(group_id, user_id):
#     with session_scope() as session:
#         grp = Group.get_unique(session, group_id=group_id)
#         usr = User.get_unique(session, id=user_id)
#         grp_usr = GroupUser()
#         grp_usr.user_owner = False
#         grp_usr.user = usr
#         grp_usr.group = grp
#         session.add(grp_usr)
#         session.commit()
#         grp_usr_dict = grp_usr.get_class_table_vals()
#     return jsonify(grp_usr_dict)


# @app.route('/add_group_thing/<group_id>/<thing_id>')
# @token_required
# def add_group_thing(group_id, thing_id):
#     with session_scope() as session:
#         grp = Group.get_unique(session, group_id=group_id)
#         thng = Thing.get_unique(session, thing_id=thing_id)
#         grp_thng = GroupThing()
#         grp_thng.thing = thng
#         grp_thng.group = grp
#         session.add(grp_thng)
#         session.commit()
#         grp_thing_dict = grp_thng.get_class_table_vals() 
#     return jsonify(grp_thing_dict)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)