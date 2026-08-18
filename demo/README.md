# Demonstração pública autocontida

Esta pasta permite avaliar, sem banco de dados, credenciais, serviços externos ou código privado, três contratos de decisão usados como referência no CarreiraPessoal:

1. **Career Goal** — separa aderência técnica de direção profissional;
2. **EvidenceGuard** — bloqueia afirmações que não possuem evidência suficiente, com tratamento mais conservador para métricas, liderança, senioridade e produção;
3. **Resume Router** — decide entre bloquear, revisar, reutilizar ou preparar uma composição de currículo.

A implementação é **sintética e independente**, escrita apenas com a biblioteca padrão do Python. Ela demonstra os princípios e invariantes públicos do produto; não é uma cópia da implementação privada nem contém dados pessoais, candidaturas ou credenciais.

## Executar

Python 3.11+:

```bash
python demo/standalone_demo.py
```

A saída é JSON e inclui uma vaga sintética, uma claim sustentada, uma claim sensível bloqueada e a decisão de roteamento.

## Executar os testes

Na raiz do repositório:

```bash
python -m unittest discover -s demo -p "test_*.py" -v
```

Os testes cobrem:

- uma vaga alinhada à direção configurada;
- uma vaga explicitamente fora do objetivo;
- uma afirmação sustentada por evidência;
- uma afirmação sensível sem evidência;
- roteamento para geração quando os gates passam;
- revisão obrigatória quando falta evidência.

## Limites intencionais

- não há matching semântico/LLM nesta demonstração;
- os thresholds são demonstrativos e não devem ser interpretados como os valores da instalação privada;
- a evidência é sintética;
- a demo não gera PDF, não coleta vagas e não envia candidatura;
- CAPTCHA, termos de uso e envio final continuam fora de qualquer automação pública demonstrada aqui.

Para a arquitetura completa e os limites da versão em uso, consulte [`../docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md), [`../docs/TESTING.md`](../docs/TESTING.md) e [`../docs/AI_SYSTEM_CARD.md`](../docs/AI_SYSTEM_CARD.md).
