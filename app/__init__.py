import os
from flask import Flask, render_template
from app.config import Config
from app.models import db

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.students import students_bp
    from app.routes.projects import projects_bp
    from app.routes.teams import teams_bp
    from app.routes.comparison import comparison_bp
    from app.routes.balance import balance_bp
    from app.routes.simulation import simulation_bp
    from app.routes.network import network_bp
    from app.routes.learning import learning_bp
    from app.routes.audit import audit_bp
    from app.routes.feedback import feedback_bp
    from app.routes.reports import reports_bp
    from app.routes.settings import settings_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(teams_bp)
    app.register_blueprint(comparison_bp)
    app.register_blueprint(balance_bp)
    app.register_blueprint(simulation_bp)
    app.register_blueprint(network_bp)
    app.register_blueprint(learning_bp)
    app.register_blueprint(audit_bp)
    app.register_blueprint(feedback_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(settings_bp)

    # Context processors
    @app.context_processor
    def inject_globals():
        from app.models import Project
        all_active_projects = Project.query.filter_by(status='Active').all() if db.engine else []
        return {
            'nav_projects': all_active_projects,
            'app_name': 'AI Group Project Team Builder'
        }

    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    # Ensure tables and folders exist
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            app.logger.error(f"Error initializing database tables: {e}")

    return app
