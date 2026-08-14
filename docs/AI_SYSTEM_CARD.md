# AI System Card — CarreiraPessoal

Este documento registra **onde a IA entra, onde ela não entra e quais controles impedem que uma saída probabilística vire afirmação profissional ou candidatura automática**.

## Papel da IA

O núcleo do CarreiraPessoal funciona sem provedor de IA. Descoberta, normalização, deduplicação, Career Goal, perfil versionado, EvidenceGuard, acompanhamento e envio final manual não dependem de uma LLM para existir.

Quando habilitada, IA local ou externa pode apoiar tarefas como:

- interpretação e resumo de descrições de vagas;
- comparação semântica entre vaga, objetivo e evidências profissionais;
- apoio à preparação de currículo e respostas com base no perfil versionado;
- classificação ou enriquecimento de informações em que um modelo agrega valor sobre regras puramente determinísticas.

## Fronteira de decisão

A IA **não pode**:

- criar experiência profissional, cargo, senioridade, certificação ou métrica ausente das evidências;
- transformar aderência técnica em decisão automática de carreira;
- enviar candidatura;
- contornar CAPTCHA, termos do site ou confirmação final do usuário;
- transformar uma sugestão em fato sem passar pelas regras de evidência aplicáveis.

O `EvidenceGuard` existe justamente para separar texto plausível de afirmação sustentada pelo perfil profissional versionado.

## Dados e privacidade

A edição pública não contém currículo pessoal completo, candidaturas reais, credenciais, banco de uso, dados de terceiros ou histórico privado. A versão completa mantém esses elementos fora do snapshot público.

O aplicativo pode usar recursos locais como Ollama/LM Studio. Quando um provedor externo é escolhido, a configuração do ambiente e a política do provedor passam a fazer parte da decisão de risco; o sistema não assume que qualquer dado pode ser enviado para qualquer serviço.

## Provedores e dependência de terceiros

A arquitetura trata IA como capacidade opcional e evita tornar um único fornecedor condição para o produto funcionar.

Princípios utilizados:

- provedor configurável em vez de contrato fixo com uma única API;
- recursos locais opcionais para cenários que pedem maior controle de dados;
- falha ou ausência da IA não bloqueia o núcleo determinístico;
- integrações externas devem ter timeout, tratamento de erro e estado explícito de indisponibilidade;
- recursos opcionais não são instalados como dependência silenciosa do produto principal.

## Riscos considerados

| Risco | Controle adotado |
| --- | --- |
| Alucinação ou claim não sustentado | perfil profissional versionado + EvidenceGuard + revisão humana |
| Vaga tecnicamente parecida, mas fora do objetivo | Career Goal separado do matching técnico |
| Dependência de provedor | IA opcional e possibilidade de execução local |
| Exposição de dados pessoais | snapshot público sanitizado; configuração consciente de provedores |
| Automação excessiva da candidatura | envio final manual e CAPTCHA/termos mantidos com o usuário |
| Drift do perfil/currículo | fatos, projetos e currículos tratados como evidências versionadas |

## Evidência e avaliação

Na versão completa v12.5.2 registrada no projeto:

- **283/283 testes Python aprovados**;
- **6/6 validações adicionais aprovadas**;
- `compileall` aprovado;
- **102 famílias ATS/plataformas reconhecidas**;
- **11 coletores diretos**.

Esses números demonstram a validação do produto e de seus contratos; **não são uma alegação de acurácia universal de LLM**. Avaliações de modelos dependem do provedor, da tarefa, do prompt, dos dados e da versão utilizados.

## Limites declarados

- IA é assistência, não fonte da verdade profissional;
- matching semântico não garante adequação cultural, salarial ou de carreira;
- a qualidade de um provedor externo pode mudar sem alteração no aplicativo;
- sites de vagas podem alterar HTML, APIs, termos e mecanismos anti-automação;
- a versão pública é sanitizada e não contém todo o workspace privado.

## Relação com a arquitetura

Leia também:

- [`ARCHITECTURE.md`](ARCHITECTURE.md) — arquitetura do produto;
- [`DECISIONS.md`](DECISIONS.md) — decisões de engenharia;
- [`PRIVACY.md`](PRIVACY.md) — privacidade e limites da edição pública;
- [`TESTING.md`](TESTING.md) — estratégia e evidências de teste.
