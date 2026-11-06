# CarreiraPessoal

**Protótipo pessoal para organizar minha busca de vagas e as versões do currículo. Ainda está incompleto.**

[Voltar ao meu GitHub](https://github.com/Mayconxzdev) · [Demo em Python](demo/README.md) · [Arquitetura](docs/ARCHITECTURE.md)

## Por que comecei

Eu estava procurando vagas em vários lugares, encontrando anúncios repetidos e gastando tempo para comparar requisitos com o que realmente quero seguir na carreira. Também precisava manter o currículo e as evidências dos projetos organizados.

Quis montar uma ferramenta local para reunir essas etapas, mas **não concluí a experiência inteira nem adotei o aplicativo como meu processo de candidatura**. Prefiro deixar isso claro a apresentar uma lista de funcionalidades como se tudo estivesse pronto.

## O que desenvolvi

O projeto tem partes para descobrir e normalizar vagas, comparar requisitos com a direção profissional, controlar afirmações do currículo com fatos registrados e escolher uma versão de currículo conforme a vaga.

Três componentes ficaram especialmente interessantes para estudar:

- **Career Goal:** separa uma vaga tecnicamente parecida de uma vaga que faz sentido para o objetivo definido.
- **EvidenceGuard:** procura evitar que a aplicação coloque no currículo informações sem comprovação.
- **Resume Router:** ajuda a relacionar a descrição da vaga com diferentes versões de currículo.

A ideia era fazer o núcleo funcionar de modo determinístico, com IA como recurso opcional quando agregasse valor. No código privado experimentei FastAPI, SQLite, React, TypeScript e Tauri.

## O que dá para testar aqui

A pasta [`demo/`](demo/README.md) é uma demonstração isolada em Python, com dados fictícios. Ela não precisa de credenciais nem dos bancos da aplicação privada.

```bash
python demo/standalone_demo.py
python -m unittest discover -s demo -p "test_*.py" -v
```

O material público contém também [exemplos de componentes](examples/), [decisões de arquitetura](docs/ARCHITECTURE.md) e [notas sobre IA](docs/AI_SYSTEM_CARD.md). Os exemplos de código não compõem o aplicativo inteiro e algumas dependências não fazem parte do recorte público.

## Onde parei

A versão privada chegou a ter um relatório de **283 testes Python aprovados**, mas esse número não significa que a jornada de candidatura tenha sido homologada. A edição pública contém poucos testes e foi encontrada uma inconsistência na comparação de senioridade entre vagas. Preciso corrigir essa regra, testar as integrações completas e simplificar a interface antes de chamar o projeto de concluído.

Por enquanto, mantenho o repositório como parte da minha trajetória de estudo sobre automação, qualidade de informação e decisões assistidas por IA. Ele **não é um produto finalizado nem um case principal do meu portfólio**.

---

**Maycon Ferreira** · [GitHub](https://github.com/Mayconxzdev) · [LinkedIn](https://www.linkedin.com/in/maycon-ferreira-7bb870231/)
