# app.py
import os
from flask import Flask
from flask_migrate import Migrate
from models import db
from controllers.main_controller import main

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "tu_clave_secreta_aqui")

# ---- DB config (Railway/Render/Local) ----
db_url = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:Cemora1909@localhost/tu_base_de_datos"
)

# Si viene como mysql:// (sin driver), conviértelo a mysql+pymysql://
if db_url.startswith("mysql://"):
    db_url = db_url.replace("mysql://", "mysql+pymysql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# ✅ Inicializa Flask-Migrate (esto habilita 'flask db ...')
migrate = Migrate(app, db)

# importa modelos para que Alembic los detecte
from models import (  # noqa: E402
    Blusa, Bluson, Vestido, Enterizo, Jean, VestidoGala,
    Compra, Usuario, Transaction,
)

# registra tus rutas si aplica
app.register_blueprint(main)

# Diagnóstico: crea tablas y muestra cuáles ve
with app.app_context():
    from sqlalchemy import inspect
    db.create_all()
    print("✅ Tablas presentes:", inspect(db.engine).get_table_names())

# Rutas de prueba (puedes quitarlas luego)
@app.route("/health")
def health():
    return "OK"

@app.route("/tablas")
def tablas():
    from sqlalchemy import inspect
    return {"tablas": inspect(db.engine).get_table_names()}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
