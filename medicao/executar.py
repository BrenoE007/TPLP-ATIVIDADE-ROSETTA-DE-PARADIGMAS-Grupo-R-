"""Processo-filho, invocado tanto para medir startup quanto para medir o regime quente.

Exemplos (na raiz do repositório):
  python -m medicao.executar --versao imperativa
  python -m medicao.executar --versao funcional --modo quente
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from medicao.adaptadores import RAIZ, VERSOES, ler_entradas, preparar


def main() -> None:
    parser = argparse.ArgumentParser(description="Executa uma implementação via adaptador")
    parser.add_argument("--versao", choices=VERSOES, required=True)
    parser.add_argument("--modo", choices=("frio", "quente"), default="frio")
    parser.add_argument("--matriz", type=Path, default=RAIZ / "dados" / "matriz.json")
    parser.add_argument("--oferta", type=Path, default=RAIZ / "dados" / "oferta.json")
    parser.add_argument("--historico", type=Path, default=RAIZ / "dados" / "historico.json")
    parser.add_argument("--iteracoes", type=int, default=1000)
    parser.add_argument("--aquecimento", type=int, default=100)
    args = parser.parse_args()

    if args.iteracoes <= 0 or args.aquecimento < 0:
        parser.error("Iterações devem ser positivas e aquecimento não pode ser negativo")

    matriz, oferta, historico = ler_entradas(args.matriz, args.oferta, args.historico)
    resolver = preparar(args.versao, matriz, oferta, historico)

    if args.modo == "frio":
        resultado = resolver()
        print(json.dumps(resultado, ensure_ascii=False, separators=(",", ":")))
        return

    # Um ÚNICO processo: parsing, import e construção do modelo ficam fora
    # da medição. Cada medição executa as quatro perguntas integralmente.
    for _ in range(args.aquecimento):
        resolver()

    duracoes_ns = []
    ultimo = None
    for _ in range(args.iteracoes):
        inicio = time.perf_counter_ns()
        ultimo = resolver()
        duracoes_ns.append(time.perf_counter_ns() - inicio)

    print(json.dumps({"duracoes_ns": duracoes_ns, "ultimo_resultado": ultimo},
                     ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
