from app import create_app
import os
import traceback

    

if __name__ == '__main__':

    try:
        app = create_app()
    except Exception as e:
        print("Error starting application:")
        traceback.print_exc()
        exit(1)

    host = app.config["server"]["host"]
    port = app.config["server"]["port"]
    debug = app.config["server"]["debug"]

    if app.config["env"] == "production" and debug:
        app.logger.warning("Debug mode is enabled in production environment.")

    app.logger.info(f"Application started on {host}:{port} in {app.config['env']} environment.")

    app.run(host=host, port=port, debug=debug)
    
    app.logger.info("Application stopped.")

