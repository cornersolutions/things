import json
from things.src.dbs.dbs import session_scope
from things.src.dbs.dbs import Description


def test_index(client):
    print('test_index')
    response = client.get('/')
    print(response)


def test_add_user(client):
    # Testing that a basic add succeeds
    response = client.get('/create_user/david')
    data = json.loads(response.data)
    assert data['user_name'] == 'david'
    assert data['user_id'] == 1

    # Testing that adding a user twice produces the same user_id
    response = client.get('/create_user/david')
    data = json.loads(response.data)
    assert data['user_name'] == 'david'
    assert data['user_id'] == 1


def test_add_thing(client):
    # Test that when we add an item it creates the item and the description row.
    response = client.get('/create_thing/myitem/words')
    data = json.loads(response.data)
    assert data['thing_name'] == 'myitem'
    assert data['thing_id'] == 1
    assert data['thing_description_id'] == 1
    assert data['thing_photo_id'] == None

    with session_scope() as session:
        desc = session.query(Description).first()
        assert desc.description == 'words'




