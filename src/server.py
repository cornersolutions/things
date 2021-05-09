from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/create_user/<name>')
def create_user(name):
    print(f'{name}')
    return jsonify({'name': f'{name}', 'user_id': -1})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)