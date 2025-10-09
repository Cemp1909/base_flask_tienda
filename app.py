import os
from flask import Flask
from models import db  # instancia de SQLAlchemy
from controllers.main_controller import main

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "tu_clave_secreta_aqui")

# ---- DB config (Render/Local) ----
db_url = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:Cemora1909@localhost/tu_base_de_datos"
)
# Si es Railway por red pública, añade SSL (seguro e inofensivo si ya está)
if "proxy.rlwy.net" in db_url and "ssl=" not in db_url:
    db_url += ("&" if "?" in db_url else "?") + "ssl=true"

app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Inicializar SQLAlchemy
db.init_app(app)

# 👇 IMPORTANTE: importar las clases para que se registren en el metadata
from models import (  # noqa: E402
    Blusa, Bluson, Vestido, Enterizo, Jean, VestidoGala,
    Compra, Usuario, Transaction
)

# Registrar blueprints
app.register_blueprint(main)

# Crear tablas y loguear lo que pasó (diagnóstico)
with app.app_context():
    from sqlalchemy import inspect
    db.create_all()
    print("✅ Tablas presentes:", inspect(db.engine).get_table_names())

# --- RUTAS DE PRUEBA (puedes borrarlas luego) ---
@app.route("/health")
def health():
    return "OK"

@app.route("/tablas")
def tablas():
    from sqlalchemy import inspect
    return {"tablas": inspect(db.engine).get_table_names()}

# Run local (Render usa gunicorn)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
