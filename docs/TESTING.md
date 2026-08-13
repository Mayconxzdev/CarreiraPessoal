# Testes e validação

O projeto possui testes automatizados cobrindo regras de negócio, API, persistência, matching, evidências, fontes e fluxos críticos. A edição pública evita congelar no README um número histórico de testes: o resultado atual deve ser conferido na CI e no código da versão publicada.

## Gates principais

```bash
python -m compileall -q app tests scripts
python -m pytest -q
python scripts/public_safety_scan.py
```

A release Windows também depende dos gates de frontend/desktop e do empacotamento real antes de ser promovida. Os workflows públicos priorizam validações reproduzíveis e não tratam documentação antiga como fonte de verdade para o estado atual.
