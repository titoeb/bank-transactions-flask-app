from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt
from typing import Any, Dict, Union

# Set-up App
app = Flask(__name__)
api = Api(app)

# Initiallize db connection
client = MongoClient("mongodb://db:27017")
db = client.BankAPI
users = db["Users"]

# Helper functions
def user_exists(username: str) -> bool:
    return users.find({"Username":username}).count() > 0

def correct_password(username:str, password: str) -> bool:
    if not user_exists(username):
        return False

    hashed_pw = users.find({
        "Username": username
        })[0]["Password"]

    return bcrypt.hashpw(password.encode("utf8"), hashed_pw) == hashed_pw

def get_field_user(username:str, field: str) -> Any:
    return users.find({
        "Username": username
        })[0][field]

def set_field_user(username: str, field: str, value: Any):
     users.update({
            "Username": username
            }, {"$set":{
                field: value
                }
            })

def cash_with_user(username: str) -> int:
    return get_field_user(username, "Own")

def debt_with_user(username: str)->int:
    return get_field_user(username, "Debt")

def update_cash_with_user(username: str, new_cash: int):
    set_field_user(username, "Own", new_cash)

def update_debt_with_user(username: str, new_debt: int):
    set_field_user(username, "Debt", new_debt)

def generate_return_dict(status:str, message:str) -> Dict:
    return {
            "status": status,
            "msg": message
        }

def verify_user(username: str, password: str) -> Union[Dict, None]:
    if not user_exists(username):
        return generate_return_dict(301, "Invalid Username")

    if not correct_password(username, password):
        return generate_return_dict(302, "Invalid Password")

class Register(Resource):
    def post(self):
        postedData = request.get_json()

        # Parse inputs
        username = postedData["username"]
        password = postedData["password"]
        
        if user_exists(username):
            return(jsonify({
                "status": 301,
                "msg": "Invalid Username"
                }))

        # Hash user password
        hashed_password = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

        # Store the user data into the database.
        users.insert({
            "Username": username,
            "Password": hashed_password,
            "Own": 0,
            "Debt": 0
        })

        return(jsonify({
                "status": 200,
                "msg": "User was sucessfully created."
        }))

class Add(Resource):
    def post(self):
        postedData = request.get_json()

        username = postedData["username"]
        password = postedData["password"]
        amount = postedData["amount"]

        error_dict = verify_user(username, password)
        if error_dict:
            return(jsonify(error_dict))
        if amount <= 0:
            return(jsonify(generate_return_dict(304, "The amount needs to be larger than 0")))

        cash = cash_with_user(username)
        
        # From each transaction the bank gets 1 dollar.
        amount -= 1
        bank_cash = cash_with_user("BANK")
        update_cash_with_user("BANK", bank_cash + 1)

        # Finalize transaction for the suer
        update_cash_with_user(username, cash + amount)
        return(jsonify(generate_return_dict(200, "Money succesfully added to the bank account")))

class Transfer(Resource):
    def post(self):
        postedData = request.get_json()

        username = postedData["username"]
        password = postedData["password"]
        amount = postedData["amount"]
        to = postedData["to"]
        
        error_dict = verify_user(username, password)
        if error_dict:
            return(jsonify(error_dict))
        if amount <= 0:
            return(jsonify(generate_return_dict(304, "The amount needs to be larger than 0")))
        
        cash_user = cash_with_user(username)

        if cash_user < amount:
            return(jsonify(generate_return_dict(304, f"You cannot do this transaction as your current cash is {cash_user} and the transaction amount is {amount} ")))
        
        if not user_exists(to):
            return(jsonify(generate_return_dict("301", f"Receiver {to} is not known!" )))
        
        cash_to = cash_with_user(to)
        cash_bank = cash_with_user("BANK")

        update_cash_with_user("BANK", cash_bank + 1)
        update_cash_with_user(to, cash_to + amount - 1)
        update_cash_with_user(username, cash_user - amount)

        return(jsonify(generate_return_dict(200, "The money was sucessfully transfered")))

class Balance(Resource):
    def post(self):
        postedData = request.get_json()

        username = postedData["username"]
        password = postedData["password"]
        
        error_dict = verify_user(username, password)
        if error_dict:
            return(jsonify(error_dict))
        
        cash_user = cash_with_user(username)
        debt_user = debt_with_user(username)

        return(jsonify({
                "status": 200,
                "msg": "success",
                "cash": cash_user,
                "debt": debt_user
            }))

class TakeLoan(Resource):
    def post(self):

        postedData = request.get_json()
        username = postedData["username"]
        password = postedData["password"]
        loan = postedData["amount"]
        
        error_dict = verify_user(username, password)
        if error_dict:
            return(jsonify(error_dict))
        
        cash_user = cash_with_user(username)
        debt_user = debt_with_user(username)
        update_cash_with_user(username, cash_user + loan)
        update_debt_with_user(username, debt_user + loan)
        
        return jsonify(generate_return_dict(200, "Loan added to your account."))

class PayLoan(Resource):
    def post(self):

        postedData = request.get_json()
        username = postedData["username"]
        password = postedData["password"]
        amount = postedData["amount"]
        
        error_dict = verify_user(username, password)
        if error_dict:
            return(jsonify(error_dict))
        
        cash_user = cash_with_user(username)
        debt_user = debt_with_user(username)
    
        if cash_user < amount:
            return(jsonify(generate_return_dict(303, "Insufficient Funds!")))

        update_cash_with_user(username, cash_user - amount)
        update_debt_with_user(username, debt_user - amount)
        
        return jsonify(generate_return_dict(200, "Loan was removed from you account"))

api.add_resource(Register, "/register")
api.add_resource(Add, "/add")
api.add_resource(Transfer, "/transfer")
api.add_resource(Balance, "/balance")
api.add_resource(TakeLoan, "/takeloan")
api.add_resource(PayLoan, "/payloan")

if __name__ == "__main__":
    	app.run(debug=True)

