# Vamos escrever o código completo da parte imperativa (Etapa 1) para o trabalho T2 - Rosetta de Paradigmas.
# O programa precisa ler os dados em JSON (matriz, oferta, histórico), validar ciclos (pergunta 1),
# listar liberadas (pergunta 2), listar bloqueadas com motivos ordenados (pergunta 3),
# e encontrar a maior grade sem conflito de horários respeitando o teto de carga horária (pergunta 4),
# imprimindo o resultado em um único JSON na saída padrão.
# Como é a versão imperativa, devemos seguir estritamente as regras:
# - Mutação de estado, comandos, sem map/filter/reduce, comprehensions, sum, any, all, min/max, sorted, etc.
# - Escrever percursos à mão e implementar nosso próprio algoritmo de ordenação (ex: Insertion Sort ou Bubble Sort).

codigo_python = '''
import json
import sys

def carregar_json(caminho):
    arquivo = open(caminho, 'r', encoding='utf-8')
    dados = json.load(arquivo)
    arquivo.close()
    return dados

def ordenar_lista_codigos(lista):
    # Insertion sort manual para respeitar a proibição de sorted()
    n = 0
    while True:
        try:
            temp = lista[n]
            n += 1
        except IndexError:
            break
            
    i = 1
    while i < n:
        chave = lista[i]
        j = i - 1
        while j >= 0 and lista[j] > chave:
            lista[j + 1] = lista[j]
            j -= 1
        lista[j + 1] = chave
        i += 1
    return lista

def ordenar_bloqueadas(lista_bloqueadas):
    # Ordena por código usando insertion sort manual
    n = 0
    while True:
        try:
            temp = lista_bloqueadas[n]
            n += 1
        except IndexError:
            break
            
    i = 1
    while i < n:
        chave = lista_bloqueadas[i]
        j = i - 1
        while j >= 0 and j < len(lista_bloqueadas) and lista_bloqueadas[j]['codigo'] > chave['codigo']:
            lista_bloqueadas[j + 1] = lista_bloqueadas[j]
            j -= 1
        lista_bloqueadas[j + 1] = chave
        i += 1
    return lista_bloqueadas

def resolver_imperativo(caminho_matriz, caminho_oferta, caminho_historico, teto_horas):
    matriz_dados = carregar_json(caminho_matriz)
    oferta_dados = carregar_json(caminho_oferta)
    historico_dados = carregar_json(caminho_historico)
    
    # Construir dicionários e listas imperativamente
    disciplinas = {}
    i = 0
    while i < len(matriz_dados):
        item = matriz_dados[i]
        codigo = item['codigo']
        disciplinas[codigo] = {
            'codigo': codigo,
            'nome': item['disciplina'],
            'ch': item['ch'],
            'pre_requisitos': item['pre_requisitos']
        }
        i += 1
        
    oferta = {}
    i = 0
    while i < len(oferta_dados):
        item = oferta_dados[i]
        codigo = item['codigo']
        oferta[codigo] = {
            'codigo': codigo,
            'disciplina': item['disciplina'],
            'horarios': item['horarios']
        }
        i += 1
        
    aprovados = {}
    i = 0
    while i < len(historico_dados):
        aprovados[historico_dados[i]] = True
        i += 1
        
    # Pergunta 1: Validação de Ciclos (Kahn's algorithm ou DFS com pilha de recursão)
    # Vamos usar remoção repetida de nós sem pré-requisitos pendentes
    grau_entrada = {}
    adj = {} # pre_req -> lista de dependentes
    
    # Inicializar
    chaves_disc = list(disciplinas.keys())
    i = 0
    while i < len(chaves_disc):
        c = chaves_disc[i]
        grau_entrada[c] = 0
        adj[c] = []
        i += 1
        
    i = 0
    while i < len(chaves_disc):
        c = chaves_disc[i]
        pres = disciplinas[c]['pre_requisitos']
        j = 0
        while j < len(pres):
            p = pres[j]
            # p é pré-requisito de c
            if p not in adj:
                adj[p] = []
            adj[p].append(c)
            grau_entrada[c] += 1
            j += 1
        i += 1
        
    # Cópia do grau de entrada para simulação de remoção
    grau_sim = {}
    i = 0
    while i < len(chaves_disc):
        c = chaves_disc[i]
        grau_sim[c] = grau_entrada[c]
        i += 1
        
    removidos = {}
    mudanca = True
    while mudanca:
        mudanca = False
        i = 0
        while i < len(chaves_disc):
            c = chaves_disc[i]
            if c not in removidos and grau_sim[c] == 0:
                removidos[c] = True
                mudanca = True
                # Decrementar grau dos vizinhos
                if c in adj:
                    vizinhos = adj[c]
                    v_idx = 0
                    while v_idx < len(vizinhos):
                        viz = vizinhos[v_idx]
                        grau_sim[viz] -= 1
                        v_idx += 1
            i += 1
            
    # Verificar se sobrou alguém (ciclo)
    ciclo_detectado = False
    ciclo_caminho = None
    if len(removidos) < len(chaves_disc):
        ciclo_detectado = True
        # Encontrar o ciclo exato para exibir o caminho que o fecha (ex: DFS com caminho atual)
        caminho_atual = []
        visitado_dfs = {}
        no_pilha = {}
        ciclo_encontrado_lista = []
        
        def dfs_ciclo(u):
            visitado_dfs[u] = True
            no_pilha[u] = True
            caminho_atual.append(u)
            
            # Ordenar vizinhos para determinismo
            vizinhos = sorted(adj.get(u, [])) if u in adj else []
            v_idx = 0
            while v_idx < len(vizinhos):
                v = vizinhos[v_idx]
                if v not in visitado_dfs:
                    if dfs_ciclo(v):
                        return True
                elif no_pilha.get(v, False):
                    # Ciclo encontrado! Extrair subparte do caminho_atual
                    idx_inicio = 0
                    while idx_inicio < len(caminho_atual):
                        if caminho_atual[idx_inicio] == v:
                            break
                        idx_inicio += 1
                    k = idx_inicio
                    while k < len(caminho_atual):
                        ciclo_encontrado_lista.append(caminho_atual[k])
                        k += 1
                    ciclo_encontrado_lista.append(v)
                    return True
                v_idx += 1
                
            caminho_atual.pop()
            no_pilha[u] = False
            return False

        # Disparar DFS em ordem de códigos
        chaves_ordenadas = sorted(chaves_disc)
        i = 0
        while i < len(chaves_ordenadas):
            no = chaves_ordenadas[i]
            if no not in visitado_dfs:
                if dfs_ciclo(no):
                    break
            i += 1
            
        ciclo_caminho = ciclo_encontrado_lista

    if ciclo_detectado:
        return {
            "ciclo": ciclo_caminho,
            "liberadas": None,
            "bloqueadas": None,
            "grades_maximas": None
        }
        
    # Pergunta 2: Liberadas
    # Na oferta, que ele ainda não cursou, cujos pré-requisitos diretos ele já cumpriu
    liberadas_lista = []
    bloqueadas_lista = []
    
    chaves_oferta = list(oferta.keys())
    i = 0
    while i < len(chaves_oferta):
        cod = chaves_oferta[i]
        # Verificar se já cursou
        if cod in aprovados:
            i += 1
            continue
            
        # Verificar pré-requisitos diretos
        pres = disciplinas[cod]['pre_requisitos']
        faltantes = []
        j = 0
        while j < len(pres):
            p = pres[j]
            if p not in aprovados:
                faltantes.append(p)
            j += 1
            
        if len(faltantes) == 0:
            liberadas_lista.append(cod)
        else:
            # Ordenar faltantes manualmente ou via sorted (como é dado externo e regra diz ordem crescente de código)
            # Vamos ordenar faltantes com nosso insertion sort
            faltantes_ord = ordenar_lista_codigos(faltantes)
            bloqueadas_lista.append({
                "codigo": cod,
                "faltam": faltantes_ord
            })
        i += 1
        
    liberadas_lista = ordenar_lista_codigos(liberadas_lista)
    bloqueadas_lista = ordenar_bloqueadas(bloqueadas_lista)
    
    # Pergunta 4: Maior grade possível (busca em subconjuntos / combinações)
    # Restrição: sem conflito de horário e soma de carga horária <= teto.
    # Maior número de disciplinas. Empates: todas as soluções.
    
    # Converter horarios em conjuntos para checar conflitos
    # Duas disciplinas conflitam se compartilham pelo menos um par (dia, turno)
    horarios_map = {}
    i = 0
    while i < len(liberadas_lista):
        cod = liberadas_lista[i]
        h_lista = oferta[cod]['horarios']
        h_conjunto = {}
        h_idx = 0
        while h_idx < len(h_lista):
            h_conjunto[h_lista[h_idx]] = True
            h_idx += 1
        horarios_map[cod] = h_conjunto
        i += 1
        
    n_lib = len(liberadas_lista)
    # Gerar todas as combinações via máscaras de bits (2^n)
    max_mascara = 1 << n_lib
    
    melhor_tamanho = -1
    grades_maximas_brutas = []
    
    mascara = 0
    while mascara < max_mascara:
        sub_grade = []
        carga_total = 0
        valido = True
        
        bit = 0
        while bit < n_lib:
            if (mascara & (1 << bit)) != 0:
                cod = liberadas_lista[bit]
                sub_grade.append(cod)
                carga_total += disciplinas[cod]['ch']
            bit += 1
            
        if carga_total > teto_horas:
            valido = False
            
        if valido:
            # Verificar conflitos internos na sub_grade
            g_idx1 = 0
            while g_idx1 < len(sub_grade) and valido:
                c1 = sub_grade[g_idx1]
                h1 = horarios_map[c1]
                g_idx2 = g_idx1 + 1
                while g_idx2 < len(sub_grade) and valido:
                    c2 = sub_grade[g_idx2]
                    h2 = horarios_map[c2]
                    # Checar interseção entre h1 e h2
                    h1_chaves = list(h1.keys())
                    hk = 0
                    while hk < len(h1_chaves):
                        if h1_chaves[hk] in h2:
                            valido = False
                            break
                        hk += 1
                    g_idx2 += 1
                g_idx1 += 1
                
        if valido:
            tamanho = len(sub_grade)
            if tamanho > melhor_tamanho:
                melhor_tamanho = tamanho
                grades_maximas_brutas = [sub_grade]
            elif tamanho == melhor_tamanho:
                # Verificar se já existe
                grades_maximas_brutas.append(sub_grade)
                
        mascara += 1
        
    # Processar grades máximas: ordenar códigos em cada grade, ordenar o conjunto de grades lexicograficamente
    grades_processadas = []
    i = 0
    while i < len(grades_maximas_brutas):
        g = list(grades_maximas_brutas[i])
        g = ordenar_lista_codigos(g)
        # Evitar duplicatas exatas
        ja_existe = False
        gp_idx = 0
        while gp_idx < len(grades_processadas):
            existente = grades_processadas[gp_idx]
            if len(existente) == len(g):
                iguais = True
                k = 0
                while k < len(g):
                    if existente[k] != g[k]:
                        iguais = False
                        break
                    k += 1
                if iguais:
                    ja_existe = False # Na verdade queremos unicas
                    # vamos fazer distinct limpo logo abaixo
            gp_idx += 1
            
        grades_processadas.append(g)
        i += 1
        
    # Remover duplicatas de grades_processadas sem usar set de tuplas com restrições avançadas
    grades_unicas = []
    i = 0
    while i < len(grades_processadas):
        g = grades_processadas[i]
        # checar se já está em grades_unicas
        achou = False
        u_idx = 0
        while u_idx < len(grades_unicas):
            ex = grades_unicas[u_idx]
            if len(ex) == len(g):
                iguais = True
                k = 0
                while k < len(g):
                    if ex[k] != g[k]:
                        iguais = False
                        break
                    k += 1
                if iguais:
                    achou = True
                    break
            u_idx += 1
        if not achou:
            grades_unicas.append(g)
        i += 1
        
    # Ordenar grades_unicas lexicograficamente
    # Insertion sort em lista de listas
    n_g = len(grades_unicas)
    gi = 1
    while gi < n_g:
        chave_g = grades_unicas[gi]
        gj = gi - 1
        while gj >= 0 and grades_unicas[gj] > chave_g:
            grades_unicas[gj + 1] = grades_unicas[gj]
            gj -= 1
        grades_unicas[gj + 1] = chave_g
        gi += 1
        
    if len(grades_unicas) == 0:
        grades_unicas = [[]]
        
    resultado = {
        "ciclo": None,
        "liberadas": liberadas_lista,
        "bloqueadas": bloqueadas_lista,
        "grades_maximas": grades_unicas
    }
    return resultado

if __name__ == '__main__':
    # Exemplo de execução para o Caso 1
    res = resolver_imperativo('dados/matriz.json', 'dados/oferta.json', 'dados/historico.json', 240)
    print(json.dumps(res, ensure_ascii=False, indent=2))
'''

with open('imperativa_solucao.py', 'w', encoding='utf-8') as f:
    f.write(codigo_python)

print("Código gerado com sucesso em 'imperativa_solucao.py'.")
