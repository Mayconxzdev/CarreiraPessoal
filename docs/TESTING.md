# Testes e gates

## Evidência da versão 12.5.2

Última validação de fonte registrada no pacote entregue em 13/08/2026:

```text
283/283 testes Python PASS
6/6 validações adicionais PASS
compileall app+tests PASS
node --check popup.js PASS
node --check background.js PASS
```

As auditorias intermediárias da evolução 12.5 registraram contagens menores porque novos testes foram adicionados durante o hardening. Para a edição pública, **283 + 6** é a referência mais recente do source candidate.

## CI pública

A CI pública reconstrói o frontend, executa `compileall`, `pytest`, checks do Companion e o safety scan.

## Gate físico Windows

A validação do instalador é separada porque exige o ciclo real:

```text
Tauri/Rust check
→ frontend
→ PyInstaller sidecar
→ NSIS
→ clean install
→ API/WebView2/sidecar smoke
→ same-version reinstall
→ smoke novamente
→ silent uninstall
```

O projeto não rotula um instalador como release final enquanto esse gate não estiver verde.
