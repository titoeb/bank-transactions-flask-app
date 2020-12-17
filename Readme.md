# Flask template

## How to use
This is my Flask template that I use to build flask based web-services. It has a development and a production set-up. To develop the web-service start-up the environment with `docker-compose up`. Then you can develop the code locally on your computer. To add packages to the environment, simply add them to the `requirements.txt`-file and rebuild the image with `docker-compose up --build`. The `Dockerfile` then can be adapted to production and copies the current state of the flask-app and executes it. 

# Resource Table
In the following table you should document the resources of your rest-api to make it easier to understand:
| Resource | Method | Path | Parameters | error-codes |
| --- | --- | --- | --- | --- |
| Register as a new user | POST  | /register | username:str, password:str |  | 
| Add money to your bank account | POST | /add | username: str, password: str, amount: int | |
| Transfer money to another account  | POST | /transfer | username: str, password: str, amount: int, to: str | |
| Check the current balance | POST | /balance | username: str, password:str | |
| Take a loan | POST | / takeloan | username: str, password: str, amount: int | | 
| Pay a loan | POST | /payloan | username: str, password: str, amount: int | |

Happy Hacking!
