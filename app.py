import os
from flask import Flask
from models import db
from controllers.main_controller import main

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "tu_clave_secreta_aqui")

# ---- DB config (Render/Local) ----
db_url = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:Cemora1909@localhost/tu_base_de_datos"
)

# ❗️No agregamos ssl=true en la URL (PyMySQL espera un dict, no un string)
app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Si tu instancia realmente exige TLS y falla sin SSL,
# descomenta esto (activa TLS sin validar CA):
# app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
#     "connect_args": {
#         "ssl": {"fake_flag_to_enable_tls": True}
#     }
# }

db.init_app(app)

# registrar modelos para que create_all los vea
from models import (  # noqa: E402
    Blusa, Bluson, Vestido, Enterizo, Jean, VestidoGala,
    Compra, Usuario, Transaction
)

app.register_blueprint(main)

with app.app_context():
    from sqlalchemy import inspect
    db.create_all()
    print("✅ Tablas presentes:", inspect(db.engine).get_table_names())

@app.route("/health")
def health():
    return "OK"

@app.route("/tablas")
def tablas():
    from sqlalchemy import inspect
    return {"tablas": inspect(db.engine).get_table_names()}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
