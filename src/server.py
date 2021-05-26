from flask import Flask, request, jsonify
from things.src.dbs import setup_session, session_scope, User, Thing, Description, Inventory, Group, GroupUser, GroupThing

app = Flask(__name__)


@app.route('/')
def index():
    return 'hello world'


@app.route('/create_user/<name>')
def create_user(name):
    setup_session()
    print(f'{name}')
    with session_scope() as session:
        usr = User.get_unique(session=session,
                              user_name=name)
        session.commit()
        usr_dict = usr.get_class_table_vals()
    return jsonify(usr_dict)


@app.route('/create_thing/<thing_name>/<thing_description>')
def create_thing(thing_name, thing_description):
    setup_session()
    with session_scope() as session:
        thng = Thing(thing_name=thing_name)
        thng.description = Description(description=thing_description)
        session.add(thng)
        session.commit()
        thng_dict = thng.get_class_table_vals()
    return jsonify(thng_dict)


@app.route('/add_inventory/<user_id>/<thing_id>')
def add_inventory(user_id, thing_id):
    setup_session()
    with session_scope() as session:
        inv = Inventory(inventory_user_id=user_id, inventory_thing_id=thing_id)
        session.add(inv)
        session.commit()
        inv_dict = inv.get_class_table_vals()
    return jsonify(inv_dict)


@app.route('/get_inventory/<user_id>')
def get_inventory(user_id):
    setup_session()
    #TODO: Can we use an association table relationship to make this query easier (inventory is association table)?
    with session_scope() as session:
        inventory = session.query(Thing.thing_name,
                                  Description.description).\
            join(Inventory, Inventory.inventory_thing_id == Thing.thing_id).\
            join(User, User.user_id == Inventory.inventory_user_id).\
            join(Description, Description.description_id == Thing.thing_description_id).\
            filter(User.user_id == user_id).all()
        inventory = [{'thing': x, 'description': y} for x, y in inventory]
    return jsonify(inventory)


@app.route('/add_group/<group_name>/<user_id>')
def add_group(group_name, user_id):
    setup_session()
    with session_scope() as session:
        grp = Group(group_name=group_name)
        if user_id == -1:  # Allow to pass -1 if do not want to setup as a user owned group
            grp.user_owned_group = False
        else:
            grp.user_owned_group = True
            usr = User.get_unique(session=session, user_id=user_id)
            grp_usr = GroupUser()
            grp_usr.user = usr
            grp_usr.group = grp
        session.add(grp)
        session.add(grp_usr)
        session.commit()
        grp_dict = grp.get_class_table_vals()
    return jsonify(grp_dict)


@app.route('/add_group_user/<group_id>/<user_id>')
def add_group_user(group_id, user_id):
    setup_session()
    with session_scope() as session:
        grp = Group.get_unique(session, group_id=group_id)
        usr = User.get_unique(session, user_id=user_id)
        grp_usr = GroupUser()
        grp_usr.user_owner = False
        grp_usr.user = usr
        grp_usr.group = grp
        session.add(grp_usr)
        session.commit()
        grp_usr_dict = grp_usr.get_class_table_vals()
    return jsonify(grp_usr_dict)


@app.route('/add_group_thing/<group_id>/<thing_id>')
def add_group_thing(group_id, thing_id):
    setup_session()
    with session_scope() as session:
        grp = Group.get_unique(session, group_id=group_id)
        thng = Thing.get_unique(session, thing_id=thing_id)
        grp_thng = GroupThing()
        grp_thng.thing = thng
        grp_thng.group = grp
        session.add(grp_thng)
        session.commit()
        grp_thing_dict = grp_thng.get_class_table_vals() 
    return jsonify(grp_thing_dict)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)