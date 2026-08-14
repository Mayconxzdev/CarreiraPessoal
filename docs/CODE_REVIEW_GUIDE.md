# Guia rápido de revisão técnica

Este repositório é uma edição pública e sanitizada do CarreiraPessoal. Se você chegou aqui para avaliar como eu penso e implemento, estes são os pontos que eu abriria primeiro.

## 1. Direção profissional sem depender de LLM

[`../examples/career_goal.py`](../examples/career_goal.py)

O Career Goal existe para resolver um problema que matching por palavras-chave não resolve sozinho: uma vaga pode ser tecnicamente compatível e ainda assim puxar a busca para uma direção profissional que o usuário não quer.

## 2. Afirmações precisam de evidência

[`../examples/evidence_guard.py`](../examples/evidence_guard.py)

O EvidenceGuard é uma proteção contra currículo “otimizado” que começa a inventar ou inflar informação. Claims com métricas, liderança, senioridade ou produção recebem tratamento mais conservador e precisam estar sustentados por fatos ou projetos atuais.

A regra de produto aqui foi simples: **melhor perder uma keyword do que criar uma experiência que eu não tenho**.

## 3. Currículo é roteado, não fabricado

[`../examples/resume_router.py`](../examples/resume_router.py)

O Resume Router usa perfil, evidências e contexto da vaga para decidir o que pode ser aproveitado. IA pode ajudar na redação, mas não é a fonte de verdade profissional.

## 4. Arquitetura e decisões

- [`ARCHITECTURE.md`](ARCHITECTURE.md)
- [`DECISIONS.md`](DECISIONS.md)
- [`PRIVACY.md`](PRIVACY.md)
- [`TESTING.md`](TESTING.md)

## Sobre os exemplos

Os módulos de `examples/` foram extraídos e sanitizados da aplicação completa. Eles preservam a lógica que quero mostrar, mas **não formam um pacote standalone**: imports como `app.models` e alguns serviços pertencem ao workspace privado.

Isso é intencional. O aplicativo completo contém meu perfil, candidaturas, histórico e integrações que não devem ser publicados só para tornar o repositório maior.

## Estado da versão completa usada como referência

```text
CarreiraPessoal 12.5.2
283/283 testes Python aprovados
6/6 validações adicionais aprovadas
compileall aprovado
```
