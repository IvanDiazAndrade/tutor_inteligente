from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from tutor.progreso import EstadoDominio, banda, estrellas, para_repasar, unidad_sugerida

AHORA = datetime(2026, 9, 29, 12, tzinfo=UTC)


@dataclass
class U:
    id: str
    curso: int
    orden: int


def dominio(indice: str, dias: int = 1) -> EstadoDominio:
    return EstadoDominio(Decimal(indice), AHORA - timedelta(days=dias))


def test_bandas_con_los_umbrales_04_y_08():
    assert banda(Decimal("0.399")) == "Empezando"
    assert banda(Decimal("0.4")) == "Practicando"
    assert banda(Decimal("0.799")) == "Practicando"
    assert banda(Decimal("0.8")) == "Dominado"


def test_estrellas_cero_si_la_unidad_no_se_ha_iniciado():
    assert estrellas(None) == 0
    assert estrellas(dominio("0.2")) == 1
    assert estrellas(dominio("0.9")) == 3


def test_para_repasar_solo_con_avance_real_y_mas_de_21_dias():
    assert para_repasar(dominio("0.6", dias=22), AHORA)
    assert not para_repasar(dominio("0.6", dias=20), AHORA)
    # Una unidad apenas tocada no "se oxida": sigue pendiente, no para repasar.
    assert not para_repasar(dominio("0.3", dias=60), AHORA)


UNIDADES = [U("4B-OA1", 4, 1), U("4B-OA2", 4, 2), U("5B-OA1", 5, 1), U("5B-OA3", 5, 2)]


def test_sugerida_prioriza_la_unidad_para_repasar_mas_antigua():
    dominios = {"5B-OA1": dominio("0.7", dias=30), "5B-OA3": dominio("0.5", dias=25)}
    assert unidad_sugerida(UNIDADES, dominios, AHORA, curso=5).id == "5B-OA1"


def test_sugerida_luego_la_iniciada_con_menor_indice():
    dominios = {"5B-OA1": dominio("0.55"), "5B-OA3": dominio("0.3")}
    assert unidad_sugerida(UNIDADES, dominios, AHORA, curso=5).id == "5B-OA3"


def test_sugerida_nueva_es_la_siguiente_de_su_curso_no_de_uno_anterior():
    """Paso 3 de §5: las unidades de 4° sin iniciar no se sugieren a un estudiante de 5°."""
    dominios = {"5B-OA1": dominio("0.9")}
    assert unidad_sugerida(UNIDADES, dominios, AHORA, curso=5).id == "5B-OA3"


def test_sin_nada_que_sugerir():
    dominios = {u.id: dominio("0.9") for u in UNIDADES}
    assert unidad_sugerida(UNIDADES, dominios, AHORA, curso=5) is None
