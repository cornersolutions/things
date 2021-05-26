def test_index(client):
    print('test_index')
    response = client.get('/')
    print(response)