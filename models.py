from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint

db = SQLAlchemy()

class RopaBase(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    talla = db.Column(db.String(10))
    color = db.Column(db.String(50))
    tipo  = db.Column(db.String(20))
    imagen = db.Column(db.String(255))
    stock = db.Column(db.Integer, nullable=False, default=0)  # ← NUEVO CAMPO

    __table_args__ = (
        CheckConstraint('stock >= 0', name='ck_stock_no_negativo'),
    )

class Blusa(RopaBase):
    __tablename__ = 'blusas'

class Bluson(RopaBase):
    __tablename__ = 'blusones'

class Vestido(RopaBase):
    __tablename__ = 'vestidos'

class Enterizo(RopaBase):
    __tablename__ = 'enterizos'

class Jean(RopaBase):
    __tablename__ = 'jeans'

class VestidoGala(RopaBase):
    __tablename__ = 'vestidosgala'


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
