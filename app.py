from flask import Flask, jsonify, request
from models import db
from config import get_config
from routes.jobs import jobs
from routes.applications import applications
from routes.webhooks import webhooks
from flask_cors import CORS
import os
import sys
from logger import logger
from werkzeug.middleware.proxy_fix import ProxyFix

def create_app():
    """Initialize the core application"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(get_config())
    
    # Add proxy support for ngrok
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Initialize database connection
    db.init_app(app)
    
    # Enable CORS for all routes and origins
    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
    
    # Register blueprints
    app.register_blueprint(jobs, url_prefix='/api/jobs')
    app.register_blueprint(applications, url_prefix='/api/applications')
    app.register_blueprint(webhooks, url_prefix='/api/webhook')
    
    # Root path handler
    @app.route('/')
    def root():
        return jsonify({"message": "API server is running. Use /api/jobs, /api/applications endpoints."})
    
    # Initialize database
    with app.app_context():
        try:
            db.create_all()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error("Error initializing database", exc_info=True)
    
    return app

def recreate_database(app):
    """Recreate the database tables"""
    with app.app_context():
        try:
            logger.info("Dropping all tables to update schema")
            db.drop_all()
            logger.info("Creating all tables with updated schema")
            db.create_all()
            logger.info("Database recreated successfully with updated schema")
            return True
        except Exception as e:
            logger.error("Error recreating database", exc_info=True)
            return False

# Create the application
app = create_app()

if __name__ == '__main__':
    # Handle command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == '--recreate-db':
        success = recreate_database(app)
        print("Database recreated successfully!" if success else "Failed to recreate database")
        sys.exit(0)
    
    # Parse port from arguments or environment
    port = 8001  # Default port
    args = sys.argv[1:]
    for i, arg in enumerate(args):
        if arg == '--port' and i + 1 < len(args):
            port = int(args[i + 1])
        elif arg.startswith('--port='):
            port = int(arg.split('=')[1])
    
    # Alternatively, get from environment
    port = int(os.environ.get('PORT', port))
    
    print(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True) 