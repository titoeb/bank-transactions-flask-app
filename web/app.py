from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt
import spacy

# Set-up App
app = Flask(__name__)
api = Api(app)

# Initiallize db connection
client = MongoClient("mongodb://db:27017")
db = client.SimilarityDB
users = db["users"]

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

def count_tokens(username:str) -> bool:
    return users.find({
        "Username": username
        })[0]["Tokens"]

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
            "Tokens": 6,
        })

        return(jsonify({
                "status": 200,
                "msg": "User was sucessfully created"
        }))

class Detect(Resource):
    def post(self):
        postedData = request.get_json()
        
        # Parse inputs
        username = postedData["username"]
        password = postedData["password"]
        text1 = postedData["text1"]
        text2 = postedData["text2"]

        if not user_exists(username):
            return(jsonify({
                    "status": 301,
                    "msg": "The user does not exist."
                }))

        if not correct_password(username, password):
            return(jsonify({
                    "status": 302,
                    "msg": "The password is wrong!"
                    }))

        number_tokens = count_tokens(username)
        if number_tokens <= 0:
            return(jsonify({
                    "status": 303,
                    "msg": "You don't have sufficient tokens!"
                }))

        # Calculate the edit-distance
        nlp = spacy.load("en_core_web_sm")    
        text1_tokenized = nlp(text1)
        text2_tokenized = nlp(text2)
        
        similarity = text1_tokenized.similarity(text2_tokenized)
        
        users.update({
            "Username": username
            }, {"$set":{
                "Tokens": number_tokens-1
                }
            })

        return(jsonify({
             "status": 200,
             "similariy": similarity,
             "msg": "Similarity score calculated"
            }))

class Refill(Resource):
    def post(self):
        postedData = request.get_json()
        
        username = postedData["username"]
        admin_password = postedData["admin_password"]
        refill_amount = postedData["refill_amount"]

        if not user_exists(username):
            return(jsonify({
                        "status": 301,
                        "msg": "Invalid Username"
                    }))

        # This pw should be hashed and stored in the database
        # But for the sake of time let's do it this way:
        if not admin_password == "admin":
            return(jsonify({
                    "status": 304,
                    "msg": "Invalid admin password"
                }))

        current_tokens = count_tokens(username)
        users.update({
                "Username": username,
                },{
                    "$set": {
                            "Tokens": refill_amount + current_tokens
                        }
            })
        message = f"Congratulations, you now have {count_tokens(username)} Tokens!"
        return(jsonify({
                "status": 200, 
                "msg": message
            }))

api.add_resource(Register, "/register")
api.add_resource(Detect, "/detect")
api.add_resource(Refill, "/refill")

if __name__ == "__main__":
    	app.run(debug=True)

