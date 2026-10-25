# sdd-task-analyzer

[![CI — TaskAnalyzer](https://github.com/MarcosVogado/sdd-task-analyzer/actions/workflows/ci.yml/badge.svg)](https://github.com/MarcosVogado/sdd-task-analyzer/actions/workflows/ci.yml)

Implementação do módulo **TaskAnalyzer** sob o paradigma **Spec-Driven
Development (SDD)**: a especificação técnica é o contrato executável, o código é
gerado por assistente de IA sob regras de governança, validado por testes
automatizados, homologado por revisão humana e entregue por uma esteira de
integração contínua com execução containerizada.

> Entrega Final (Fase 3) — Bootcamp III.

## O que o TaskAnalyzer faz

Recebe uma lista de tarefas e calcula métricas de produtividade: total de
tarefas, concluídas e pendentes, tempo médio de conclusão (horas), taxa de
atraso e os mesmos indicadores por prioridade. É um módulo puramente analítico —
não persiste dados e não possui interface.

## Estrutura do repositório

```
sdd-task-analyzer/
├── .github/
│   └── workflows/
│       └── ci.yml                   # Pipeline CI (GitHub Actions)
├── Dockerfile                       # Imagem isolada (python:3.11-slim)
├── docker-compose.yml               # Orquestração: tests e demo
├── .dockerignore
├── CONTEXT_RULES.md                 # Regras de governança para a IA
├── specs/
│   ├── system_design_document.pdf   # Documento de design do sistema (SDD)
│   ├── requirements.yaml            # Requisitos rastreáveis (requisito ↔ teste)
│   └── task_analyzer_spec.md        # Contrato SDD em texto (fonte da verdade)
├── tests/
│   └── test_harness.py              # Suíte de testes (pytest)
├── src/
│   └── task_analyzer.py             # Código gerado via IA e homologado
├── conftest.py                      # Torna src/ importável nos testes
├── requirements.txt                 # Dependências autorizadas (versão fixada)
└── README.md
```

## Como executar

### Opção 1 — Docker (recomendado, ambiente idêntico ao CI)

Requisito: Docker com Compose v2.

```bash
docker compose run --rm tests   # executa o Test Harness isolado
docker compose run --rm demo    # executa a análise de demonstração
```

Ou diretamente:

```bash
docker build -t sdd-task-analyzer .
docker run --rm sdd-task-analyzer
```

### Opção 2 — Local

Requisito: **Python 3.11+**.

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m pytest tests/test_harness.py -v
```

Resultado esperado: **10 passed (100%)**.

## Integração contínua

A cada push ou Pull Request em `main` e `develop`, o GitHub Actions:

1. Prepara `ubuntu-latest` com **Python 3.11**;
2. Instala as dependências de `requirements.txt`;
3. Executa `pytest tests/test_harness.py -v`;
4. Constrói a imagem Docker e roda a suíte dentro do container.

## Fluxo SDD adotado

1. **Especificar** — contrato em `specs/` (texto, PDF e YAML rastreável).
2. **Governar** — regras em `CONTEXT_RULES.md` fornecidas ao assistente de IA.
3. **Gerar** — código em `src/task_analyzer.py` produzido via IA sob o contrato.
4. **Validar** — `tests/test_harness.py` cobrindo cenários de aceite e bordas.
5. **Homologar** — revisão crítica humana antes do merge (Pull Request).
6. **Entregar** — CI/CD + Docker garantem reprodutibilidade e auditoria.

## Fluxo de branches

`feature/*` → PR para `develop` (CI obrigatório) → PR de release para `main` → tag.

## Autor

Marcos Vogado — Bootcamp III.
