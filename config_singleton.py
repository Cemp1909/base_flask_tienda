# config_singleton.py
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Instancia global de SQLAlchemy
db = SQLAlchemy()

class Configuracion:
    """
    Singleton para configuración global de Flask + Base de Datos.
    Garantiza que solo exista una instancia de 'app' y 'db' en todo el proyecto.
    """
    _instance = None  # Variable estática: guarda la única instancia

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Configuracion, cls).__new__(cls)
            cls._instance._init_app()
        return cls._instance

    def _init_app(self):
        self.app = Flask(__name__)
        self.app.secret_key = os.getenv("SECRET_KEY", "clave_local")

        # --- Configuración de la base de datos ---
        db_url = os.getenv(
            "DATABASE_URL",
            "mysql+pymysql://root:Cemora1909@localhost/tienda"
        )

        # Corrige URL sin driver (MySQL → PyMySQL)
        if db_url.startswith("mysql://"):
            db_url = db_url.replace("mysql://", "mysql+pymysql://", 1)

        self.app.config["SQLALCHEMY_DATABASE_URI"] = db_url
        self.app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

        # Inicializa SQLAlchemy y Migrate
        db.init_app(self.app)
        Migrate(self.app, db)
