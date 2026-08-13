# Arquitetura — Carreira Pessoal 12

## Visão

```text
Tauri / navegador local
        │
React + TypeScript UI
        │ HTTP localhost
Carreira Engine (FastAPI)
 ├─ scheduler + queue/workers
 ├─ source engine
 ├─ validation/liveness
 ├─ matching + opportunity value
 ├─ applications + evidence bundle
 ├─ resume/evidence/answers
 ├─ Capability Broker
 ├─ Resource Manager
 └─ AI Gateway / Model Router
        │
SQLite + arquivos locais
```

O processo visível é um único aplicativo. O Tauri inicia o sidecar `carreira-engine.exe`; API, scheduler e worker convivem na engine.

## Zero-dependency baseline

Uma instalação limpa precisa funcionar sem recurso externo. As capacidades obrigatórias são `job_discovery`, `job_validation`, `text_matching` e `scheduler`. Recursos opcionais entram como capacidades adicionais.

## Capability Broker

Detecta hardware e recursos conhecidos sem port scan agressivo. O sistema raciocina em capacidades (`chat`, `embeddings`, `web_search`, `containers`) e não em marcas. Detectores específicos existem apenas na borda.

## Resource Manager

Gerencia extras a partir de `app/default_data/resources.yaml`:

`detectar → resolver dependências → instalar → configurar → verificar → ativar`

Instalações externas usam canal estável suportado e health-check. Estado fica em `storage/resources/resource_state.json`.

## AI Gateway

Providers podem ser autodetectados localmente ou cadastrados no banco. Adapters iniciais: OpenAI-compatible e Anthropic-compatible. A seleção considera capacidades, política, local/nuvem e prioridade.

A IA não decide elegibilidade objetiva nem altera evidências sem gate humano.

## Dados

Mutable data fica em `%LOCALAPPDATA%\CarreiraPessoal`. Assets de aplicação ficam no pacote. Esse corte é obrigatório para PyInstaller/Tauri e upgrades.

## Segurança

- localhost only;
- token separado para extensão;
- secret vault para chaves;
- redaction de PII para nuvem quando habilitado;
- conteúdo de vaga tratado como não confiável;
- submit final humano.
