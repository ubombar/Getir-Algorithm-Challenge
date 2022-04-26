import os
from solver import solve_vrp
from flask import Flask
from flask import request

app = Flask(__name__)

@app.route('/', methods=['GET'])
def vrp_get():
    return "Server is working. To test the solver service: POST request to '/'"

@app.route('/', methods=['POST']) 
def vrp_post():
    if len([n for n in ("vehicles", "jobs", "matrix") if n not in request.json]):
        return '"Bad Request"', 400

    response = solve_vrp(**request.json)

    if not response:
        return '"Internat Server Error"', 500

    return response


if __name__ == "__main__":
    debug = "PROD" not in os.environ
    app.run(host="0.0.0.0", debug=debug)