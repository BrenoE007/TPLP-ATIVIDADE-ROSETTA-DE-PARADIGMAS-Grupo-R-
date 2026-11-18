import json
import sys
from functools import reduce

def buscar_disc(matriz_tup, codigo):
    encontrados = tuple(filter(lambda d: d[0] == codigo, matriz_tup))
    return encontrados[0] if len(encontrados) > 0 else None


def extrair_ciclo(caminho, alvo):
    if caminho[0] == alvo:
        return caminho + (alvo,)
    return extrair_ciclo(caminho[1:], alvo)


def encontrar_ciclo(matriz_tup):

    codigos_ordenados = tuple(sorted(map(lambda d: d[0], matriz_tup)))

    def prereqs_de(cod):
        d = buscar_disc(matriz_tup, cod)
        return tuple(sorted(d[2])) if d is not None else ()

    def explorar_vizinhos(vizinhos, visitados, caminho):
        if not vizinhos:
            return visitados, None
        v = vizinhos[0]
        resto = vizinhos[1:]

        if v in caminho:
            return visitados, extrair_ciclo(caminho, v)
        if v in visitados:
            return explorar_vizinhos(resto, visitados, caminho)

        novos_visitados, ciclo = dfs_no(v, visitados, caminho)
        if ciclo is not None:
            return novos_visitados, ciclo
        return explorar_vizinhos(resto, novos_visitados, caminho)

    def dfs_no(u, visitados, caminho):
        novos_visitados, ciclo = explorar_vizinhos(
            prereqs_de(u), visitados, caminho + (u,)
        )
        if ciclo is not None:
            return novos_visitados, ciclo
        return novos_visitados | frozenset((u,)), None

    def iterar_componentes(codigos, visitados):
        if not codigos:
            return None
        c = codigos[0]
        if c in visitados:
            return iterar_componentes(codigos[1:], visitados)
        novos_visitados, ciclo = dfs_no(c, visitados, ())
        if ciclo is not None:
            return ciclo
        return iterar_componentes(codigos[1:], novos_visitados)

    return iterar_componentes(codigos_ordenados, frozenset())


def calcular_liberadas_e_bloqueadas(matriz_tup, oferta_tup, aprovadas_fset):

    oferta_ordenada = tuple(sorted(oferta_tup, key=lambda o: o[0]))
    nao_cursadas = tuple(filter(lambda o: o[0] not in aprovadas_fset, oferta_ordenada))

    def faltantes_de(cod):
        disc = buscar_disc(matriz_tup, cod)
        prereqs = disc[2] if disc is not None else ()
        return tuple(sorted(filter(lambda p: p not in aprovadas_fset, prereqs)))

    avaliadas = tuple(map(lambda o: (o[0], faltantes_de(o[0])), nao_cursadas))

    liberadas = tuple(
        map(lambda par: par[0], filter(lambda par: len(par[1]) == 0, avaliadas))
    )
    bloqueadas = tuple(
        map(
            lambda par: (("codigo", par[0]), ("faltam", par[1])),
            filter(lambda par: len(par[1]) > 0, avaliadas),
        )
    )
    return liberadas, bloqueadas


def gerar_subconjuntos(elementos):

    if not elementos:
        return ((),)
    primeiro = elementos[0]
    sub_resto = gerar_subconjuntos(elementos[1:])
    com_primeiro = tuple(map(lambda s: (primeiro,) + s, sub_resto))
    return sub_resto + com_primeiro


def calcular_grades_maximas(liberadas, matriz_tup, oferta_tup, teto):

    def ch_de(cod):
        return buscar_disc(matriz_tup, cod)[1]

    def horarios_de(cod):
        enc = tuple(filter(lambda o: o[0] == cod, oferta_tup))
        return enc[0][1] if len(enc) > 0 else frozenset()

    def cabe_no_teto(grade):
        carga_total = reduce(lambda acc, c: acc + ch_de(c), grade, 0)
        return carga_total <= teto

    def sem_conflito_De_horario(grade):
        if len(grade) <= 1:
            return True
        cabeca = grade[0]
        cauda = grade[1:]
        h_cabeca = horarios_de(cabeca)
        conflita_com_cabeca = any(
            map(lambda outro: len(h_cabeca & horarios_de(outro)) > 0, cauda)
        )
        return (not conflita_com_cabeca) and sem_conflito_De_horario(cauda)

    todas_candidatas = gerar_subconjuntos(liberadas)
    grades_validas = tuple(
        filter(
            lambda g: cabe_no_teto(g) and sem_conflito_De_horario(g),
            todas_candidatas,
        )
    )

    maior_tamanho = reduce(
        lambda acc, g: len(g) if len(g) > acc else acc, grades_validas, 0
    )
    melhores = tuple(filter(lambda g: len(g) == maior_tamanho, grades_validas))
    return tuple(sorted(melhores))


def resolver_funcional(matriz_tup, oferta_tup, aprovadas_fset, teto):

    ciclo = encontrar_ciclo(matriz_tup)
    if ciclo is not None:
        return (
            ("ciclo", ciclo),
            ("liberadas", None),
            ("bloqueadas", None),
            ("grades_maximas", None),
        )

    liberadas, bloqueadas = calcular_liberadas_e_bloqueadas(
        matriz_tup, oferta_tup, aprovadas_fset
    )
    grades_maximas = calcular_grades_maximas(
        liberadas, matriz_tup, oferta_tup, teto
    )

    return (
        ("ciclo", None),
        ("liberadas", liberadas),
        ("bloqueadas", bloqueadas),
        ("grades_maximas", grades_maximas),
    )

def congelar_dados(matriz_raw, oferta_raw, historico_raw):

    # Suporta chave 'pre_requisitos' ou 'prereqs' conforme o arquivo
    matriz_tup = tuple(
        map(
            lambda item: (
                item["codigo"],
                item["ch"],
                tuple(item.get("pre_requisitos", item.get("prereqs", []))),
            ),
            matriz_raw,
        )
    )
    oferta_tup = tuple(
        map(
            lambda item: (item["codigo"], frozenset(item["horarios"])),
            oferta_raw,
        )
    )
    if isinstance(historico_raw, dict):
        aprovadas = frozenset(
            historico_raw.get("aprovadas", historico_raw.get("disciplinas_aprovadas", ()))
        )
        teto = historico_raw.get("teto", historico_raw.get("teto_horas", 240))
    else:
        aprovadas = frozenset(historico_raw)
        teto = 240

    return matriz_tup, oferta_tup, aprovadas, teto


def formatar_para_json(res_tupla):
    d = dict(res_tupla)
    if d["ciclo"] is not None:
        return {
            "ciclo": list(d["ciclo"]),
            "liberadas": None,
            "bloqueadas": None,
            "grades_maximas": None,
        }
    return {
        "ciclo": None,
        "liberadas": list(d["liberadas"]),
        "bloqueadas": list(
            map(
                lambda b: {"codigo": dict(b)["codigo"], "faltam": list(dict(b)["faltam"])},
                d["bloqueadas"],
            )
        ),
        "grades_maximas": list(map(list, d["grades_maximas"])),
    }


def main():
    c_matriz = sys.argv[1] if len(sys.argv) > 1 else "dados/matriz.json"
    c_oferta = sys.argv[2] if len(sys.argv) > 2 else "dados/oferta.json"
    c_hist = sys.argv[3] if len(sys.argv) > 3 else "dados/historico.json"

    with open(c_matriz, "r", encoding="utf-8") as f1, \
         open(c_oferta, "r", encoding="utf-8") as f2, \
         open(c_hist, "r", encoding="utf-8") as f3:
        m_raw, o_raw, h_raw = json.load(f1), json.load(f2), json.load(f3)

    matriz_tup, oferta_tup, aprovadas_fset, teto = congelar_dados(m_raw, o_raw, h_raw)
    resposta_pura = resolver_funcional(matriz_tup, oferta_tup, aprovadas_fset, teto)
    print(json.dumps(formatar_para_json(resposta_pura), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
