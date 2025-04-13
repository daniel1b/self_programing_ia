import pytest
from src.main import calcula_total_com_taxa

@pytest.mark.integration
def test_calcula_total_com_taxa():
    valor = 200
    taxa = 5  # 5%
    resultado_esperado = 210.0
    assert calcula_total_com_taxa(valor, taxa) == resultado_esperado
