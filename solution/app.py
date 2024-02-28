from flask import Flask, request, jsonify
from config import SERVER_ADDRESS, SERVER_PORT
from database import start_session, start_engine
from sqlalchemy import text


app = Flask(__name__)

@app.route('/api/ping', methods=['GET'])
def send():
    return jsonify({"status": "ok"}), 200


@app.route('/api/countries', methods=["GET"])
def list_countries():
    if not request.args.get('region') == None:
        with engine.connect() as connection:
            result = connection.execute(text(f"SELECT name FROM countries WHERE region = '{request.args.get('region').capitalize()}'")).all()
            
            return jsonify([i[0] for i in result])
    else:
        with engine.connect() as connection:
            result = connection.execute(text(f"SELECT name FROM countries")).all()
            return jsonify([i[0] for i in result])



if __name__ == "__main__":
    engine = start_engine()
    app.run(host=SERVER_ADDRESS, port=SERVER_PORT, debug=True)
