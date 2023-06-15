from app import create_app
from waitress import serv

app=create_app()
if __name__ == "__main__":
    serv(app, host='0.0.0.0', port=8000)