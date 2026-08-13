# Arquitetura

```mermaid
flowchart LR
    U[Desktop Windows / Tauri 2] --> F[React + TypeScript + Vite]
    F --> A[FastAPI local / sidecar Python]
    A --> D[(SQLite / WAL / FTS5)]
    A --> S[Source Intelligence]
    A --> M[Matching + Career Goal Gate]
    A --> E[EvidenceGuard + Resume Router]
    A --> C[CRM de candidaturas]
    A --> R[Resource Manager]
    R --> L[IA local / Ollama / LM Studio]
    R --> Q[Busca semântica / Qdrant opcional]
    R --> X[SearXNG opcional]
    B[Extensão Chrome/Edge] --> A
```

## Princípios

1. **Local-first:** dados de carreira permanecem locais por padrão.
2. **Sem IA obrigatória:** descoberta, deduplicação, tracking e regras principais continuam funcionais sem LLM.
3. **Evidência antes de geração:** currículos e respostas devem usar somente fatos sustentados pelo perfil versionado.
4. **Human-in-the-loop:** o sistema prepara; a decisão e o envio final pertencem ao usuário.
5. **Adaptabilidade:** fontes, modelos e recursos externos são opcionais e substituíveis.

A documentação evita tratar integrações opcionais como dependências obrigatórias ou como evidência de uso em produção fora do ambiente pessoal.
