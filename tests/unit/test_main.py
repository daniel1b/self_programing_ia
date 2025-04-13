import pytest
from src.main import soma

@pytest.mark.unit
def test_soma_positiva():
    assert soma(2, 3) == 5

@pytest.mark.unit
def test_soma_negativa():
    assert soma(-1, -2) == -3
