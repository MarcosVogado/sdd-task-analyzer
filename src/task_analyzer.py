"""TaskAnalyzer — módulo de análise de tarefas e produtividade.

Implementação gerada sob o paradigma Spec-Driven Development (SDD), guiada
estritamente pelo contrato de negócio (``specs/task_analyzer_spec.md``) e pelas
regras de governança (``CONTEXT_RULES.md``).

O módulo é puramente analítico: recebe uma lista de tarefas, valida a entrada
e retorna métricas de produtividade. Não persiste dados e não possui interface.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from statistics import mean
from typing import Any

logger = logging.getLogger(__name__)

PRIORIDADES_VALIDAS: frozenset[str] = frozenset({"baixa", "media", "alta"})
STATUS_VALIDOS: frozenset[str] = frozenset({"concluida", "pendente", "cancelada"})


class TaskValidationError(Exception):
    """Exceção para entradas inválidas do TaskAnalyzer.

    Lançada quando uma tarefa viola o contrato de interface: identificador não
    positivo, prioridade/status fora do enum, campos obrigatórios ausentes em
    tarefas concluídas ou datas inconsistentes.
    """


@dataclass
class Tarefa:
    """Representa uma tarefa a ser analisada.

    Attributes:
        id_tarefa: Identificador único e positivo da tarefa.
        prioridade: Prioridade da tarefa ("baixa", "media" ou "alta").
        status: Situação da tarefa ("concluida", "pendente" ou "cancelada").
        data_criacao: Data/hora de criação (UTC).
        prazo: Prazo-limite para conclusão (UTC).
        titulo: Título descritivo opcional.
        data_inicio: Data/hora de início da execução (UTC). Obrigatória para
            tarefas concluídas.
        data_conclusao: Data/hora de conclusão (UTC). Obrigatória para tarefas
            concluídas.
    """

    id_tarefa: int
    prioridade: str
    status: str
    data_criacao: datetime
    prazo: datetime
    titulo: str | None = None
    data_inicio: datetime | None = None
    data_conclusao: datetime | None = None


def _validar_tarefa(tarefa: Tarefa) -> None:
    """Valida uma tarefa contra o contrato de interface.

    Args:
        tarefa: Tarefa a ser validada.

    Raises:
        TaskValidationError: Se a tarefa violar qualquer regra do contrato.
    """
    if tarefa.id_tarefa <= 0:
        raise TaskValidationError(
            f"id_tarefa deve ser maior que zero (recebido: {tarefa.id_tarefa})."
        )
    if tarefa.prioridade not in PRIORIDADES_VALIDAS:
        raise TaskValidationError(
            f"prioridade inválida: '{tarefa.prioridade}'. "
            f"Valores aceitos: {sorted(PRIORIDADES_VALIDAS)}."
        )
    if tarefa.status not in STATUS_VALIDOS:
        raise TaskValidationError(
            f"status inválido: '{tarefa.status}'. "
            f"Valores aceitos: {sorted(STATUS_VALIDOS)}."
        )

    if tarefa.data_inicio is not None and tarefa.data_inicio < tarefa.data_criacao:
        raise TaskValidationError(
            f"Tarefa {tarefa.id_tarefa}: data_inicio anterior à data_criacao."
        )
    if tarefa.data_conclusao is not None:
        if tarefa.data_conclusao < tarefa.data_criacao:
            raise TaskValidationError(
                f"Tarefa {tarefa.id_tarefa}: data_conclusao anterior à data_criacao."
            )
        if (
            tarefa.data_inicio is not None
            and tarefa.data_conclusao < tarefa.data_inicio
        ):
            raise TaskValidationError(
                f"Tarefa {tarefa.id_tarefa}: data_conclusao anterior à data_inicio."
            )

    if tarefa.status == "concluida" and (
        tarefa.data_inicio is None or tarefa.data_conclusao is None
    ):
        raise TaskValidationError(
            f"Tarefa {tarefa.id_tarefa}: tarefas concluídas exigem "
            "data_inicio e data_conclusao."
        )


def _metricas(concluidas: list[Tarefa]) -> dict[str, float]:
    """Calcula tempo médio (horas) e taxa de atraso (%) de tarefas concluídas.

    Retorna 0.0 para ambas as métricas quando não há tarefas concluídas,
    prevenindo divisão por zero — entrada vazia não é condição de erro.

    Args:
        concluidas: Tarefas com status "concluida" já validadas.

    Returns:
        Dicionário com ``tempo_medio_conclusao_horas`` e
        ``taxa_atraso_percentual``, arredondados em 2 casas decimais.
    """
    if not concluidas:
        return {"tempo_medio_conclusao_horas": 0.0, "taxa_atraso_percentual": 0.0}

    duracoes_horas: list[float] = []
    atrasadas = 0
    for tarefa in concluidas:
        # Garantido pela validação prévia: concluídas têm ambas as datas.
        assert tarefa.data_inicio is not None and tarefa.data_conclusao is not None
        duracao = (tarefa.data_conclusao - tarefa.data_inicio).total_seconds() / 3600
        duracoes_horas.append(duracao)
        if tarefa.data_conclusao > tarefa.prazo:
            atrasadas += 1

    return {
        "tempo_medio_conclusao_horas": round(mean(duracoes_horas), 2),
        "taxa_atraso_percentual": round(atrasadas / len(concluidas) * 100, 2),
    }


def _indicadores_por_prioridade(
    concluidas: list[Tarefa],
) -> dict[str, dict[str, float]]:
    """Calcula as métricas de conclusão agrupadas por prioridade.

    Args:
        concluidas: Tarefas com status "concluida" já validadas.

    Returns:
        Dicionário com uma entrada por prioridade ("baixa", "media", "alta"),
        cada uma com ``tempo_medio_conclusao_horas`` e ``taxa_atraso_percentual``.
    """
    indicadores: dict[str, dict[str, float]] = {}
    for prioridade in ("baixa", "media", "alta"):
        grupo = [t for t in concluidas if t.prioridade == prioridade]
        indicadores[prioridade] = _metricas(grupo)
    return indicadores


def analyze_tasks(tarefas: list[Tarefa]) -> dict[str, Any]:
    """Analisa uma lista de tarefas e retorna métricas de produtividade.

    Apenas tarefas concluídas entram no cálculo de tempo médio e taxa de
    atraso. Tarefas canceladas são ignoradas nas métricas; pendentes entram
    somente nas contagens. Entrada vazia ou sem tarefas concluídas produz
    métricas iguais a 0.0 (sem exceção).

    Args:
        tarefas: Lista de tarefas a analisar.

    Returns:
        Dicionário com ``total_tarefas``, ``total_concluidas``,
        ``total_pendentes``, ``tempo_medio_conclusao_horas``,
        ``taxa_atraso_percentual`` e ``indicadores_por_prioridade``.

    Raises:
        TaskValidationError: Se alguma tarefa violar o contrato de interface.
    """
    logger.info("Iniciando análise de %d tarefa(s).", len(tarefas))
    for tarefa in tarefas:
        _validar_tarefa(tarefa)

    concluidas = [t for t in tarefas if t.status == "concluida"]
    pendentes = [t for t in tarefas if t.status == "pendente"]
    canceladas = [t for t in tarefas if t.status == "cancelada"]
    if canceladas:
        logger.debug(
            "%d tarefa(s) cancelada(s) ignorada(s) nas métricas.", len(canceladas)
        )

    metricas_gerais = _metricas(concluidas)
    resultado: dict[str, Any] = {
        "total_tarefas": len(tarefas),
        "total_concluidas": len(concluidas),
        "total_pendentes": len(pendentes),
        "tempo_medio_conclusao_horas": metricas_gerais["tempo_medio_conclusao_horas"],
        "taxa_atraso_percentual": metricas_gerais["taxa_atraso_percentual"],
        "indicadores_por_prioridade": _indicadores_por_prioridade(concluidas),
    }
    logger.info("Análise concluída com sucesso.")
    return resultado


def _demonstracao() -> None:
    """Executa uma análise de exemplo e imprime o resultado.

    Ponto de execução para demonstração manual do módulo
    (``python src/task_analyzer.py``). Não faz parte da lógica de negócio e
    não altera o comportamento de ``analyze_tasks`` quando o módulo é importado.
    """

    def utc(ano: int, mes: int, dia: int, hora: int = 0) -> datetime:
        return datetime(ano, mes, dia, hora, tzinfo=timezone.utc)

    exemplo: list[Tarefa] = [
        Tarefa(1, "alta", "concluida", utc(2026, 1, 1, 8), utc(2026, 1, 1, 12),
               data_inicio=utc(2026, 1, 1, 9), data_conclusao=utc(2026, 1, 1, 11)),
        Tarefa(2, "media", "concluida", utc(2026, 1, 1, 8), utc(2026, 1, 1, 12),
               data_inicio=utc(2026, 1, 1, 10), data_conclusao=utc(2026, 1, 1, 14)),
        Tarefa(3, "baixa", "pendente", utc(2026, 1, 1, 8), utc(2026, 1, 5, 12)),
    ]

    resultado = analyze_tasks(exemplo)
    print(json.dumps(resultado, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    _demonstracao()
