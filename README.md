# T2 — Rosetta de Paradigmas

**Disciplina:** CC0114 — Teoria e Paradigmas de Linguagens de Programação  
**Curso:** Ciência da Computação — Universidade Federal do Amapá (UNIFAP)  
**Período:** 2026.2

## Sobre o projeto

Este repositório reúne as implementações do trabalho **Rosetta de Paradigmas**, cujo objetivo é resolver o mesmo problema utilizando três paradigmas de programação: **imperativo, funcional e orientado a objetos**.

O problema, chamado **“O que eu posso cursar?”**, simula o planejamento de matrícula universitária. A partir de uma matriz curricular, da oferta de disciplinas de um semestre e do histórico acadêmico de um aluno, cada implementação deve:

1. **Detectar ciclos de pré-requisitos** na matriz curricular. Se houver um ciclo, informar seu caminho e interromper as demais análises.
2. **Identificar disciplinas liberadas**, considerando as aprovações do aluno e os pré-requisitos diretos.
3. **Identificar disciplinas bloqueadas**, indicando os pré-requisitos diretos ainda não cumpridos.
4. **Encontrar todas as grades máximas**, priorizando o maior número de disciplinas, sem conflitos de horário e respeitando o teto de carga horária.

As três versões devem produzir resultados equivalentes e obedecer ao mesmo contrato de saída JSON. O trabalho também inclui uma **versão gerada por inteligência artificial**, preservada para auditoria, e um **arnês de medição** para comparar o desempenho das implementações.

## Início rápido

### Requisitos

- **Python 3.10 ou superior**;
- **Git** (para clonar o repositório);
- Nenhuma biblioteca externa é necessária: os programas utilizam a biblioteca padrão do Python.

### Clonar e testar

No terminal, execute:

```bash
git clone https://github.com/BrenoE007/TPLP-ATIVIDADE-ROSETTA-DE-PARADIGMAS-Grupo-R-.git
cd TPLP-ATIVIDADE-ROSETTA-DE-PARADIGMAS-Grupo-R-
python -m medicao.testar
```

> **Importante:** execute os comandos deste README a partir da **raiz do repositório** (a pasta que contém `dados/`, `imperativa/`, `Funcional/`, `oo/` e `medicao/`). No Windows, o comando `python` pode ser substituído por `py`, conforme a instalação.

O último comando executa as **três implementações nos cinco casos oficiais**, totalizando **15 verificações**, e compara as saídas com `saidas_esperadas.json`. Se houver divergência, o teste apresentará um erro.

## Estrutura do repositório

```text
.
├── dados/                       # Arquivos JSON de entrada fornecidos na atividade
├── saidas_esperadas.json         # Saídas canônicas dos cinco casos
├── imperativa/
│   └── imperativo.py            # Implementação imperativa
├── Funcional/
│   └── funcional.py             # Implementação funcional
├── oo/
│   ├── dominio.py               # Classes e regras de negócio da versão OO
│   ├── main.py                  # Entrada e saída da versão OO
│   ├── testes.py                # Testes independentes da versão OO
│   └── README.md                # Documentação da versão OO
├── gerada_por_ia/
│   ├── PROMPT.md                # Prompt utilizado na geração por IA
│   └── RESPOSTA-ORIGINAL/       # Código original produzido pela IA
├── medicao/
│   ├── adaptadores.py           # Adapta os dados para cada implementação
│   ├── executar.py              # Executa uma versão por linha de comando
│   ├── testar.py                # Testes de equivalência das três versões
│   ├── gerar_matriz.py          # Gerador da matriz ampliada
│   ├── medir.py                 # Medições de desempenho
│   ├── dados/                   # Matriz ampliada para os experimentos
│   ├── resultados/              # Amostras e estatísticas registradas
│   └── README.md                # Documentação detalhada do arnês
├── ANALISE.md                   # Comparação dos paradigmas e desempenho
├── AUDITORIA.md                 # Auditoria do código gerado por IA
├── USO-DE-IA.md                 # Declaração de utilização de IA no trabalho
├── .gitignore                   # Arquivos temporários excluídos do Git
└── README.md                    # Este documento
```

A capitalização dos diretórios deve ser respeitada, especialmente `Funcional/`.

## Executando as implementações

### Executar uma versão por vez

Para executar as três versões utilizando o **mesmo formato dos arquivos oficiais**, utilize os adaptadores do arnês:

**Imperativa**

```bash
python -m medicao.executar --versao imperativa
```

**Funcional**

```bash
python -m medicao.executar --versao funcional
```

**Orientada a objetos**

```bash
python -m medicao.executar --versao oo
```

Por padrão, esses comandos utilizam `dados/matriz.json`, `dados/oferta.json` e `dados/historico.json` (**caso 1**) e imprimem um único objeto JSON.

> As versões imperativa e funcional possuem funções de resolução próprias, mas seus arquivos originais não oferecem a mesma interface de linha de comando nem leem diretamente o formato oficial de entrada. O módulo `medicao/adaptadores.py` faz a conversão necessária **sem alterar os algoritmos** dessas versões. Por isso, os comandos acima são a forma recomendada para executá-las e compará-las.

### Selecionar outros casos de teste

Os parâmetros `--matriz`, `--oferta` e `--historico` permitem escolher os arquivos de entrada. Exemplos:

**Caso 2 — ciclo de pré-requisitos**

```bash
python -m medicao.executar --versao imperativa --matriz dados/caso2_ciclo.json
```

**Caso 3 — histórico vazio**

```bash
python -m medicao.executar --versao funcional --historico dados/caso3_historico_vazio.json
```

**Caso 4 — todas as disciplinas da oferta já concluídas**

```bash
python -m medicao.executar --versao oo --historico dados/caso4_historico_completo.json
```

**Caso 5 — teto de carga horária reduzido**

```bash
python -m medicao.executar --versao oo --historico dados/caso5_teto_reduzido.json
```

A versão OO também pode ser executada diretamente, sem o adaptador:

```bash
python oo/main.py
python oo/main.py --matriz dados/caso2_ciclo.json
python oo/testes.py
```

Para os parâmetros e detalhes dessa implementação, consulte [`oo/README.md`](oo/README.md).

## Formato de saída

Toda execução de uma solução deve produzir **um único objeto JSON**, com as seguintes chaves:

| Chave | Conteúdo |
|---|---|
| `ciclo` | `null` ou lista com o caminho de um ciclo de pré-requisitos |
| `liberadas` | Lista ordenada dos códigos das disciplinas liberadas |
| `bloqueadas` | Lista de objetos com `codigo` e `faltam` (pré-requisitos ausentes) |
| `grades_maximas` | Lista de todas as grades válidas com o maior número de disciplinas |

As disciplinas e grades são ordenadas conforme o contrato da atividade. Em caso de ciclo, as outras três chaves são `null`. Os resultados oficiais dos cinco casos estão em [`saidas_esperadas.json`](saidas_esperadas.json).

## Medições de desempenho

O arnês compara as três versões utilizando **dois cenários** (matriz original e matriz ampliada para 200 disciplinas) e **dois regimes**:

| Regime | Procedimento |
|---|---|
| **Frio (ponta a ponta)** | 20 execuções independentes por versão e cenário, incluindo a criação e o encerramento do processo |
| **Quente (em regime)** | 100 execuções de aquecimento descartadas e 1.000 execuções medidas dentro de um único processo, sem incluir o carregamento inicial dos dados |

São calculados **mediana**, **mínimo** e **intervalo interquartil (IQR)**. Para reproduzir o experimento:

```bash
python -m medicao.gerar_matriz
python -m medicao.medir
```

O segundo comando também verifica a correção das implementações e gera os resultados em `medicao/resultados/`:

- `amostras.csv`: tempos individuais de execução;
- `resumo.csv`: estatísticas consolidadas;
- `resumo.json`: estatísticas e informações do ambiente de execução.

**Observação metodológica:** o regime frio apresentou atrasos intermitentes associados à criação/espera de subprocessos no ambiente Windows utilizado pelo grupo, reproduzidos também em testes de controle com programas simples. Por isso, as comparações de desempenho do regime frio devem ser interpretadas com cautela. Os diagnósticos complementares e a discussão das limitações estão documentados no material de medição e em [`ANALISE.md`](ANALISE.md). As diferenças observadas não devem ser atribuídas automaticamente a um paradigma de programação.

Para instruções completas, parâmetros alternativos e limitações, consulte [`medicao/README.md`](medicao/README.md).

## Documentação do trabalho

- [`ANALISE.md`](ANALISE.md) — comparação das versões em legibilidade, expressividade e desempenho, incluindo a metodologia experimental;
- [`AUDITORIA.md`](AUDITORIA.md) — identificação e classificação de defeitos na versão gerada por IA;
- [`gerada_por_ia/PROMPT.md`](gerada_por_ia/PROMPT.md) — prompt utilizado para solicitar o código à IA;
- [`gerada_por_ia/RESPOSTA-ORIGINAL/`](gerada_por_ia/RESPOSTA-ORIGINAL/) — resposta original da IA, preservada para auditoria;
- [`USO-DE-IA.md`](USO-DE-IA.md) — registro do uso de ferramentas de IA no desenvolvimento;
- [`oo/README.md`](oo/README.md) e [`medicao/README.md`](medicao/README.md) — detalhes específicos de implementação e reprodução.

## Observações finais

- Os arquivos originais da pasta `dados/` devem ser mantidos **sem modificações**.
- A saída do código gerado por IA integra a **auditoria** e não substitui nenhuma das três implementações avaliadas.
- A comparação de desempenho avalia as **implementações concretas**: escolhas de algoritmos e estruturas de dados também influenciam os resultados.

---

*Trabalho acadêmico da disciplina Teoria e Paradigmas de Linguagens de Programação — UNIFAP, 2026.2.*
