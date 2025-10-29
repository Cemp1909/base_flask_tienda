# controllers/main_controller.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from functools import wraps
import random, time, string, os

from models import db, Compra, Transaction  # Modelos que sigues usando directamente
from services.facade import TiendaFacade     # ✅ Fachada (Facade)
from services.abstract_factory import VeranoFactory, InviernoFactory  # ✅ Abstract Factory (uso opcional en /conjunto)

main = Blueprint("main", __name__, url_prefix="")
facade = TiendaFacade()  # ✅ instancia única de la fachada para este blueprint

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

# -------- Catálogo (HTML estático por ahora) --------
@main.route("/blusas")
def blusas():
    return render_template("blusas.html")

@main.route("/blusones")
def blusones():
    return render_template("blusones.html")

@main.route("/vestidos")
def vestidos():
    return render_template("vestidos.html")

@main.route("/enterizos")
def enterizos():
    return render_template("enterizos.html")

@main.route("/jeans")
def jeans():
    return render_template("jeans.html")

@main.route("/vestidosgala")
def vestidosgala():
    return render_template("vestidosgala.html")

# -------- Compra --------
@main.route("/comprar")
def comprar():
    talla = request.args.get("talla")
    color = request.args.get("color")
    tipo  = request.args.get("tipo")

    precios = {
        "Blusas": 20.00,
        "Blusones": 25.00,
        "Vestidos": 40.00,
        "Enterizos": 35.00,
        "Jeans": 30.00,
        "Vestidos de Gala": 80.00,
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

# ===================  AUTENTICACIÓN  (vía FACHADA)  ===================

@main.route("/crear_usuario", methods=["GET", "POST"])
def crear_usuario():
    if request.method == "POST":
        usuario    = (request.form.get("usuario") or "").strip().lower()
        email      = (request.form.get("email") or "").strip().lower()
        contrasena = request.form.get("contrasena") or ""
        rol        = (request.form.get("rol") or "cliente").strip().lower()

        if not usuario or not email or not contrasena:
            flash("Usuario, email y contraseña son obligatorios.", "danger")
            return redirect(url_for("main.crear_usuario"))

        u = facade.registrar_usuario(usuario=usuario, email=email, contrasena=contrasena, rol=rol)
        if u:
            flash("Usuario creado. Ahora inicia sesión. ✅", "success")
            return redirect(url_for("main.login"))
        else:
            flash("El usuario o el correo ya existen. ❌", "warning")
            return redirect(url_for("main.crear_usuario"))

    # OJO: usa tu template real de registro; si el tuyo se llama 'crear.html', déjalo así
    return render_template("crear_usuario.html")

@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario_o_email = (request.form.get("usuario") or "").strip().lower()
        contrasena      = request.form.get("contrasena") or ""

        u = facade.iniciar_sesion(usuario_o_email, contrasena)
        if u:
            session["user_id"]  = u.id
            session["username"] = u.nombre_usuario
            flash("Has iniciado sesión correctamente ✅", "success")
            return redirect(url_for("main.inicio"))

        flash("Usuario o contraseña incorrectos ❌", "danger")
        return redirect(url_for("main.login"))

    # IMPORTANTE: muestra el formulario de login (no 'inicio.html')
    return render_template("inicio.html")

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
    """Solo desarrollo: crea tablas si no existen."""
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

@main.route("/db-check")
def db_check():
    try:
        from models import Usuario
        x = Usuario.query.first()
        return f"DB OK. Primer usuario: {x.nombre_usuario if x else 'ninguno'}"
    except Exception as e:
        return f"DB ERROR: {type(e).__name__}: {e}", 500

# ===================  ABSTRACT FACTORY: Conjuntos por temporada  ===================

@main.route("/conjunto", methods=["POST"])
@login_required
def crear_conjunto_temporada():
    """
    Crea un conjunto de prendas coherente según la temporada usando Abstract Factory.
    Form POST esperado: temporada (verano|invierno), talla, color, tipo, imagen?, stock?
    """
    temporada = (request.form.get("temporada") or "verano").strip().lower()
    datos = {
        "talla":  request.form.get("talla"),
        "color":  request.form.get("color"),
        "tipo":   request.form.get("tipo"),
        "imagen": request.form.get("imagen"),
        "stock":  int(request.form.get("stock", 0) or 0),
    }

    # Puedes usar la fachada para persistir en bloque
    from services.abstract_factory import crear_conjunto
    factory = VeranoFactory() if temporada == "verano" else InviernoFactory()
    prendas = crear_conjunto(factory, **datos)
    db.session.add_all(prendas)
    db.session.commit()

    flash(f"Conjunto de {temporada} creado con {len(prendas)} prendas ✅", "success")
    return redirect(url_for("main.inicio"))

# --- RUTA TEMPORAL PARA SEMILLAR DATOS (usa tus modelos originales) ---
@main.route("/seed")
def seed():
    key = request.args.get("key")
    if key != os.getenv("SEED_KEY", "dev"):
        return "Forbidden", 403

    inserted = {}
    # Puedes añadir 'stock' si tus tablas lo tienen
    from models import Blusa, Bluson, Vestido, Enterizo, Jean, VestidoGala

    blusones = [
        {"talla": "XL", "color": "Rosado",         "tipo": "Blusones", "imagen": "imagen17.jpeg", "stock": 5},
        {"talla": "XL", "color": "Salmon",         "tipo": "Blusones", "imagen": "imagen15.jpeg", "stock": 4},
        {"talla": "XL", "color": "Blanco y Negro", "tipo": "Blusones", "imagen": "imagen18.jpeg", "stock": 3},
        {"talla": "XL", "color": "Gris",           "tipo": "Blusones", "imagen": "imagen16.jpeg", "stock": 2},
        {"talla": "L",  "color": "Rosado",         "tipo": "Blusones", "imagen": "imagen17.jpeg", "stock": 2},
        {"talla": "M",  "color": "Salmon",         "tipo": "Blusones", "imagen": "imagen15.jpeg", "stock": 2},
    ]
    for d in blusones: db.session.add(Bluson(**d))
    inserted["blusones"] = len(blusones)

    blusas = [
        {"talla": "S", "color": "Negro",  "tipo": "Blusas", "imagen": "blusa1.jpeg", "stock": 10},
        {"talla": "M", "color": "Blanco", "tipo": "Blusas", "imagen": "blusa2.jpeg", "stock": 8},
        {"talla": "L", "color": "Rojo",   "tipo": "Blusas", "imagen": "blusa3.jpeg", "stock": 6},
        {"talla": "XL","color": "Azul",   "tipo": "Blusas", "imagen": "blusa4.jpeg", "stock": 4},
    ]
    for d in blusas: db.session.add(Blusa(**d))
    inserted["blusas"] = len(blusas)

    vestidos = [
        {"talla": "S", "color": "Negro",  "tipo": "Vestidos", "imagen": "vestido1.jpeg", "stock": 7},
        {"talla": "M", "color": "Rojo",   "tipo": "Vestidos", "imagen": "vestido2.jpeg", "stock": 7},
        {"talla": "L", "color": "Azul",   "tipo": "Vestidos", "imagen": "vestido3.jpeg", "stock": 5},
        {"talla": "XL","color": "Verde",  "tipo": "Vestidos", "imagen": "vestido4.jpeg", "stock": 3},
    ]
    for d in vestidos: db.session.add(Vestido(**d))
    inserted["vestidos"] = len(vestidos)

    enterizos = [
        {"talla": "S", "color": "Beige",  "tipo": "Enterizos", "imagen": "enterizo1.jpeg", "stock": 5},
        {"talla": "M", "color": "Negro",  "tipo": "Enterizos", "imagen": "enterizo2.jpeg", "stock": 5},
        {"talla": "L", "color": "Mostaza","tipo": "Enterizos", "imagen": "enterizo3.jpeg", "stock": 4},
        {"talla": "XL","color": "Gris",   "tipo": "Enterizos", "imagen": "enterizo4.jpeg", "stock": 3},
    ]
    for d in enterizos: db.session.add(Enterizo(**d))
    inserted["enterizos"] = len(enterizos)

    jeans = [
        {"talla": "30", "color": "Azul",      "tipo": "Jeans", "imagen": "jean1.jpeg", "stock": 9},
        {"talla": "32", "color": "Azul Claro","tipo": "Jeans", "imagen": "jean2.jpeg", "stock": 8},
        {"talla": "34", "color": "Negro",     "tipo": "Jeans", "imagen": "jean3.jpeg", "stock": 6},
        {"talla": "36", "color": "Gris",      "tipo": "Jeans", "imagen": "jean4.jpeg", "stock": 4},
    ]
    for d in jeans: db.session.add(Jean(**d))
    inserted["jeans"] = len(jeans)

    vestidosgala = [
        {"talla": "S",  "color": "Rojo",   "tipo": "VestidosGala", "imagen": "gala1.jpeg", "stock": 2},
        {"talla": "M",  "color": "Negro",  "tipo": "VestidosGala", "imagen": "gala2.jpeg", "stock": 2},
        {"talla": "L",  "color": "Dorado", "tipo": "VestidosGala", "imagen": "gala3.jpeg", "stock": 2},
        {"talla": "XL", "color": "Verde",  "tipo": "VestidosGala", "imagen": "gala4.jpeg", "stock": 2},
    ]
    for d in vestidosgala: db.session.add(VestidoGala(**d))
    inserted["vestidosgala"] = len(vestidosgala)

    db.session.commit()
    return jsonify({"status": "ok", "inserted": inserted})
