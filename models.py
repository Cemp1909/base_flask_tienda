from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint
db = SQLAlchemy()

# 👇 Si tu MySQL/MariaDB es reciente y ENFORCE CHECKS, deja el CheckConstraint.
# En MySQL < 8.0.16 los CHECK se ignoran (no rompen, pero no validan).
CHECKS = (
    CheckConstraint('stock >= 0', name='ck_stock_no_negativo'),
)

class Blusa(db.Model):
    __tablename__ = 'blusas'
    id = db.Column(db.Integer, primary_key=True)
    talla = db.Column(db.String(10))
    color = db.Column(db.String(50))
    tipo  = db.Column(db.String(20))
    imagen = db.Column(db.String(255))
    stock = db.Column(db.Integer, nullable=False, server_default='0')
    __table_args__ = CHECKS

class Bluson(db.Model):
    __tablename__ = 'blusones'
    id = db.Column(db.Integer, primary_key=True)
    talla = db.Column(db.String(10))
    color = db.Column(db.String(50))
    tipo  = db.Column(db.String(20))
    imagen = db.Column(db.String(255))
    stock = db.Column(db.Integer, nullable=False, server_default='0')
    __table_args__ = CHECKS

class Vestido(db.Model):
    __tablename__ = 'vestidos'
    id = db.Column(db.Integer, primary_key=True)
    talla = db.Column(db.String(10))
    color = db.Column(db.String(50))
    tipo  = db.Column(db.String(20))
    imagen = db.Column(db.String(255))
    stock = db.Column(db.Integer, nullable=False, server_default='0')
    __table_args__ = CHECKS

class Enterizo(db.Model):
    __tablename__ = 'enterizos'
    id = db.Column(db.Integer, primary_key=True)
    talla = db.Column(db.String(10))
    color = db.Column(db.String(50))
    tipo  = db.Column(db.String(20))
    imagen = db.Column(db.String(255))
    stock = db.Column(db.Integer, nullable=False, server_default='0')
    __table_args__ = CHECKS

class Jean(db.Model):
    __tablename__ = 'jeans'
    id = db.Column(db.Integer, primary_key=True)
    talla = db.Column(db.String(10))
    color = db.Column(db.String(50))
    tipo  = db.Column(db.String(20))
    imagen = db.Column(db.String(255))
    stock = db.Column(db.Integer, nullable=False, server_default='0')
    __table_args__ = CHECKS

class VestidoGala(db.Model):
    __tablename__ = 'vestidosgala'
    id = db.Column(db.Integer, primary_key=True)
    talla = db.Column(db.String(10))
    color = db.Column(db.String(50))
    tipo  = db.Column(db.String(20))
    imagen = db.Column(db.String(255))
    stock = db.Column(db.Integer, nullable=False, server_default='0')
    __table_args__ = CHECKS


class Compra(db.Model):
    __tablename__ = 'compras'
    id = db.Column(db.Integer, primary_key=True)
    nombre_cliente = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.String(200), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    producto = db.Column(db.String(100), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.DateTime, server_default=db.func.now())

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nombre_usuario = db.Column(db.String(50), unique=True, nullable=False)
    contrasena_hash = db.Column(db.String(255), nullable=False)

# --- PÉGALO AL FINAL DE models.py ---
from datetime import datetime

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    tx_id = db.Column(db.String(64), unique=True, index=True)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(8), default="USD")
    status = db.Column(db.String(20), default="pending")  # pending | success | failed
    method = db.Column(db.String(20), default="card_fake")
    card_last4 = db.Column(db.String(4))
    card_brand = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
