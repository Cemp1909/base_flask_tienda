# controllers/main_controller.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

from models import db, Blusa, Bluson, Vestido, Enterizo, Jean, VestidoGala, Compra, Usuario, Transaction
import random, time, string

main = Blueprint("main", __name__, url_prefix="")

# -------- Helpers de auth --------
def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Debes iniciar sesión", "warning")
            return redirect(url_for("main.login"))
        return view(*args, **kwargs)
    return wrapped

def _gen_tx_id(n=12):
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=n))

def _mask_card(number):
    return number[-4:] if number and len(number) >= 4 else number

# -------- Home --------
@main.route("/")
def inicio():
    return render_template("index.html")

# -------- Catálogo --------
@main.route("/blusas")
def blusas():
    data = Blusa.query.limit(6).all()
    return render_template("blusas.html", blusas=data)

@main.route("/blusones")
def blusones():
    data = Bluson.query.limit(6).all()
    return render_template("blusones.html", prendas=data)

@main.route("/vestidos")
def vestidos():
    data = Vestido.query.limit(6).all()
    return render_template("vestidos.html", vestidos=data)

@main.route("/enterizos")
def enterizos():
    data = Enterizo.query.limit(6).all()
    return render_template("enterizos.html", enterizos=data)

@main.route("/jeans")
def jeans():
    data = Jean.query.limit(6).all()
    return render_template("jeans.html", jeans=data)

@main.route("/vestidosgala")
def vestidosgala():
    data = VestidoGala.query.limit(6).all()
    return render_template("vestidosgala.html", vestidosgala=data)

# -------- Compra --------
@main.route("/comprar")
def comprar():
    talla = request.args.get("talla")
    color = request.args.get("color")
    tipo  = request.args.get("tipo")

    precios = {
        "Blusa": 20.00,
        "Bluson": 25.00,
        "Vestido": 40.00,
        "Enterizo": 35.00,
        "Jean": 30.00,
        "VestidoGala": 80.00,
    }
    precio_unitario = precios.get(tipo, 0.0)

    return render_template(
        "formulario_compra.html",
        talla=talla, color=color, tipo=tipo, precio_unitario=precio_unitario
    )

@main.route("/enviar_pedido", methods=["POST"])
def enviar_pedido():
    try:
        nombre          = request.form["nombre"]
        direccion       = request.form["direccion"]
        telefono        = request.form["telefono"]
        talla           = request.form["talla"]
        color           = request.form["color"]
        tipo            = request.form["tipo"]
        cantidad        = int(request.form["cantidad"])
        precio_unitario = float(request.form["precio_unitario"])
        total           = cantidad * precio_unitario

        compra = Compra(
            nombre_cliente=nombre,
            direccion=direccion,
            telefono=telefono,
            producto=f"{tipo} - talla {talla}, Color {color}",
            cantidad=cantidad,
            total=total
        )
        db.session.add(compra)
        db.session.commit()
        return render_template(
            "pedido_exitoso.html",
            nombre=nombre, tipo=tipo, talla=talla, color=color, total=total
        )
    except Exception as e:
        db.session.rollback()
        flash(f"Error al procesar el pedido: {e}", "danger")
        return redirect(url_for("main.inicio"))

# ===================  AUTENTICACIÓN  ===================

@main.route("/crear_usuario", methods=["GET", "POST"])
def crear_usuario():
    if request.method == "POST":
        nombre_usuario = request.form.get("usuario", "").strip().lower()
        contrasena     = request.form.get("contrasena", "")

        if not nombre_usuario or not contrasena:
            flash("Usuario y contraseña son obligatorios", "danger")
            return redirect(url_for("main.crear_usuario"))

        if Usuario.query.filter_by(nombre_usuario=nombre_usuario).first():
            flash("El usuario ya existe", "warning")
            return redirect(url_for("main.crear_usuario"))

        nuevo = Usuario(
            nombre_usuario=nombre_usuario,
            contrasena_hash=generate_password_hash(contrasena)
        )
        db.session.add(nuevo)
        db.session.commit()
        flash("Usuario creado. Ahora inicia sesión.", "success")
        return redirect(url_for("main.login"))

    return render_template("crear.html")  # tu template de registro

@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        nombre_usuario = request.form.get("usuario", "").strip().lower()
        contrasena     = request.form.get("contrasena", "")

        usuario = Usuario.query.filter_by(nombre_usuario=nombre_usuario).first()
        if usuario and check_password_hash(usuario.contrasena_hash, contrasena):
            # ✅ Guardar sesión
            session["user_id"]  = usuario.id
            session["username"] = usuario.nombre_usuario
            flash("Has iniciado sesión correctamente", "success")
            return redirect(url_for("main.inicio"))

        flash("Usuario o contraseña incorrectos", "danger")
        return redirect(url_for("main.login"))

    return render_template("login.html")  # tu template de login

@main.route("/logout")
@login_required
def logout():
    session.clear()
    flash("Sesión cerrada", "info")
    return redirect(url_for("main.login"))

@main.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", username=session.get("username"))

# ===================  UTILIDADES BD  ===================

@main.route("/init-db")
def init_db():
    db.create_all()
    return "Tablas creadas correctamente ✅"

# ===================  PASARELA SIMULADA  ===================

@main.route("/pay", methods=["GET"])
def pay():
    amount = request.args.get("amount", 0)
    return render_template("pay.html", amount=amount)

@main.route("/process_payment", methods=["POST"])
def process_payment():
    nombre = request.form.get("nombre")
    card_number = request.form.get("card_number", "").replace(" ", "")
    exp = request.form.get("exp")
    cvv = request.form.get("cvv")
    try:
        amount = float(request.form.get("amount", 0))
    except ValueError:
        amount = 0.0

    if not (nombre and card_number and exp and cvv and amount > 0):
        flash("Datos incompletos del pago.", "danger")
        return redirect(url_for("main.pay", amount=amount))

    time.sleep(1)
    is_success = (random.random() < 0.9)

    tx = Transaction(
        tx_id=_gen_tx_id(), amount=amount, currency="USD",
        status="success" if is_success else "failed", method="card_fake",
        card_last4=_mask_card(card_number),
        card_brand=("VISA" if card_number.startswith("4")
                    else "MC" if card_number.startswith("5")
                    else "UNKNOWN")
    )
    db.session.add(tx)
    db.session.commit()

    return redirect(url_for("main.payment_result", tx_id=tx.tx_id))

@main.route("/payment_result/<tx_id>")
def payment_result(tx_id):
    tx = Transaction.query.filter_by(tx_id=tx_id).first_or_404()
    return render_template("payment_result.html", tx=tx)

# --- RUTA TEMPORAL PARA SEMILLAR DATOS ---
import os
from flask import jsonify

@main.route("/seed")
def seed():
    # Protección simple: llámala como /seed?key=tu_clave
    key = request.args.get("key")
    if key != os.getenv("SEED_KEY", "dev"):
        return "Forbidden", 403

    inserted = {}

    # -------- BLUSONES (como tu captura) --------
    blusones = [
        {"talla": "XL", "color": "Rosado",         "tipo": "Blusones", "imagen": "imagen17.jpeg"},
        {"talla": "XL", "color": "Salmon",         "tipo": "Blusones", "imagen": "imagen15.jpeg"},
        {"talla": "XL", "color": "Blanco y Negro", "tipo": "Blusones", "imagen": "imagen18.jpeg"},
        {"talla": "XL", "color": "Gris",           "tipo": "Blusones", "imagen": "imagen16.jpeg"},
        {"talla": "L",  "color": "Rosado",         "tipo": "Blusones", "imagen": "imagen17.jpeg"},
        {"talla": "M",  "color": "Salmon",         "tipo": "Blusones", "imagen": "imagen15.jpeg"},
    ]
    for d in blusones:
        db.session.add(Bluson(**d))
    inserted["blusones"] = len(blusones)

    # -------- BLUSAS --------
    blusas = [
        {"talla": "S", "color": "Negro",  "tipo": "Blusas", "imagen": "blusa1.jpeg"},
        {"talla": "M", "color": "Blanco", "tipo": "Blusas", "imagen": "blusa2.jpeg"},
        {"talla": "L", "color": "Rojo",   "tipo": "Blusas", "imagen": "blusa3.jpeg"},
        {"talla": "XL","color": "Azul",   "tipo": "Blusas", "imagen": "blusa4.jpeg"},
    ]
    for d in blusas:
        db.session.add(Blusa(**d))
    inserted["blusas"] = len(blusas)

    # -------- VESTIDOS --------
    vestidos = [
        {"talla": "S", "color": "Negro",  "tipo": "Vestidos", "imagen": "vestido1.jpeg"},
        {"talla": "M", "color": "Rojo",   "tipo": "Vestidos", "imagen": "vestido2.jpeg"},
        {"talla": "L", "color": "Azul",   "tipo": "Vestidos", "imagen": "vestido3.jpeg"},
        {"talla": "XL","color": "Verde",  "tipo": "Vestidos", "imagen": "vestido4.jpeg"},
    ]
    for d in vestidos:
        db.session.add(Vestido(**d))
    inserted["vestidos"] = len(vestidos)

    # -------- ENTERIZOS --------
    enterizos = [
        {"talla": "S", "color": "Beige",  "tipo": "Enterizos", "imagen": "enterizo1.jpeg"},
        {"talla": "M", "color": "Negro",  "tipo": "Enterizos", "imagen": "enterizo2.jpeg"},
        {"talla": "L", "color": "Mostaza","tipo": "Enterizos", "imagen": "enterizo3.jpeg"},
        {"talla": "XL","color": "Gris",   "tipo": "Enterizos", "imagen": "enterizo4.jpeg"},
    ]
    for d in enterizos:
        db.session.add(Enterizo(**d))
    inserted["enterizos"] = len(enterizos)

    # -------- JEANS --------
    jeans = [
        {"talla": "30", "color": "Azul",     "tipo": "Jeans", "imagen": "jean1.jpeg"},
        {"talla": "32", "color": "Azul Claro","tipo": "Jeans", "imagen": "jean2.jpeg"},
        {"talla": "34", "color": "Negro",    "tipo": "Jeans", "imagen": "jean3.jpeg"},
        {"talla": "36", "color": "Gris",     "tipo": "Jeans", "imagen": "jean4.jpeg"},
    ]
    for d in jeans:
        db.session.add(Jean(**d))
    inserted["jeans"] = len(jeans)

    # -------- VESTIDOS DE GALA --------
    vestidosgala = [
        {"talla": "S",  "color": "Rojo",    "tipo": "VestidosGala", "imagen": "gala1.jpeg"},
        {"talla": "M",  "color": "Negro",   "tipo": "VestidosGala", "imagen": "gala2.jpeg"},
        {"talla": "L",  "color": "Dorado",  "tipo": "VestidosGala", "imagen": "gala3.jpeg"},
        {"talla": "XL", "color": "Verde",   "tipo": "VestidosGala", "imagen": "gala4.jpeg"},
    ]
    for d in vestidosgala:
        db.session.add(VestidoGala(**d))
    inserted["vestidosgala"] = len(vestidosgala)

    db.session.commit()
    return jsonify({"status": "ok", "inserted": inserted})
