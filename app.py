from app_server import app

if __name__ == '__main__':
    # app.run(port=5000, debug=True,host="0.0.0.0",ssl_context=('config/fssl.pem', 'config/fssl.key'))
    app.run(port=5000, debug=True, host="0.0.0.0")


