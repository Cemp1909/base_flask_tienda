from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui'

# Configuración de la base de datos MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Cemora1909@localhost/tu_base_de_datos'  # Cambia esto
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelos
class Blusa(db.Model):
    __tablename__ = 'blusas'
    id = db.Column(db.Integer, primary_key=True)
    talla = db.Column(db.String(10))
    color = db.Column(db.String(50))
    tipo = db.Column(db.String(20))

class Bluson(db.Model):
    __tablename__ = 'blusones'
    id = db.Column(db.Integer, primary_key=True)
    talla = db.Column(db.String(10))
    color = db.Column(db.String(50))
    tipo = db.Column(db.String(20))
    imagen = db.Column(db.String(100))

class Vestido(db.Model):
    __tablename__ = 'vestidos'
    id = db.Column(db.Integer, primary_key=True)
    talla = db.Column(db.String(10))
    color = db.Column(db.String(50))
    tipo = db.Column(db.String(20))
    imagen = db.Column(db.String(100))

class Enterizo(db.Model):
    __tablename__ = 'enterizos'
    id = db.Column(db.Integer, primary_key=True)
    talla = db.Column(db.String(10))
    color = db.Column(db.String(50))
    tipo = db.Column(db.String(20))
    imagen = db.Column(db.String(100))

class Jean(db.Model):
    __tablename__ = 'jeans'
    id = db.Column(db.Integer, primary_key=True)
    talla = db.Column(db.String(10))
    color = db.Column(db.String(50))
    tipo = db.Column(db.String(20))
    imagen = db.Column(db.String(100))

class VestidoGala(db.Model):
    __tablename__ = 'vestidosgala'
    id = db.Column(db.Integer, primary_key=True)
    talla = db.Column(db.String(10))
    color = db.Column(db.String(50))
    tipo = db.Column(db.String(20))
    imagen = db.Column(db.String(100))

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
    contrasena = db.Column(db.String(128), nullable=False)

# Rutas
@app.route('/')
def inicio():
    return render_template('index.html')

@app.route('/blusas')
def blusas():
    blusas = Blusa.query.limit(6).all()
    return render_template('blusas.html', blusas=blusas)

@app.route('/blusones')
def blusones():
    blusones = Bluson.query.limit(6).all()
    return render_template('blusones.html', prendas=blusones)

@app.route('/vestidos')
def vestidos():
    vestidos = Vestido.query.limit(6).all()
    return render_template('vestidos.html', vestidos=vestidos)

@app.route('/enterizos')
def enterizos():
    enterizos = Enterizo.query.limit(6).all()
    return render_template('enterizos.html', enterizos=enterizos)

@app.route('/jeans')
def jeans():
    jeans = Jean.query.limit(6).all()
    return render_template('jeans.html', jeans=jeans)

@app.route('/vestidosgala')
def vestidosgala():
    vestidosgala = VestidoGala.query.limit(6).all()
    return render_template('vestidosgala.html', vestidosgala=vestidosgala)

# Ruta para mostrar formulario con datos del producto
@app.route('/comprar')
def comprar():
    talla = request.args.get('talla')
    color = request.args.get('color')
    tipo = request.args.get('tipo')

    # Puedes usar un diccionario con precios base por tipo
    precios = {
        'Blusones': 25.00,
        'Vestido': 40.00,
        'Enterizo': 35.00,
        'Jean': 30.00,
        'Vestido de Gala': 80.00,
        'Blusa': 20.00
    }

    precio_unitario = precios.get(tipo, 0.00)

    return render_template('formulario_compra.html',
                           talla=talla,
                           color=color,
                           tipo=tipo,
                           precio_unitario=precio_unitario)


# Ruta para procesar pedido
@app.route('/enviar_pedido', methods=['POST'])
def enviar_pedido():
    nombre = request.form['nombre']
    direccion = request.form['direccion']
    telefono = request.form['telefono']
    talla = request.form['talla']
    color = request.form['color']
    tipo = request.form['tipo']
    cantidad = int(request.form['cantidad'])
    precio_unitario = float(request.form['precio_unitario'])
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

    return render_template('pedido_exitoso.html', nombre=nombre, tipo=tipo, talla=talla,color=color,total=total)

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nombre_usuario = request.form['usuario']
        contrasena = request.form['contrasena']
        usuario = Usuario.query.filter_by(nombre_usuario=nombre_usuario).first()
        if usuario and usuario.contrasena == contrasena:
            flash('Has iniciado sesión correctamente')
            return redirect(url_for('inicio'))
        else:
            flash('Usuario o contraseña incorrectos')
            return redirect(url_for('login'))
    return render_template('inicio.html')

# Registro de usuario
@app.route('/crear_usuario', methods=['GET', 'POST'])
def crear_usuario():
    if request.method == 'POST':
        nombre_usuario = request.form['usuario']
        contrasena = request.form['contrasena']
        if Usuario.query.filter_by(nombre_usuario=nombre_usuario).first():
            flash('El usuario ya existe')
            return redirect(url_for('crear_usuario'))
        nuevo_usuario = Usuario(nombre_usuario=nombre_usuario, contrasena=contrasena)
        db.session.add(nuevo_usuario)
        db.session.commit()
        flash('Usuario creado exitosamente. Por favor inicia sesión.')
        return redirect(url_for('login'))
    return render_template('crear.html')

if __name__ == '__main__':
    app.run(debug=True)
