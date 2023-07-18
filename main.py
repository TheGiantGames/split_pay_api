from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow


app = Flask(__name__)

@app.route('/')
def print():
    return "in print"

if __name__ == '__main__':
    app.run()