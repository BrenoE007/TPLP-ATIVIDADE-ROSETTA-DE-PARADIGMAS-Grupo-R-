# Declaração de Uso de Inteligência Artificial

**Trabalho:** T2 — Rosetta de Paradigmas  
**Disciplina:** Teoria e Paradigmas de Linguagens de Programação

## 1. Objetivo

Este documento registra de forma transparente como ferramentas de inteligência artificial (IA) foram utilizadas no desenvolvimento, na avaliação e na documentação do projeto. O grau de participação da IA variou de acordo com o componente: em algumas partes, atuou como apoio à programação e à escrita; em outras, produziu versões de código que passaram por revisão humana.

## 2. Ferramentas utilizadas

- **Gemini 4:** auxílio no desenvolvimento das versões imperativa e funcional e na elaboração da auditoria.
- **GPT-6 (ChatGPT):** geração e apoio à revisão da versão orientada a objetos, implementação do arnês de medição, elaboração de scripts de diagnóstico e apoio à documentação e à análise comparativa.

## 3. Uso de IA por componente

| Componente | Ferramenta | Participação da IA | Participação humana |
|---|---|---|---|
| Versão imperativa (`imperativa/`) | Gemini 4 | Auxílio durante o desenvolvimento do código. | Desenvolvimento conduzido pelo grupo com apoio da ferramenta. |
| Versão funcional (`Funcional/`) | Gemini 4 | Auxílio durante o desenvolvimento do código. | Desenvolvimento conduzido pelo grupo com apoio da ferramenta. |
| Versão orientada a objetos (`oo/`) | GPT-6 (ChatGPT) | Geração do código da implementação. | Revisão e modificações no código gerado. |
| Arnês de medição (`medicao/`) | GPT-6 (ChatGPT) | Geração do código dos scripts de medição. | Revisão humana do código. |
| Scripts complementares de diagnóstico | GPT-6 (ChatGPT) | Geração dos scripts utilizados para investigar a variação dos tempos do regime frio. | Execução dos diagnósticos e análise dos resultados obtidos pelo grupo. |
| Auditoria (`AUDITORIA.md`) | Gemini 4 | Auxílio à elaboração e à análise do material. | Auditoria elaborada por humano com apoio da ferramenta. |
| Três arquivos `README.md` | GPT-6 (ChatGPT) | Redação inicial da documentação. | Revisão humana dos textos. |
| Análise comparativa (`ANALISE.md`) | GPT-6 (ChatGPT) | Elaboração inicial do documento e apoio à interpretação dos resultados. | Modificações e complementações humanas no documento. |

## 4. Código gerado para auditoria

O projeto também preserva o código obtido por solicitação a uma ferramenta de IA e o prompt utilizado para produzi-lo, destinados à atividade de auditoria. Essa versão é distinta da implementação imperativa desenvolvida pelo grupo com auxílio de IA.

O relatório `AUDITORIA.md` registra os problemas identificados na versão gerada, suas classificações e as formas de verificação.

## 5. Revisão, testes e validação

A participação das ferramentas de IA não substituiu as atividades de revisão e avaliação do projeto. As versões foram submetidas à bateria de casos de teste prevista na atividade, e o arnês foi utilizado para coletar dados de desempenho.

Os scripts de diagnóstico complementares foram utilizados para investigar atrasos observados na execução de processos durante o regime frio. Os resultados dessa investigação e suas limitações são discutidos no `ANALISE.md`.

## 6. Considerações finais

O uso de IA teve funções diferentes ao longo do trabalho, abrangendo assistência à implementação, geração de código, produção de documentação e apoio à análise. Este registro distingue essas formas de participação e explicita as etapas de revisão ou modificação humana informadas pelo grupo, de modo a permitir a avaliação transparente do processo de desenvolvimento.
