from werkzeug.security import check_password_hash
from sqlalchemy.exc import IntegrityError
from models import db, Usuario
from .abstract_factory import VeranoFactory, InviernoFactory, crear_conjunto

class TiendaFacade:
    """Fachada para manejar usuarios y productos."""

    # ---------- USUARIOS ----------
    def registrar_usuario(self, usuario, email, contrasena, rol="cliente"):
        nuevo = Usuario(nombre_usuario=usuario, email=email, rol=rol)
        nuevo.set_password(contrasena)
        try:
            db.session.add(nuevo)
            db.session.commit()
            return nuevo
        except IntegrityError:
            db.session.rollback()
            return None

    def iniciar_sesion(self, usuario_o_email, contrasena):
        dato = usuario_o_email.lower()
        u = Usuario.query.filter(
            (Usuario.nombre_usuario == dato) | (Usuario.email == dato)
        ).first()
        if u and check_password_hash(u.contrasena_hash, contrasena):
            return u
        return None

    # ---------- PRODUCTOS ----------
    def crear_conjunto_temporada(self, temporada, **datos):
        """Usa la fábrica adecuada para crear un conjunto de prendas."""
        factory = VeranoFactory() if temporada.lower() == "verano" else InviernoFactory()
        prendas = crear_conjunto(factory, **datos)
        db.session.add_all(prendas)
        db.session.commit()
        return prendas
