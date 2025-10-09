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

# Si es Railway y aún no tiene querystring, añade SSL
if "proxy.rlwy.net" in db_url and "ssl=" not in db_url:
    sep = "&" if "?" in db_url else "?"
    db_url = f"{db_url}{sep}ssl=true"

app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
app.register_blueprint(main)

# ---- Diagnóstico rápido y creación de tablas ----
with app.app_context():
    try:
        db.create_all()
        print("✅ DB lista. URL:", app.config["SQLALCHEMY_DATABASE_URI"].split('@')[-1])
    except Exception as e:
        import traceback
        print("❌ Error al crear/verificar tablas:", e)
        traceback.print_exc()

# Rutas de verificación (temporales)
@app.route("/health")
def health():
    return "OK"

@app.route("/tablas")
def tablas():
    from sqlalchemy import inspect
    return {"tablas": inspect(db.engine).get_table_names()}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
