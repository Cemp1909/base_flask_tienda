import os
from flask import Flask
from models import db
from controllers.main_controller import main

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "tu_clave_secreta_aqui")

# Conexión MySQL
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:Cemora1909@localhost/tu_base_de_datos"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Inicializar base de datos
db.init_app(app)

# Registrar controlador
app.register_blueprint(main)

if __name__ == "__main__":
    from app import app
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000)

