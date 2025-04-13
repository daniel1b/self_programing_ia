def soma(a, b):
    """Soma dois números e retorna o resultado."""
    return a + b


def calcula_total_com_taxa(valor, taxa_percentual):
    """
    Simula um fluxo de integração: aplica uma taxa percentual sobre um valor.
    Por exemplo, calcula_total_com_taxa(100, 10) retorna 110.0
    """
    taxa = valor * (taxa_percentual / 100)
    return valor + taxa
