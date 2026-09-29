import pytest
from sqlalchemy.exc import IntegrityError

from tutor.modelos import Apoderado, DominioOA, Ejercicio, Estudiante, Unidad


def _unidad(sesion) -> Unidad:
    unidad = Unidad(
        id="4B-OA9",
        oa_texto_oficial="texto",
        descripcion_ciudadana="Sumar fracciones",
        curso=4,
        basal=True,
        anillo=1,
        orden=8,
        rango_numerico={},
    )
    sesion.add(unidad)
    sesion.flush()  # sin relación ORM con Ejercicio, la unidad debe existir antes
    return unidad


def _estudiante(sesion, apoderado: Apoderado) -> Estudiante:
    estudiante = Estudiante(apoderado=apoderado, alias="Vale", curso=5, pin_hash="x")
    sesion.add(estudiante)
    return estudiante


def test_dominio_oa_parte_en_indice_05_y_nivel_2(sesion):
    """Arranque en frío de modelo_estudiante.md §4: los valores iniciales vienen de la base."""
    unidad = _unidad(sesion)
    estudiante = _estudiante(sesion, Apoderado(email="a@ejemplo.cl", password_hash="x"))
    sesion.flush()

    dominio = DominioOA(estudiante_id=estudiante.id, unidad_id=unidad.id)
    sesion.add(dominio)
    sesion.flush()
    sesion.refresh(dominio)

    assert float(dominio.indice) == 0.5
    assert dominio.nivel_actual == 2


def test_un_apoderado_tiene_un_solo_estudiante(sesion):
    apoderado = Apoderado(email="b@ejemplo.cl", password_hash="x")
    _estudiante(sesion, apoderado)
    sesion.flush()

    sesion.add(Estudiante(apoderado_id=apoderado.id, alias="Tomás", curso=4, pin_hash="x"))
    with pytest.raises(IntegrityError):
        sesion.flush()


def test_el_correo_no_distingue_mayusculas(sesion):
    sesion.add(Apoderado(email="Correo@Ejemplo.cl", password_hash="x"))
    sesion.flush()

    sesion.add(Apoderado(email="correo@ejemplo.cl", password_hash="x"))
    with pytest.raises(IntegrityError):
        sesion.flush()


def _ejercicio(**cambios) -> Ejercicio:
    datos = dict(
        unidad_id="4B-OA9",
        nivel=2,
        fuente="llm",
        enunciado="Calcula 1/4 + 2/4.",
        formato_respuesta="fraccion",
        respuesta_final="3/4",
        solucion_referencia=["Se suman los numeradores."],
        pistas=["p1", "p2", "p3"],
    )
    datos.update(cambios)
    return Ejercicio(**datos)


def test_ejercicio_servible_exige_tres_pistas(sesion):
    _unidad(sesion)
    sesion.add(_ejercicio(pistas=["solo una"]))

    with pytest.raises(IntegrityError):
        sesion.flush()


def test_ejercicio_gold_no_necesita_pistas(sesion):
    _unidad(sesion)
    sesion.add(_ejercicio(fuente="gold", uso_gold="validacion", pistas=[]))
    sesion.flush()


def test_ejercicio_parametrico_exige_plantilla(sesion):
    _unidad(sesion)
    sesion.add(_ejercicio(fuente="parametrica"))

    with pytest.raises(IntegrityError):
        sesion.flush()
