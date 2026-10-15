# sdd-task-analyzer

Implementação do módulo **TaskAnalyzer** sob o paradigma **Spec-Driven
Development (SDD)**: a especificação técnica é o contrato executável, o código é
gerado por assistente de IA sob regras de governança, e a validação é feita por
testes automatizados com revisão (homologação) humana.

> Entrega Intermediária (Fase 2) — Bootcamp III.

## O que o TaskAnalyzer faz

Recebe uma lista de tarefas e calcula métricas de produtividade: total de
tarefas, concluídas e pendentes, tempo médio de conclusão (horas), taxa de
atraso e os mesmos indicadores por prioridade. É um módulo puramente analítico —
não persiste dados e não possui interface.

## Estrutura do repositório

```
sdd-task-analyzer/
├── README.md              # Este arquivo
├── CONTEXT_RULES.md       # Regras de governança para a IA
├── requirements.txt       # Dependências autorizadas (pytest)
├── .gitignore
├── conftest.py            # Torna src/ importável nos testes
├── specs/
│   └── task_analyzer_spec.md   # Contrato SDD (fonte da verdade)
├── src/
│   └── task_analyzer.py        # Código gerado via IA e homologado
└── tests/
    └── test_harness.py         # Suíte de testes (pytest)
```

## Como executar

Requisitos: **Python 3.11+**.

```bash
# 1. Criar e ativar o ambiente virtual
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Rodar os testes
pytest -v
```

Resultado esperado: **100% dos testes aprovados**.

## Fluxo SDD adotado

1. **Especificar** — contrato em `specs/task_analyzer_spec.md`.
2. **Governar** — regras em `CONTEXT_RULES.md` fornecidas ao assistente de IA.
3. **Gerar** — código em `src/task_analyzer.py` produzido via IA sob o contrato.
4. **Validar** — `tests/test_harness.py` cobrindo os Cenários 1, 2 e casos de borda.
5. **Homologar** — revisão crítica humana antes do merge (Pull Request).

## Autor

Marcos Vogado — Bootcamp III.
