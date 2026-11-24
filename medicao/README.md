# Arnês de medição — T2 Rosetta de Paradigmas

Executar os comandos **a partir da raiz do repositório**. Exige Python 3.10+ e **não requer pacotes externos**.

## O que foi observado no repositório

- `imperativa/imperativo.py` possui `resolver_matricula()`, mas não tem CLI. Espera matrizes como listas com a chave `prereqs` e histórico com a chave `teto`.
- `Funcional/funcional.py` possui `resolver_funcional()` e `main()`, mas seu `main()` atual não lê diretamente o esquema dos arquivos oficiais: o código funcional espera listas de disciplinas/oferta, pré-requisitos na chave `prereqs` e o teto na chave `teto`.
- `oo/main.py` funciona com os JSONs oficiais e a OO possui `PlanejadorDeMatricula.analisar()`.

O módulo `adaptadores.py` lê os arquivos JSON **originais sem alterá-los**, converte as entradas para o contrato de cada implementação e chama **as funções originais do grupo**. Não copia nem altera a lógica dos algoritmos. Assim, os testes e as medições não dependem de editar as três versões.

## 1. Testar equivalência (um comando)

```bash
python -m medicao.testar
```

Executa as três versões sobre os cinco casos e compara os resultados JSON com `saidas_esperadas.json` (15 verificações). Em caso de divergência, retorna erro.

## 2. Executar cada versão com os dados originais

```bash
python -m medicao.executar --versao imperativa
python -m medicao.executar --versao funcional
python -m medicao.executar --versao oo
```

Exemplo de outro caso:

```bash
python -m medicao.executar --versao funcional --matriz dados/caso2_ciclo.json
python -m medicao.executar --versao imperativa --historico dados/caso5_teto_reduzido.json
```

Esses são **comandos pelo adaptador** e não constituem um `main()` novo nos arquivos das implementações.

## 3. Gerar matriz ampliada

```bash
python -m medicao.gerar_matriz
```

Cria `medicao/dados/matriz_200.json` com exatamente **200 disciplinas**, mantendo as originais e adicionando disciplinas artificiais com códigos novos e pré-requisitos sem ciclos. Os JSONs de `dados/` ficam intocados. Usa-se a **mesma oferta oficial** (com menos de 16 disciplinas), de modo a isolar o aumento do tamanho da matriz da explosão combinatória da busca de grades.

## 4. Executar as medições completas

```bash
python -m medicao.medir
```

O script valida automaticamente todos os casos, gera a matriz ampliada, mede dois cenários (matriz original e matriz de 200 disciplinas) e produz arquivos em `medicao/resultados/`:

- `amostras.csv`: tempos individuais em nanossegundos, com cenário, regime, versão e iteração;
- `resumo.csv`: número de amostras, **mediana, mínimo e IQR** em milissegundos;
- `resumo.json`: os mesmos resumos e o ambiente de execução (SO, Python, arquitetura, processador quando informado pelo sistema).

**Regime frio:** pelo menos 20 execuções por versão/cenário; cada medição inicia um novo processo Python, carrega o código, lê e normaliza JSON, executa as quatro perguntas e produz a saída. O tempo é observado pelo processo controlador, incluindo a inicialização e finalização do processo, a captura do JSON e a adaptação necessária à compatibilidade.

**Regime quente:** um processo Python para cada versão/cenário; lê os dados, importa os módulos e cria os dados de entrada **uma única vez**. Executa 100 aquecimentos descartados, depois cronometra separadamente **1.000 execuções completas das quatro perguntas** via `time.perf_counter_ns()`. O JSON é impresso somente após as medições. As estatísticas são computadas no processo controlador.

Para diagnóstico rápido, com números **não válidos para entregar como medição final**, use:

```bash
python -m medicao.medir --repeticoes-frias 2 --iteracoes-quentes 20 --aquecimento 5
```

Para rodar apenas um cenário:

```bash
python -m medicao.medir --cenarios original
python -m medicao.medir --cenarios ampliado
```

## 5. Interpretação e limitações metodológicas

- Todas as implementações usam **Python** neste repositório. Isso reduz a confusão entre diferentes linguagens, embora ainda compare três algoritmos e modelos de dados distintos.
- **Não atribua diretamente diferenças de desempenho ao paradigma.** Uma implementação usa bitmasks, outra gera tuplas de subconjuntos e a OO faz backtracking com poda. Algoritmo, representação de coleções, recursão, alocações e construção de respostas influenciam os tempos.
- Os tempos frios contêm custo do adaptador e do processo de teste, além do código da versão correspondente; o impacto da estrutura do adaptador deve ser declarado.
- O regime quente **exclui importação, leitura e normalização** dos arquivos, mas inclui a criação do resultado de cada chamada e sua conversão para dicionário quando necessária.
- Os 100 aquecimentos não são registrados; o CPython normalmente não tem JIT. Aqui o descarte reduz efeitos iniciais (alocação, caches etc.), sem alegar aquecimento de um JIT inexistente.
- Métricas são sensíveis a carga da CPU, frequência, serviços em segundo plano, sistema e hardware. Registre a configuração da **máquina em que serão obtidos os números entregues**, evitando copiar resultados de máquinas diferentes como comparáveis.
- O método para IQR é `P75 - P25`, com percentis interpolados linearmente; `min` e mediana também são reportados. Unidades nos CSVs estão indicadas explicitamente.
- Mesmo com matriz de 200, a oferta oficial permanece pequena, evitando medir principalmente o crescimento exponencial da pergunta 4.

## Integração ao trabalho

Copie a pasta `medicao/` para a **raiz** do repositório, mantendo `imperativa/`, `Funcional/`, `oo/`, `dados/` e `saidas_esperadas.json` no mesmo nível. Não é preciso editar os códigos das três versões.

Após medir, utilize os números de `medicao/resultados/resumo.csv` na seção de desempenho de `ANALISE.md`. Os arquivos de resultados devem ser gerados novamente no computador do grupo para a apresentação e entrega.
