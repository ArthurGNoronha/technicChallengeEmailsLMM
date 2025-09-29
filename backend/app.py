from flask import Flask, jsonify
import os
from routes import api
from flask_cors import CORS
from utils.database import initDB
from utils.donwload_nltk import download_nltk_data

app = Flask(__name__, static_folder='../frontend', static_url_path='/')
CORS(app)

app.register_blueprint(api, url_prefix='/api')

initDB()
download_nltk_data()

@app.route('/<path:path>')
def serve_static(path):
    return app.send_static_file(path)

@app.route('/')
def serve_frontend():
    return app.send_static_file('index.html')

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', debug=False, port=port)