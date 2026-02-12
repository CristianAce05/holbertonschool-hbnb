from flask import Flask
from app.api import blueprint

app = Flask(__name__)

# Register the API blueprint
app.register_blueprint(blueprint)

@app.route('/')
def hello():
    return "HBnB Project is Running!"

if __name__ == '__main__':
    app.run(debug=True)
