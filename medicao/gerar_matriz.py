"""Gerador determinístico de matriz curricular ampliada com 200 disciplinas.

Preserva as disciplinas oficiais, adiciona disciplinas fora da oferta e mantém
as dependências novas acíclicas. Não altera os dados fornecidos pelo professor.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from medicao.adaptadores import RAIZ

ARQUIVO_PADRAO = RAIZ / "medicao" / "dados" / "matriz_200.json"


def gerar(destino: Path = ARQUIVO_PADRAO, total: int = 200) -> Path:
    origem = RAIZ / "dados" / "matriz.json"
    matriz = json.loads(origem.read_text(encoding="utf-8"))
    existentes = matriz["disciplinas"]
    if total < len(existentes):
        raise ValueError("Total não pode ser inferior ao tamanho da matriz original")
    codigos = {d["codigo"] for d in existentes}
    originais = len(existentes)
    if not any(d["codigo"] == "CC0101" for d in existentes):
        raise ValueError("A matriz original precisa conter CC0101 para criar os pré-requisitos")

    novos = []
    numero = 1000
    while len(existentes) + len(novos) < total:
        codigo = f"CC{numero:04d}"
        numero += 1
        if codigo in codigos:
            continue
        pos = len(novos)
        # Cadeias de comprimento até 2, sem ciclos e sem dependências inexistentes.
        if pos % 3 == 0:
            requisitos = []
        elif pos % 3 == 1:
            requisitos = ["CC0101"]
        else:
            requisitos = [novos[pos - 1]["codigo"]]
        novos.append({
            "codigo": codigo,
            "nome": f"Disciplina Ampliada {pos + 1:03d}",
            "ch": 60 if pos % 4 else 30,
            "prerequisitos": requisitos,
        })
        codigos.add(codigo)

    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(
        json.dumps({"disciplinas": existentes + novos}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Matriz gerada: {destino} ({originais} originais + {len(novos)} novas = {total})")
    return destino


def main() -> None:
    parser = argparse.ArgumentParser(description="Gera matriz curricular com 200 disciplinas")
    parser.add_argument("--destino", type=Path, default=ARQUIVO_PADRAO)
    parser.add_argument("--total", type=int, default=200)
    args = parser.parse_args()
    gerar(args.destino, args.total)


if __name__ == "__main__":
    main()
