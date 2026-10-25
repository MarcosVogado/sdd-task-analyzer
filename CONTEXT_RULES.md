# CONTEXT_RULES — Governança de Contexto para Agentes de IA

Regras rígidas fornecidas ao assistente de IA para garantir alinhamento,
consistência e qualidade do código gerado para o módulo **TaskAnalyzer**.
Devem ser lidas em conjunto com o contrato em `specs/task_analyzer_spec.md`
e com os requisitos rastreáveis em `specs/requirements.yaml`.

## 1. Diretrizes Arquiteturais (Obrigatórias)

- **Python 3.11+** como versão mínima.
- **Type hints** em 100% das funções, métodos e parâmetros.
- Princípio **Single Responsibility (SRP)** e código limpo (**PEP 8**).
- **Docstrings** no padrão **Google style** para módulos, classes e funções.
- Funções pequenas, coesas e com um único propósito.
- Tratamento de exceções específico, com a exceção customizada
  `TaskValidationError` e mensagens claras.
- Prevenção explícita de **divisão por zero** (ver contrato, regra 7).
- **Logs estruturados** com o módulo padrão `logging`.
- Nomes de variáveis e funções descritivos.

## 2. Proibições Explícitas (Restritivas)

- ❌ Não utilizar bibliotecas externas não autorizadas (ver `requirements.txt`).
- ❌ Não alterar, remover ou adaptar os cenários de teste fornecidos.
- ❌ Não modificar a estrutura de pastas definida na especificação.
- ❌ Não persistir dados em arquivos ou bancos de dados.
- ❌ Não alterar a assinatura das funções públicas (`analyze_tasks`) sem
  autorização.
- ❌ Não gerar código sem os testes correspondentes.
- ❌ Não inserir código duplicado ou desnecessário.
- ❌ Não assumir comportamentos não especificados no contrato de negócio.

## 3. Regras de Interação com a IA

- Fornecer sempre o contexto completo (este arquivo + a especificação).
- A IA deve compreender e validar o contrato antes de gerar código.
- Em caso de dúvida, solicitar esclarecimento — nunca "alucinar" uma solução.
- Todo código gerado é revisado criticamente pelo desenvolvedor humano antes
  de ser aceito (homologação).
- Respostas que violem as proibições ou o contrato devem ser rejeitadas.

## 4. Governança de Pipeline e Infraestrutura (Fase 3)

- ❌ Não desabilitar, pular (`skip`/`xfail`) ou condicionar testes para obter
  build verde — build vermelho é sinal de violação do contrato, não um
  obstáculo a contornar.
- ❌ Não alterar `.github/workflows/ci.yml`, `Dockerfile` ou
  `docker-compose.yml` fora de Pull Request revisado.
- ❌ Não adicionar dependências sem registrá-las em `requirements.txt` com
  **versão fixada** e aprovação humana.
- ❌ Não incluir segredos, tokens ou credenciais no repositório nem na imagem.
- Toda alteração entra por `feature/*` → Pull Request para `develop` com CI
  verde; `main` recebe código apenas a partir de `develop`.
- Todo requisito novo deve ser registrado em `specs/requirements.yaml` com o
  teste que o comprova (rastreabilidade requisito ↔ teste).
- Rastreabilidade de prompts: o corpo do PR registra o assistente de IA
  utilizado e o objetivo do prompt.
