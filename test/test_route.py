import json


def test_index(client):
    print('test_index')
    response = client.get('/')
    print(response)


def test_add_user(client):
    response = client.get('/create_user/david')
    data = json.loads(response.data)
    assert data['user_name'] == 'david'
    assert data['user_id'] == 1