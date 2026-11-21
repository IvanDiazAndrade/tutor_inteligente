"""Generador paramétrico (AD-9; modelo_dominio.md §4): registro de las plantillas.

Las piezas comunes están en `base`; las plantillas, en un módulo por curso. Una plantilla nueva
se agrega a PLANTILLAS y la prueba común (tests/test_plantillas.py) la verifica sola.
"""

from tutor.dominio.plantillas.base import EjercicioGenerado, Plantilla, menciona
from tutor.dominio.plantillas.cuarto import (
    CalculoMentalTablas,
    ConceptoFraccion,
    Division2x1,
    Multiplicacion3x1,
    NumerosHasta10000,
    SumaIgualDenominador,
    SumaRestaHasta1000,
)
from tutor.dominio.plantillas.quinto import (
    CompararDecimales,
    DivisionConResto,
    FraccionDecimal,
    FraccionesDistintoDenominador,
    FraccionesEquivalentes,
    Multiplicacion2x2,
    NumerosGrandes,
    OperatoriaCombinada,
    SumaRestaDecimales,
)
from tutor.dominio.plantillas.sexto import DecimalesPorNatural, ImpropiasYMixtos, SumaRestaMixtos

PLANTILLAS: dict[str, Plantilla] = {
    p.id: p
    for p in (
        DivisionConResto(),
        SumaIgualDenominador(),
        CalculoMentalTablas(),
        SumaRestaHasta1000(),
        Multiplicacion3x1(),
        Division2x1(),
        Multiplicacion2x2(),
        OperatoriaCombinada(),
        FraccionesDistintoDenominador(),
        SumaRestaDecimales(),
        DecimalesPorNatural(),
        NumerosHasta10000(),
        ConceptoFraccion(),
        NumerosGrandes(),
        FraccionesEquivalentes(),
        FraccionDecimal(),
        CompararDecimales(),
        ImpropiasYMixtos(),
        SumaRestaMixtos(),
    )
}

__all__ = ["PLANTILLAS", "EjercicioGenerado", "Plantilla", "menciona"]
