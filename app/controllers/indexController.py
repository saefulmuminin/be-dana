from flask import Flask, Blueprint

app = Flask(__name__)

# kasih nama blueprint, misalnya 'index'
index_bp = Blueprint('index', __name__, url_prefix='/')

@index_bp.route('/', methods=['GET'])
def index():
    return "Ini halaman index"
