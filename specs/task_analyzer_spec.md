# Especificação SDD — TaskAnalyzer

> Contrato executável (Spec-Driven Development) do módulo **TaskAnalyzer**.
> Fonte da verdade para o código em `src/task_analyzer.py` e para os testes em
> `tests/test_harness.py`. Transposta da Fase 1 e refinada conforme os
> requisitos da Fase 2 (nomes de função/exceção, unidade em horas, contagens e
> tratamento de entrada vazia).

## 1. Propósito

Módulo puramente analítico que recebe uma lista de tarefas e retorna métricas
de produtividade. **Não persiste dados** e **não possui interface gráfica**.

## 2. Contrato de Interface

### 2.1 Função pública

```python
def analyze_tasks(tarefas: list[Tarefa]) -> dict[str, Any]: ...
```

### 2.2 Entrada — `Tarefa`

| Campo | Tipo | Obrigatório | Restrições |
|---|---|---|---|
| `id_tarefa` | `int` | Sim | `> 0`. |
| `prioridade` | `str` (enum) | Sim | `"baixa"`, `"media"`, `"alta"`. |
| `status` | `str` (enum) | Sim | `"concluida"`, `"pendente"`, `"cancelada"`. |
| `data_criacao` | `datetime` (UTC) | Sim | — |
| `prazo` | `datetime` (UTC) | Sim | — |
| `titulo` | `str \| None` | Não | — |
| `data_inicio` | `datetime \| None` | Condicional | Obrigatória quando `status = "concluida"`. |
| `data_conclusao` | `datetime \| None` | Condicional | Obrigatória quando `status = "concluida"`. |

### 2.3 Saída

Dicionário com:

| Campo | Tipo | Descrição |
|---|---|---|
| `total_tarefas` | `int` | Total de tarefas recebidas na entrada. |
| `total_concluidas` | `int` | Quantidade de tarefas com `status = "concluida"`. |
| `total_pendentes` | `int` | Quantidade de tarefas com `status = "pendente"`. |
| `tempo_medio_conclusao_horas` | `float` | Tempo médio de conclusão, em horas, das concluídas. |
| `taxa_atraso_percentual` | `float` | Percentual de concluídas entregues após o prazo. |
| `indicadores_por_prioridade` | `dict` | `tempo_medio_conclusao_horas` e `taxa_atraso_percentual` por prioridade. |

Todas as métricas numéricas são **arredondadas em 2 casas decimais**.

## 3. Regras de Negócio

1. Apenas tarefas `concluida` entram no cálculo de tempo médio e taxa de atraso.
2. Tempo de conclusão = `data_conclusao − data_inicio`, expresso em **horas**.
3. Tarefa **atrasada** quando `data_conclusao > prazo`.
4. Tarefas `cancelada` são ignoradas nas métricas (mas contam em `total_tarefas`).
5. Tarefas `pendente` entram apenas nas contagens, nunca em tempo ou atraso.
6. Todas as datas são tratadas em **UTC**.
7. **Prevenção de divisão por zero:** entrada vazia ou sem nenhuma tarefa
   concluída retorna `0.0` para médias e taxas — **sem lançar exceção**.
8. O módulo não assume nenhum comportamento não descrito neste contrato.

## 4. Validação e Exceção

A exceção **`TaskValidationError`** é lançada quando:

- `id_tarefa <= 0`;
- `prioridade` ou `status` fora do enum;
- datas inconsistentes: `data_inicio < data_criacao`,
  `data_conclusao < data_criacao` ou `data_conclusao < data_inicio`;
- tarefa `concluida` sem `data_inicio` ou sem `data_conclusao`.

## 5. Cenários de Aceite (Dado — Quando — Então)

**Cenário 1 — Sucesso.** Dado um conjunto de tarefas válidas (concluídas,
pendentes e canceladas), quando `analyze_tasks` é executado, então retorna as
contagens e métricas corretas, geral e por prioridade.

**Cenário 2 — Exceção/Erro.** Dado uma entrada com datas inconsistentes ou enum
inválido, quando `analyze_tasks` é executado, então dispara
`TaskValidationError` com mensagem clara.

**Casos de borda.** Entrada vazia ou apenas com pendentes retorna `0.0` nas
médias e taxas, sem exceção.
