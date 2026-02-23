from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    host = app.config["server"]["host"]
    port = app.config["server"]["port"]
    debug = app.config["server"]["debug"]

    if app.config["env"] == "production" and debug:
        app.logger.warning("Debug mode is enabled in production environment.")

    app.run(host=host, port=port, debug=debug)

