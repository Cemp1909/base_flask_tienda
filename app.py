# app.py
import os
from flask import Flask
from flask_migrate import Migrate
from models import db
from controllers.main_controller import main
from config_singleton import Configuracion  # ✅ importa tu clase de configuración

# --- Inicializa la configuración global (usa Singleton o clase Configuracion) ---
config = Configuracion()
app = config.app  # Flask app ya configurada dentro de Configuracion
app.register_blueprint(main)

# --- Inicializa Flask-Migrate ---
migrate = Migrate(app, db)

# --- Importa modelos para que Alembic detecte los cambios ---
from models import (
    Blusa, Bluson, Vestido, Enterizo, Jean, VestidoGala,
    Compra, Usuario, Transaction
)

# --- Diagnóstico: crea tablas si no existen y muestra cuáles detecta ---
with app.app_context():
    from sqlalchemy import inspect
    db.create_all()
    print("✅ Tablas presentes:", inspect(db.engine).get_table_names())

# --- Rutas simples de prueba ---
@app.route("/health")
def health():
    return "OK"

@app.route("/tablas")
def tablas():
    from sqlalchemy import inspect
    return {"tablas": inspect(db.engine).get_table_names()}

# --- Ejecución local ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
