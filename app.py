import os
from flask import Flask
from models import db
from controllers.main_controller import main

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "tu_clave_secreta_aqui")

# 🔹 Conexión: Render (DATABASE_URL) o local
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:Cemora1909@localhost/tu_base_de_datos"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Inicializar base de datos
db.init_app(app)

# Registrar blueprints
app.register_blueprint(main)

# ✅ Crear tablas si no existen (en Render o local)
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
