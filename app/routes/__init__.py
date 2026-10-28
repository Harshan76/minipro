from .auth import auth_bp
from .dashboard import dashboard_bp
from .students import students_bp
from .projects import projects_bp
from .teams import teams_bp
from .comparison import comparison_bp
from .balance import balance_bp
from .simulation import simulation_bp
from .network import network_bp
from .learning import learning_bp
from .audit import audit_bp
from .feedback import feedback_bp
from .reports import reports_bp
from .settings import settings_bp

__all__ = [
    'auth_bp', 'dashboard_bp', 'students_bp', 'projects_bp',
    'teams_bp', 'comparison_bp', 'balance_bp', 'simulation_bp',
    'network_bp', 'learning_bp', 'audit_bp', 'feedback_bp',
    'reports_bp', 'settings_bp'
]
