"""Test Harness do TaskAnalyzer (pytest).

Traduz diretamente os cenários de aceite do contrato SDD em testes
automatizados:

    - Cenário 1 (Sucesso): cálculo correto das métricas, geral e por prioridade.
    - Cenário 2 (Exceção/Erro): entradas inválidas disparam TaskValidationError.
    - Casos de borda: entrada vazia e apenas pendentes retornam 0.0 nas médias,
      sem lançar exceções não tratadas.

Padrão adotado: Arrange-Act-Assert; exceções validadas com ``pytest.raises``.
"""

from datetime import datetime, timezone

import pytest

from task_analyzer import Tarefa, TaskValidationError, analyze_tasks


def _utc(ano: int, mes: int, dia: int, hora: int = 0, minuto: int = 0) -> datetime:
    """Cria um datetime em UTC para uso nas fixtures de teste."""
    return datetime(ano, mes, dia, hora, minuto, tzinfo=timezone.utc)


@pytest.fixture
def tarefas_validas() -> list[Tarefa]:
    """Conjunto válido com concluídas, pendente e cancelada.

    Durações das concluídas: T1=2h (alta, no prazo), T2=4h (media, atrasada),
    T3=6h (alta, no prazo). Média geral esperada = 4.0h; atraso = 1/3 = 33.33%.
    """
    return [
        Tarefa(1, "alta", "concluida", _utc(2026, 1, 1, 8), _utc(2026, 1, 1, 12),
               data_inicio=_utc(2026, 1, 1, 9), data_conclusao=_utc(2026, 1, 1, 11)),
        Tarefa(2, "media", "concluida", _utc(2026, 1, 1, 8), _utc(2026, 1, 1, 12),
               data_inicio=_utc(2026, 1, 1, 10), data_conclusao=_utc(2026, 1, 1, 14)),
        Tarefa(3, "alta", "concluida", _utc(2026, 1, 2, 8), _utc(2026, 1, 2, 20),
               data_inicio=_utc(2026, 1, 2, 8), data_conclusao=_utc(2026, 1, 2, 14)),
        Tarefa(4, "baixa", "pendente", _utc(2026, 1, 1, 8), _utc(2026, 1, 5, 12)),
        Tarefa(5, "media", "cancelada", _utc(2026, 1, 1, 8), _utc(2026, 1, 3, 12)),
    ]


# --------------------------- Cenário 1 — Sucesso ---------------------------

def test_cenario1_metricas_gerais(tarefas_validas: list[Tarefa]) -> None:
    resultado = analyze_tasks(tarefas_validas)
    assert resultado["total_tarefas"] == 5
    assert resultado["total_concluidas"] == 3
    assert resultado["total_pendentes"] == 1
    assert resultado["tempo_medio_conclusao_horas"] == 4.0   # (2 + 4 + 6) / 3
    assert resultado["taxa_atraso_percentual"] == 33.33       # 1 de 3 atrasada


def test_cenario1_indicadores_por_prioridade(tarefas_validas: list[Tarefa]) -> None:
    indicadores = analyze_tasks(tarefas_validas)["indicadores_por_prioridade"]
    assert indicadores["alta"]["tempo_medio_conclusao_horas"] == 4.0   # (2 + 6) / 2
    assert indicadores["alta"]["taxa_atraso_percentual"] == 0.0
    assert indicadores["media"]["tempo_medio_conclusao_horas"] == 4.0
    assert indicadores["media"]["taxa_atraso_percentual"] == 100.0
    assert indicadores["baixa"]["tempo_medio_conclusao_horas"] == 0.0
    assert indicadores["baixa"]["taxa_atraso_percentual"] == 0.0


def test_atraso_contabilizado_corretamente() -> None:
    tarefas = [
        Tarefa(1, "alta", "concluida", _utc(2026, 1, 1, 8), _utc(2026, 1, 1, 10),
               data_inicio=_utc(2026, 1, 1, 8), data_conclusao=_utc(2026, 1, 1, 12)),
        Tarefa(2, "alta", "concluida", _utc(2026, 1, 1, 8), _utc(2026, 1, 1, 20),
               data_inicio=_utc(2026, 1, 1, 8), data_conclusao=_utc(2026, 1, 1, 12)),
    ]
    assert analyze_tasks(tarefas)["taxa_atraso_percentual"] == 50.0


def test_canceladas_sao_ignoradas(tarefas_validas: list[Tarefa]) -> None:
    sem_cancelada = [t for t in tarefas_validas if t.status != "cancelada"]
    com_cancelada = analyze_tasks(tarefas_validas)
    assert com_cancelada["total_concluidas"] == 3
    assert (
        com_cancelada["tempo_medio_conclusao_horas"]
        == analyze_tasks(sem_cancelada)["tempo_medio_conclusao_horas"]
    )


# ----------------------- Cenário 2 — Exceção / Erro ------------------------

def test_cenario2_datas_inconsistentes() -> None:
    tarefa = Tarefa(1, "alta", "concluida", _utc(2026, 1, 10), _utc(2026, 1, 20),
                    data_inicio=_utc(2026, 1, 10), data_conclusao=_utc(2026, 1, 5))
    with pytest.raises(TaskValidationError):
        analyze_tasks([tarefa])


def test_cenario2_status_invalido() -> None:
    tarefa = Tarefa(1, "alta", "finalizada", _utc(2026, 1, 1), _utc(2026, 1, 2))
    with pytest.raises(TaskValidationError):
        analyze_tasks([tarefa])


def test_cenario2_prioridade_invalida() -> None:
    tarefa = Tarefa(1, "urgente", "pendente", _utc(2026, 1, 1), _utc(2026, 1, 2))
    with pytest.raises(TaskValidationError):
        analyze_tasks([tarefa])


def test_cenario2_concluida_sem_datas() -> None:
    tarefa = Tarefa(1, "alta", "concluida", _utc(2026, 1, 1), _utc(2026, 1, 2))
    with pytest.raises(TaskValidationError):
        analyze_tasks([tarefa])


# --------------------------- Casos de borda --------------------------------

def test_borda_lista_vazia() -> None:
    resultado = analyze_tasks([])
    assert resultado["total_tarefas"] == 0
    assert resultado["total_concluidas"] == 0
    assert resultado["total_pendentes"] == 0
    assert resultado["tempo_medio_conclusao_horas"] == 0.0
    assert resultado["taxa_atraso_percentual"] == 0.0


def test_borda_apenas_pendentes() -> None:
    tarefas = [
        Tarefa(1, "baixa", "pendente", _utc(2026, 1, 1), _utc(2026, 1, 5)),
        Tarefa(2, "alta", "pendente", _utc(2026, 1, 1), _utc(2026, 1, 5)),
    ]
    resultado = analyze_tasks(tarefas)
    assert resultado["total_pendentes"] == 2
    assert resultado["total_concluidas"] == 0
    assert resultado["tempo_medio_conclusao_horas"] == 0.0
    assert resultado["taxa_atraso_percentual"] == 0.0
