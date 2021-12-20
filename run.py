#!/usr/bin/env python3
import time
import Configuration
import WSGIServer
import os


if __name__ == "__main__":
    debug = os.getenv('debug', True)
    app = WSGIServer.APIServer(Configuration.environment['flask']['ip_address'],
                               Configuration.environment['flask']['port'],
                               Configuration.cwd,
                               debug=debug)

    try:
        while True:
            # Flask runs in its own thread, so do anything you like here outside of the flask application...
            time.sleep(1)
    except KeyboardInterrupt:
        app.stop()
