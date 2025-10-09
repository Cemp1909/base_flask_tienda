from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Blusa, Bluson, Vestido, Enterizo, Jean, VestidoGala, Compra, Usuario
# IMPORTS EXTRA (arriba con el resto)
import random, time
from models import Transaction  # para guardar la transacción simulada


main = Blueprint("main", __name__, url_prefix="")

@main.route("/")
def inicio():
    return render_template("index.html")

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

    return render_template("formulario_compra.html",
                           talla=talla, color=color, tipo=tipo, precio_unitario=precio_unitario)

@main.route("/enviar_pedido", methods=["POST"])
def enviar_pedido():
    try:
        nombre = request.form["nombre"]
        direccion = request.form["direccion"]
        telefono = request.form["telefono"]
        talla = request.form["talla"]
        color = request.form["color"]
        tipo = request.form["tipo"]
        cantidad = int(request.form["cantidad"])
        precio_unitario = float(request.form["precio_unitario"])
        total = cantidad * precio_unitario

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
        return render_template("pedido_exitoso.html",
                               nombre=nombre, tipo=tipo, talla=talla, color=color, total=total)
    except Exception as e:
        db.session.rollback()
        flash(f"Error al procesar el pedido: {e}")
        return redirect(url_for("main.inicio"))

@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        nombre_usuario = request.form["usuario"]
        contrasena = request.form["contrasena"]
        usuario = Usuario.query.filter_by(nombre_usuario=nombre_usuario).first()
        if usuario and check_password_hash(usuario.contrasena_hash, contrasena):
            flash("Has iniciado sesión correctamente")
            return redirect(url_for("main.inicio"))
        flash("Usuario o contraseña incorrectos")
        return redirect(url_for("main.login"))
    return render_template("login.html")

@main.route("/crear_usuario", methods=["GET", "POST"])
def crear_usuario():
    if request.method == "POST":
        nombre_usuario = request.form["usuario"]
        contrasena = request.form["contrasena"]

        if Usuario.query.filter_by(nombre_usuario=nombre_usuario).first():
            flash("El usuario ya existe")
            return redirect(url_for("main.crear_usuario"))

        nuevo = Usuario(
            nombre_usuario=nombre_usuario,
            contrasena_hash=generate_password_hash(contrasena)
        )
        db.session.add(nuevo)
        db.session.commit()
        flash("Usuario creado. Por favor inicia sesión.")
        return redirect(url_for("main.login"))
    return render_template("crear.html")

@main.route("/init-db")
def init_db():
    db.create_all()
    return "Tablas creadas correctamente ✅"

# --- PASARELA DE PAGO SIMULADA (dentro del blueprint main) ---

def _gen_tx_id(n=12):
    import string, random
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=n))

def _mask_card(number):
    return number[-4:] if number and len(number) >= 4 else number

@main.route("/pay", methods=["GET"])
def pay():
    """
    Muestra el formulario de pago simulado.
    Uso: /pay?amount=123.45
    """
    amount = request.args.get("amount", 0)
    return render_template("pay.html", amount=amount)

@main.route("/process_payment", methods=["POST"])
def process_payment():
    """
    Procesa el pago simulado: valida datos, crea Transaction y redirige al resultado.
    """
    nombre = request.form.get("nombre")
    card_number = request.form.get("card_number", "").replace(" ", "")
    exp = request.form.get("exp")
    cvv = request.form.get("cvv")
    try:
        amount = float(request.form.get("amount", 0))
    except ValueError:
        amount = 0.0

    if not (nombre and card_number and exp and cvv and amount > 0):
        flash("Datos incompletos del pago.")
        return redirect(url_for("main.pay", amount=amount))

    # Simulación: pequeña latencia y 90% de éxito
    time.sleep(1)
    is_success = (random.random() < 0.9)

    tx = Transaction(
        tx_id=_gen_tx_id(),
        amount=amount,
        currency="USD",
        status="success" if is_success else "failed",
        method="card_fake",
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
    """
    Muestra la página de resultado del pago simulado.
    """
    tx = Transaction.query.filter_by(tx_id=tx_id).first_or_404()
    return render_template("payment_result.html", tx=tx)

