# Análise Comparativa — T2 Rosetta de Paradigmas

> **Status:** versão atualizada com diagnósticos do regime frio e configuração do computador. Antes da entrega, preencher os itens marcados **PENDENTE**, especialmente o teste de legibilidade e os créditos de autoria/revisão.

## 1. Objetivo e escopo

Este documento compara três implementações do mesmo problema de planejamento de matrícula: **imperativa**, **funcional** e **orientada a objetos (OO)**. Todas foram implementadas em **Python**, permitindo estudar as diferenças de organização do programa sem introduzir, nesta comparação, linguagens de programação distintas.

As quatro perguntas resolvidas são: (1) detecção de ciclos de pré-requisitos; (2) identificação de disciplinas liberadas; (3) identificação de disciplinas bloqueadas e pré-requisitos faltantes; e (4) identificação de **todas** as grades válidas com maior número de disciplinas, respeitando conflitos de horários e teto de carga horária.

As três versões passaram nos **cinco casos oficiais**, conforme o teste de equivalência executado pelo grupo: **15 verificações aprovadas**.

**Arquivos examinados:** `imperativa/imperativo.py`, `Funcional/funcional.py`, `oo/dominio.py` e os módulos da pasta `medicao/`. **Fonte dos números abaixo:** `medicao/resultados/amostras.csv`, `resumo.csv` e `resumo.json`, gerados no computador do grupo.

## 2. Legibilidade

### 2.1. Organização e extensão do código do problema

Para não distorcer a comparação com leitura de arquivos, impressão, conversão de JSON e declarações de tipo, foi feita uma **contagem estática preliminar** das linhas de código não vazias e não comentadas **no corpo das rotinas que resolvem as quatro perguntas**, sem contar cabeçalhos de funções, docstrings, `main`, adaptadores ou testes. Na versão OO, foram incluídos os métodos de negócio que colaboram na resolução; construtores e declarações de atributos não foram contados. As contagens não são uma medida absoluta de facilidade de leitura.

| Implementação | Linhas de corpo de código relevantes | Rotinas/métodos considerados | Profundidade máxima de blocos `if`/laço observada* |
|---|---:|---:|---:|
| Imperativa | 149 | 6 | 5 |
| Funcional | 113 | 7 | 1 |
| Orientada a objetos | 105 | 18 | 3 |

\* Profundidade sintática dos blocos de controle nas rotinas examinadas. A recursão, as lambdas, as expressões geradoras e a complexidade conceitual **não** são capturadas por essa métrica; por isso, profundidade menor não significa necessariamente leitura mais fácil.

A versão **imperativa** organiza a resolução em procedimentos e controles explícitos. Sua leitura tende a ser direta em cada laço, mas várias operações que Python oferece prontas são reimplementadas manualmente, aumentando a extensão dos trechos.

A versão **funcional** emprega funções puras no núcleo, `map`, `filter`, `reduce`, recursão e estruturas imutáveis (`tuple`, `frozenset`). Isso torna transformações de dados concisas, mas algumas cadeias de chamadas e funções aninhadas podem exigir mais esforço para acompanhar o fluxo.

A versão **OO** distribui as decisões entre entidades (`Aluno`, `Disciplina`, `Grade`, `MatrizCurricular`), restrições e um buscador. Essa separação favorece a localização de responsabilidades. Por outro lado, entender a execução completa exige navegar entre métodos e compreender a colaboração entre objetos. O código possui **11 classes** de domínio, incluindo a classe abstrata `Restricao`.

### 2.2. Teste prático com leitor externo — PENDENTE

O enunciado exige que **a mesma pessoa, de outro trio**, leia as três versões em ordem sorteada, registrando **tempo e erros de interpretação**. Esse experimento **não está presente** nos resultados enviados e não deve ser inventado.

Preencher após realizá-lo:

| Ordem sorteada | Implementação | Tempo de leitura | O que o leitor entendeu incorretamente |
|---|---|---|---|
| **PENDENTE** | **PENDENTE** | **PENDENTE** | **PENDENTE** |
| **PENDENTE** | **PENDENTE** | **PENDENTE** | **PENDENTE** |
| **PENDENTE** | **PENDENTE** | **PENDENTE** | **PENDENTE** |

Pedir ao leitor que explique, sem auxílio, onde cada versão detecta ciclos, verifica pré-requisitos, valida horários e decide quais grades são máximas. Os erros relatados são evidência tão importante quanto o tempo gasto.

## 3. Expressividade

A comparação considera a proporção entre **regra de negócio** (o que o problema exige) e **mecanismo** (os passos e estruturas utilizados para implementá-la). As expressões abaixo são recortes dos códigos reais; não representam o algoritmo completo.

### 3.1. Pergunta 1 — Detectar ciclo de pré-requisitos

| Imperativa | Funcional | Orientada a objetos |
|---|---|---|
| `estado[viz] == 1` no percurso de DFS; pilha e estados atualizados explicitamente | `v in caminho`; funções recursivas `dfs_no` e `explorar_vizinhos` propagam caminho e visitados | `MatrizCurricular.detectar_ciclo()` contém o DFS e mantém estados e posições da pilha |

As três versões utilizam busca em profundidade (DFS). A diferença principal é a forma de **manter e transmitir o estado da busca**: mutações explícitas de estruturas na imperativa e na OO, contra passagem de novos valores pela recursão na funcional. Na OO, a regra fica encapsulada no objeto responsável pela matriz.

### 3.2. Pergunta 2 — Disciplinas liberadas

| Imperativa | Funcional | Orientada a objetos |
|---|---|---|
| `if not contem(aprovadas, req[j]):` e laços para percorrer os requisitos | `filter(lambda p: p not in aprovadas_fset, prereqs)` e `map` para avaliar ofertas | `disciplina.prerequisitos_faltantes(aluno)` consulta `aluno.aprovou(codigo)` |

Na imperativa, a regra de pertinência ao histórico é construída por uma rotina `contem` com laço. Na funcional, a transformação é expressa por funções de ordem superior. Na OO, o aluno e a disciplina colaboram por métodos que nomeiam o conceito do domínio.

### 3.3. Pergunta 3 — Disciplinas bloqueadas

| Imperativa | Funcional | Orientada a objetos |
|---|---|---|
| Preenche `faltam` com `append`, depois adiciona `{"codigo": cod, "faltam": faltam}` | Filtra pares com requisitos faltantes e usa `map` para construir os registros | `PlanejadorDeMatricula.analisar()` usa o retorno de `Disciplina.prerequisitos_faltantes()` para classificar as ofertas |

As perguntas 2 e 3 compartilham a mesma regra de pré-requisitos, mas produzem saídas diferentes: lista de códigos liberados e lista de registros com requisitos faltantes. A versão funcional reaproveita uma sequência de pares `(código, faltantes)`; a OO centraliza a verificação em `Disciplina`.

### 3.4. Pergunta 4 — Grades máximas

| Imperativa | Funcional | Orientada a objetos |
|---|---|---|
| `for mask in range(1, total_mascaras):` gera subconjuntos por bits e testa as restrições | `gerar_subconjuntos(liberadas)` constrói tuplas recursivamente; `filter` seleciona grades válidas | `BuscadorDeGrades._explorar()` usa backtracking com poda; objetos `Restricao` decidem a validade |

A imperativa representa as escolhas por **máscaras de bits**. A funcional gera explicitamente os subconjuntos em estruturas imutáveis e filtra os válidos. A OO usa **busca com retrocesso (backtracking)** e pode podar ramos que não conseguem alcançar o máximo atual. A validação OO usa polimorfismo: o mesmo método `permite(grade)` é executado por `TetoDeCargaHoraria` e `ConflitoDeHorario`, conforme o tipo real do objeto.

**Complexidade:** gerar todos os subconjuntos possíveis de `k` disciplinas ofertadas pode exigir até `2^k` candidatos. A poda da OO pode reduzir o trabalho efetivo, mas não elimina o pior caso exponencial. O tamanho da **oferta**, e não apenas o da matriz, é o fator crítico da quarta pergunta.

### 3.5. Quanto da verbosidade imperativa é imposto pelas regras?

Um exemplo simples do código imperativo é a busca por pertinência:

```python
# Implementação imperativa utilizada no trabalho
def contem(lista, alvo):
    for i in range(len(lista)):
        if lista[i] == alvo:
            return True
    return False
```

Usando uma construção pronta de Python, a mesma operação poderia ser expressa assim:

```python
def contem(lista, alvo):
    return alvo in lista
```

Nesse exemplo, o corpo foi reduzido de **4 linhas de instruções** para **1 linha**, sem alterar a regra de negócio. Isso mostra que parte da verbosidade da versão imperativa decorre da **restrição às operações prontas de coleções** imposta no exercício, e não necessariamente de uma limitação intrínseca do paradigma. Essa observação não é uma medição completa da redução possível em toda a implementação.

## 4. Desempenho

### 4.1. Ambiente e metodologia

Os resultados foram produzidos pelo arnês `medicao/medir.py` no ambiente registrado automaticamente:

| Item | Valor registrado |
|---|---|
| Sistema operacional | Windows 11 (`Windows-11-10.0.26200-SP0`) |
| Linguagem e implementação | Python, CPython 3.15.2, 64 bits |
| Arquitetura | AMD64 |
| Identificação de CPU informada pelo sistema | `AMD64 Family 25 Model 97 Stepping 2, AuthenticAMD` |
| Modelo comercial do processador | AMD Ryzen 5 7600X |
| Memória RAM | 16 GB DDR5 instalados |
| Relógio de alta resolução | `time.perf_counter_ns()` |
| Data da geração, UTC | 24/11/2026, 01:56:03 |

A matriz original contém **15 disciplinas** e a ampliada, **200 disciplinas**. Ambas utilizam a mesma oferta de **8 disciplinas**, preservando o número de possíveis combinações para que o aumento da matriz não provoque por si só uma explosão combinatória da quarta pergunta.

Os dois regimes foram executados separadamente:

- **Frio (ponta a ponta):** 20 execuções por versão e cenário, cada uma em um novo processo Python, incluindo inicialização, importações, leitura dos JSONs, adaptação, resolução e produção da saída.
- **Quente (em regime):** 100 execuções iniciais descartadas e mais **1.000 execuções cronometradas** das quatro perguntas no mesmo processo, sem leitura dos JSONs dentro da região medida.

Os resultados são apresentados em **milissegundos (ms)** e resumidos por **mediana**, **mínimo** e **intervalo interquartil (IQR = P75 − P25)**, com interpolação linear dos percentis. Foram examinadas **6.120 amostras**: `2 cenários × 3 versões × (20 frias + 1.000 quentes)`; nenhuma combinação ou iteração estava ausente no CSV enviado.

### 4.2. Resultados — regime quente

| Cenário | Versão | Mediana (ms) | Mínimo (ms) | IQR (ms) |
|---|---|---:|---:|---:|
| Original (15) | Imperativa | 0,0661 | 0,0643 | 0,0043 |
| Original (15) | Funcional | 0,2857 | 0,2794 | 0,0075 |
| Original (15) | OO | **0,0270** | 0,0262 | 0,0012 |
| Ampliado (200) | Imperativa | 0,1502 | 0,1462 | 0,0045 |
| Ampliado (200) | Funcional | 3,0862 | 2,8468 | 0,1996 |
| Ampliado (200) | OO | **0,0781** | 0,0729 | 0,0065 |

A versão OO apresentou as menores medianas nos dois cenários. No cenário original, a versão imperativa teve mediana cerca de **2,45 vezes maior** que a OO, e a funcional, cerca de **10,58 vezes maior**. Na matriz ampliada, as razões foram de cerca de **1,92** e **39,52**, respectivamente.

Ao passar de 15 para 200 disciplinas, a mediana da versão imperativa cresceu aproximadamente **2,27 vezes**, a funcional **10,80 vezes** e a OO **2,89 vezes**.

Uma explicação **plausível, apoiada pela leitura do código**, é que a versão funcional consulta repetidamente disciplinas por meio de `buscar_disc()`, que usa `filter` sobre uma **tupla inteira**. Quando a matriz cresce, buscas repetidas desse tipo custam mais. As versões imperativa e OO usam **dicionários por código** em pontos importantes da resolução. Além disso, a versão funcional gera explicitamente todos os subconjuntos, enquanto a OO utiliza busca com poda. Isso ajuda a interpretar os números, mas não prova isoladamente qual mecanismo causou toda a diferença.

**Limitação importante:** no regime quente, a leitura e a normalização de dados são realizadas antes do cronômetro. A OO também constrói previamente objetos de domínio; já as outras versões trabalham com suas representações preparadas. A região medida representa a **resolução das quatro perguntas em cada implementação**, não o custo de carregar um caso inteiro do zero.

### 4.3. Resultados — regime frio

| Cenário | Versão | Mediana (ms) | Mínimo (ms) | IQR (ms) |
|---|---|---:|---:|---:|
| Original (15) | Imperativa | 588,11 | 61,86 | 982,00 |
| Original (15) | Funcional | 1.034,12 | 62,68 | 980,08 |
| Original (15) | OO | 71,44 | 65,29 | 977,27 |
| Ampliado (200) | Imperativa | 558,14 | 61,75 | 984,43 |
| Ampliado (200) | Funcional | 75,44 | 65,24 | 984,90 |
| Ampliado (200) | OO | 1.045,11 | 66,30 | 982,61 |

**Alerta metodológico:** os dados frios mostram duas faixas de tempo muito distintas em **todas** as implementações e nos **dois** cenários: a maioria das execuções ficou próxima de **60–80 ms ou 1.040–1.060 ms**, com algumas intermediárias. Por exemplo, na matriz original, **10/20 execuções imperativas**, **11/20 funcionais** e **9/20 OO** superaram 500 ms. Na matriz ampliada, os números foram **10/20**, **9/20** e **11/20**, respectivamente.

A diferença próxima de um segundo aparece em implementações e entradas distintas, indicando **forte interferência externa ou de inicialização**, ainda não identificada. Os valores de IQR próximos de **980 ms** confirmam a dispersão extrema. Por isso, a classificação por mediana no regime frio **não é robusta**, e esses números **não sustentam conclusões de superioridade** de uma implementação sobre outra. Os mínimos, todos entre aproximadamente 62 e 66 ms, sugerem que parte considerável da medição fria é custo fixo do ambiente de inicialização do processo.

**Investigação complementar:** a instabilidade foi investigada com testes de controle, descritos na seção 4.4. Os tempos lentos devem permanecer nas estatísticas originais: não é adequado descartar observações apenas por serem altas. A interferência impede conclusões sólidas de superioridade no regime frio.

### 4.4. Diagnósticos de controle do regime frio

Para investigar a variação, foram executados três diagnósticos adicionais: uma comparação de processos Python com e sem captura de saída, a separação entre **criação** e **espera pela conclusão** e uma comparação de **Python vazio** com o **CMD nativo do Windows**. Esses testes de controle não executam as quatro perguntas do problema, permitindo observar o comportamento do ambiente independentemente dos algoritmos de matrícula.

No teste final (`diagnostico_sistema.csv`), foram realizados **20 processos Python vazios** (`python -c "pass"`) e **20 processos CMD vazios** (`cmd /d /c "exit /b 0"`), em **ordem embaralhada**. As medições utilizaram `time.perf_counter_ns()` e `subprocess.Popen()`, separando tempo de criação do subprocesso e tempo de espera por sua conclusão.

| Indicador | Python vazio | CMD vazio |
|---|---:|---:|
| Quantidade | 20 | 20 |
| Mínimo do tempo total | 15,165 ms | 6,291 ms |
| Mediana do tempo total | 47,608 ms | 8,074 ms |
| Máximo do tempo total | 2.027,114 ms | 2.026,108 ms |
| Tempo total ≥ 500 ms | 5/20 | 3/20 |

Das **40 execuções**, **8 (20%)** duraram pelo menos 500 ms. Houve **7 ocorrências** de criação demorada (≥ 500 ms) e **4 ocorrências** de espera demorada (≥ 500 ms), das quais **3** coincidiram em uma mesma execução. Como o comportamento também apareceu ao executar o CMD, ele **não é específico do interpretador Python nem dos algoritmos de matrícula**. O experimento indica variabilidade na criação e/ou espera por subprocessos, mas **não identifica o componente responsável**. Não há base para atribuir a causa, isoladamente, ao antivírus, à memória RAM, ao processador ou ao sistema operacional.

**Implicação metodológica:** manter a coleta fria original e relatar essa variabilidade é mais transparente do que descartar resultados altos ou classificar implementações com base em medianas instáveis. Um teste em outro ambiente seria útil como confirmação adicional, mas os dados atuais continuam válidos como observações do ambiente medido, com essa limitação. Os tempos do **regime quente**, de menor dispersão, são a referência mais estável desta comparação específica.

### 4.5. Interpretação geral

Como as três implementações utilizam **a mesma linguagem e implementação (CPython)**, esta comparação evita parte do confundimento entre linguagens e runtimes distintos. Ainda assim, **não mede a velocidade intrínseca de paradigmas**. Mede versões concretas, com decisões distintas: percursos explícitos e máscaras de bits (imperativa); estruturas imutáveis, buscas lineares frequentes e construção recursiva de subconjuntos (funcional); objetos, mapas, backtracking com poda e polimorfismo (OO).

A ampliação da **matriz** aumenta principalmente o trabalho com disciplinas e relações de pré-requisitos. A ampliação da **oferta** seria metodologicamente distinta, pois a busca pelas grades possui pior caso exponencial no número de disciplinas candidatas; por isso, a oferta permaneceu com 8 disciplinas, respeitando o limite máximo de 16 indicado no enunciado.

## 5. Conclusão

Para este problema, a versão **orientada a objetos** mostrou-se uma escolha adequada: os conceitos de aluno, disciplina, matriz, grade e restrições correspondem bem a objetos com responsabilidades próprias. O método `permite()` nas subclasses de `Restricao` demonstra polimorfismo real e facilita acrescentar novas regras sem reescrever o buscador. A versão OO também apresentou as menores medianas no **regime quente**, embora isso seja um resultado das implementações examinadas e não uma prova de superioridade geral do paradigma.

A versão **funcional** favorece a descrição declarativa de transformações e o controle explícito de efeitos, mas seu uso de buscas repetidas sobre tuplas elevou o custo observado com a matriz ampliada. A versão **imperativa** tornou os percursos explícitos e previsíveis, porém parte de sua verbosidade resultou das construções proibidas pelo exercício. A resposta sobre qual paradigma é mais adequado poderia mudar se a prioridade fosse, por exemplo, transformação de dados imutáveis, facilidade de extensão das regras ou implementação de estruturas de acesso mais eficientes. O resultado final deve considerar **correção, clareza, facilidade de manutenção e desempenho**, sem confundir um algoritmo específico com o paradigma inteiro.

