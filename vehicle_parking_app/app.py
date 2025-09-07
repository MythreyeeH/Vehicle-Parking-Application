from flask import Flask
from controllers import controller
def create_app():
    app=Flask(__name__)
    app.secret_key = 'your_secret_key'  
    controller.init_app_routes(app)
    return app

if __name__=='__main__':
    app=create_app()
    app.run(debug=True)