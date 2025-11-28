"""
Registro de simulations - mapeo de IDs a instancias.
"""
from simulations.base import PlaceholderSim
from simulations.binary_search import BinarySearchSim
from simulations.sequential_search import SequentialSearchSim
from simulations.hash_mod import HashModSim
from simulations.hash_square import HashSquareSim
from simulations.hash_trunc import HashTruncSim
from simulations.hash_fold import HashFoldSim


def make_placeholders():
    """Crea placeholders para todos los temas sin implementar."""
    return {
        "1.1.B": PlaceholderSim("1.1.B", "Búsqueda Indizada"),
        "1.2.A.1": PlaceholderSim("1.2.A.1", "Árboles de búsqueda digital"),
        "1.2.A.2": PlaceholderSim("1.2.A.2", "Tries de búsquedas por residuos"),
        "1.2.A.3": PlaceholderSim("1.2.A.3", "Árboles por residuos múltiples"),
        "1.2.A.4": PlaceholderSim("1.2.A.4", "Árboles de Huffman"),
        "1.2.B.1": PlaceholderSim("1.2.B.1", "Métodos elementales"),
        "1.2.B.2": PlaceholderSim("1.2.B.2", "Métodos de la rejilla"),
        "1.2.B.3": PlaceholderSim("1.2.B.3", "Arreglos 2D"),
        "1.3.1": PlaceholderSim("1.3.1", "Búsquedas Externas: Secuencial"),
        "1.3.2": PlaceholderSim("1.3.2", "Búsquedas Externas: Binaria"),
        "1.3.3.A": PlaceholderSim("1.3.3.A", "Función Módulo"),
        "1.3.3.B": PlaceholderSim("1.3.3.B", "Función Cuadrado"),
        "1.3.3.C": PlaceholderSim("1.3.3.C", "Función Truncamiento"),
        "1.3.3.D": PlaceholderSim("1.3.3.D", "Función Plegamiento"),
        "1.3.3.E": PlaceholderSim("1.3.3.E", "Transferencia de base - conversión"),
        "1.4.1.A": PlaceholderSim("1.4.1.A", "Expansiones parciales"),
        "1.4.1.B": PlaceholderSim("1.4.1.B", "Expansiones totales"),
        "1.4.1.C": PlaceholderSim("1.4.1.C", "Reducción Parcial"),
        "1.4.1.D": PlaceholderSim("1.4.1.D", "Reducción Total"),
        "1.5.1.A": PlaceholderSim("1.5.1.A", "Primarios"),
        "1.5.1.B": PlaceholderSim("1.5.1.B", "Secundarios"),
        "1.5.1.C": PlaceholderSim("1.5.1.C", "Agrupación"),
        "1.5.1.D": PlaceholderSim("1.5.1.D", "Denso"),
        "1.5.1.E": PlaceholderSim("1.5.1.E", "No denso"),
        "1.5.2.A": PlaceholderSim("1.5.2.A", "Montado sobre primario"),
        "1.5.2.B": PlaceholderSim("1.5.2.B", "Montado sobre secundario"),
        "1.5.2.C": PlaceholderSim("1.5.2.C", "Denso"),
        "1.5.2.D": PlaceholderSim("1.5.2.D", "No denso"),
    }


# Registro final de simulaciones
SIM_REGISTRY = {
    "1.1.C": BinarySearchSim(),
    "1.1.A": SequentialSearchSim(),
    "1.1.D.1": HashModSim(),
    "1.1.D.2": HashSquareSim(),
    "1.1.D.3": HashTruncSim(),
    "1.1.D.4": HashFoldSim(),
    **make_placeholders()
}
