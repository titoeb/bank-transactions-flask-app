# Flask template

## How to use
This is my Flask template that I use to build flask based web-services. It has a development and a production set-up. To develop the web-service start-up the environment with `docker-compose up`. Then you can develop the code locally on your computer. To add packages to the environment, simply add them to the `requirements.txt`-file and rebuild the image with `docker-compose up --build`. The `Dockerfile` then can be adapted to production and copies the current state of the flask-app and executes it. 

# Resource Table
In the following table you should document the resources of your rest-api to make it easier to understand:
| Resource | Method | Path | Parameters | error-codes |
| --- | --- | --- | --- | --- |
| Register as a new user | POST  | /register | username:str, password:str | 200 OK , 301 Invalid Username | 
| Detect similarity between two documents | POST | /detect | username: str, password: str, document1:str, document2:str| 200 OK, 301 Invalid Username, 302 Invalid password, 303 Out of tokens |
| Add new tokens for a specific user | POST | /refill | username:str, admin\_pw:str, refill\_amount:int | 200 OK, 301 Invalid Username, 304 Invalid admin password |

Happy Hacking!
