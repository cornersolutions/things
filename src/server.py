from flask import Flask, request, jsonify
from dbs import setup_session, session_scope, User

app = Flask(__name__)


@app.route('/create_user/<name>')
def create_user(name):
    print(f'{name}')
    setup_session()
    with session_scope() as session:
        session.add(User(user_name=name))
    return jsonify({'name': f'{name}', 'user_id': -1})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)