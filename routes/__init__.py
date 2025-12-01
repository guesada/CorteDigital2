"""Registro das rotas (blueprints) do Corte Digital."""

from . import appointments, auth, info, pages, barber_prices


def register_routes(app):
    """Registra todos os blueprints no app Flask principal."""

    app.register_blueprint(pages.pages_bp)
    app.register_blueprint(auth.auth_bp)
    app.register_blueprint(info.info_bp)
    app.register_blueprint(appointments.appointments_bp)
    app.register_blueprint(barber_prices.barber_prices_bp)
