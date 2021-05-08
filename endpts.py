import flask

app = Flask(__name__)


app.route('/create_user/{name}')
def create_user():
    pass