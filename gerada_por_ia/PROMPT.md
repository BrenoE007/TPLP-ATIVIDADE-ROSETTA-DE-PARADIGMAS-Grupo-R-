# Prompt utilizado para gerar a versão imperativa por IA

> Registro do prompt fornecido à inteligência artificial para produzir a implementação imperativa do trabalho **“O que eu posso cursar?”**.

## Texto do prompt

Escreva um programa completo em Python, seguindo estritamente o paradigma imperativo, para resolver o problema "O que eu posso cursar?" de matrícula universitária.

### 1. Entradas
O programa deve ler os dados a partir de arquivos JSON (matriz curricular, oferta do semestre e histórico do aluno com o teto de carga horária), recebendo os caminhos via argumentos de linha de comando (sys.argv), sem fixar valores ou caminhos no código.

### 2. Regras do Problema (nesta ordem exata)
1. *Validação da matriz (ciclo):* Verificar se existe ciclo de pré-requisitos na matriz curricular (ex.: A exige B, que exige A). Se houver ciclo, retornar o caminho que o fecha (ex.: ["CC0106", "CC0109", "CC0106"]) e definir as outras três chaves da saída como null, encerrando o processamento sem responder às demais perguntas.
2. *Disciplinas liberadas:* Listar as disciplinas da oferta que o aluno ainda não cursou e cujos pré-requisitos *diretos* (não transitivos) já constam como aprovados no histórico.
3. *Disciplinas bloqueadas:* Para cada disciplina da oferta não cursada que não está liberada, listar seu código e *todos* os pré-requisitos diretos não cumpridos, em ordem crescente de código.
4. *Maior grade possível:* Encontrar o subconjunto de disciplinas liberadas com o *maior número de disciplinas* (a carga horária é apenas restrição, não objetivo) que não tenha conflito de horário (nenhum par dia-turno compartilhado) e cuja soma de carga horária seja menor ou igual ao teto. Se houver empate no número máximo de disciplinas, listar todas as soluções empatadas. Se não houver nenhuma grade possível, retornar [[]].

### 3. Contrato de Saída
Imprimir na saída padrão (stdout) exclusivamente um único objeto JSON com as chaves exatas:
- "ciclo": null ou lista de strings com o caminho do ciclo.
- "liberadas": lista de códigos em ordem crescente.
- "bloqueadas": lista de objetos {"codigo": "...", "faltam": [...]} ordenada por "codigo", com "faltam" em ordem crescente.
- "grades_maximas": lista de listas de códigos (cada grade ordenada e a lista de grades em ordem lexicográfica).

### 4. Restrições Estritas do Paradigma Imperativo
- O algoritmo deve avançar mutando estado por meio de comandos e laços manuais (for ou while).
- É *proibido* usar: map, filter, reduce, compreensões de lista/dicionário/conjunto, expressões geradoras, sum, any, all, min, max, sorted, operações de conjunto (|, &, -), collections.Counter e qualquer função do módulo itertools.
- Todo percurso, busca, filtragem e ordenação de coleções deve ser escrito manualmente (implemente seu próprio algoritmo de ordenação, como Insertion Sort ou Bubble Sort).
- Para a pergunta 4, utilize busca em subconjuntos via máscara de bits (2^n) ou recursão com retrocesso (backtracking).
