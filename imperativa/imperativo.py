import json
import sys

def contem(lista, alvo):
    for i in range(len(lista)):
        if lista[i] == alvo:
            return True
    return False

def ordenar_strings(lista):
    n = len(lista)
    for i in range(1, n):
        chave = lista[i]
        j = i - 1
        while j >= 0 and lista[j] > chave:
            lista[j + 1] = lista[j]
            j -= 1
        lista[j + 1] = chave

def comparar_listas(a, b):
    # Devolve True se a > b lexicograficamente
    n = len(a) if len(a) < len(b) else len(b)
    for i in range(n):
        if a[i] != b[i]:
            return a[i] > b[i]
    return len(a) > len(b)

def ordenar_grades(grades):
    n = len(grades)
    for i in range(1, n):
        chave = grades[i]
        j = i - 1
        while j >= 0 and comparar_listas(grades[j], chave):
            grades[j + 1] = grades[j]
            j -= 1
        grades[j + 1] = chave

def encontrar_ciclo(codigos_matriz, prereqs_por_cod):
    # Estados: 0 = não visitado, 1 = na pilha, 2 = finalizado
    estado = {}
    for i in range(len(codigos_matriz)):
        estado[codigos_matriz[i]] = 0

    caminho = []

    def dfs(atual):
        estado[atual] = 1
        caminho.append(atual)

        prereqs = prereqs_por_cod[atual]
        for i in range(len(prereqs)):
            viz = prereqs[i]
            if estado[viz] == 1:
                # Extrair apenas o pedaço do caminho que forma o ciclo
                ciclo = []
                copiando = False
                for k in range(len(caminho)):
                    if caminho[k] == viz:
                        copiando = True
                    if copiando:
                        ciclo.append(caminho[k])
                ciclo.append(viz)
                return ciclo
            elif estado[viz] == 0:
                res = dfs(viz)
                if res is not None:
                    return res

        caminho.pop()
        estado[atual] = 2
        return None

    for i in range(len(codigos_matriz)):
        cod = codigos_matriz[i]
        if estado[cod] == 0:
            ciclo_achado = dfs(cod)
            if ciclo_achado is not None:
                return ciclo_achado
    return None

def resolver_matricula(matriz_raw, oferta_raw, aluno_raw):
    codigos_matriz = []
    ch_por_cod = {}
    prereqs_por_cod = {}

    for i in range(len(matriz_raw)):
        item = matriz_raw[i]
        c = item["codigo"]
        codigos_matriz.append(c)
        ch_por_cod[c] = item["ch"]
        p_lista = []
        for j in range(len(item["prereqs"])):
            p_lista.append(item["prereqs"][j])
        ordenar_strings(p_lista)
        prereqs_por_cod[c] = p_lista

    ordenar_strings(codigos_matriz)

    ciclo = encontrar_ciclo(codigos_matriz, prereqs_por_cod)
    if ciclo is not None:
        return {
            "ciclo": ciclo,
            "liberadas": None,
            "bloqueadas": None,
            "grades_maximas": None
        }

    aprovadas = aluno_raw["aprovadas"]
    teto = aluno_raw["teto"]

    codigos_oferta = []
    horarios_por_cod = {}
    for i in range(len(oferta_raw)):
        item = oferta_raw[i]
        c = item["codigo"]
        codigos_oferta.append(c)
        horarios_por_cod[c] = item["horarios"]

    ordenar_strings(codigos_oferta)

    liberadas = []
    bloqueadas = []

    for i in range(len(codigos_oferta)):
        cod = codigos_oferta[i]
        if contem(aprovadas, cod):
            continue  # Já cursou

        req = prereqs_por_cod[cod]
        faltam = []
        for j in range(len(req)):
            if not contem(aprovadas, req[j]):
                faltam.append(req[j])

        if len(faltam) == 0:
            liberadas.append(cod)
        else:
            ordenar_strings(faltam)
            bloqueadas.append({"codigo": cod, "faltam": faltam})

    n_lib = len(liberadas)
    maior_qtd = 0
    grades_maximas = [[]]

    total_mascaras = 1 << n_lib
    for mask in range(1, total_mascaras):
        candidata = []
        soma_ch = 0

        for i in range(n_lib):
            if ((mask >> i) & 1) == 1:
                disc = liberadas[i]
                candidata.append(disc)
                soma_ch = soma_ch + ch_por_cod[disc]

        if soma_ch > teto:
            continue

        tem_conflito = False
        for i in range(len(candidata)):
            for j in range(i + 1, len(candidata)):
                h1 = horarios_por_cod[candidata[i]]
                h2 = horarios_por_cod[candidata[j]]
                for k in range(len(h1)):
                    if contem(h2, h1[k]):
                        tem_conflito = True
                        break
                if tem_conflito:
                    break
            if tem_conflito:
                break

        if tem_conflito:
            continue

        qtd = len(candidata)
        if qtd > maior_qtd:
            maior_qtd = qtd
            grades_maximas = [candidata]
        elif qtd == maior_qtd:
            grades_maximas.append(candidata)

    ordenar_grades(grades_maximas)

    return {
        "ciclo": None,
        "liberadas": liberadas,
        "bloqueadas": bloqueadas,
        "grades_maximas": grades_maximas
    }
