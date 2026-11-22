"""Leitura de JSON e saida padronizada (sem log na saida padrao)."""

import argparse
import json
from pathlib import Path

from dominio import (
    Aluno,
    Disciplina,
    DisciplinaOfertada,
    Horario,
    MatrizCurricular,
    PlanejadorDeMatricula,
)

RAIZ = Path(__file__).resolve().parent.parent


def carregar_json(caminho: Path) -> dict:
    with caminho.open(encoding="utf-8") as arquivo:
        return json.load(arquivo)


def construir_planejador(
    caminho_matriz: Path, caminho_oferta: Path, caminho_historico: Path
) -> PlanejadorDeMatricula:
    dados_matriz = carregar_json(caminho_matriz)
    dados_oferta = carregar_json(caminho_oferta)
    dados_historico = carregar_json(caminho_historico)

    disciplinas = [
        Disciplina(
            codigo=item["codigo"],
            nome=item["nome"],
            ch=item["ch"],
            prerequisitos=tuple(item["prerequisitos"]),
        )
        for item in dados_matriz["disciplinas"]
    ]
    matriz = MatrizCurricular(disciplinas)
    aluno = Aluno(
        aprovadas=frozenset(dados_historico["aprovadas"]),
        teto_ch=dados_historico["teto_ch"],
    )
    ofertas = [
        DisciplinaOfertada(
            disciplina=matriz.disciplina(item["codigo"]),
            horarios=frozenset(
                Horario(dia=h["dia"], turno=h["turno"])
                for h in item["horarios"]
            ),
        )
        for item in dados_oferta["oferta"]
    ]
    return PlanejadorDeMatricula(matriz, aluno, ofertas)


def main() -> None:
    parser = argparse.ArgumentParser(description="T2 - Versao orientada a objetos")
    parser.add_argument(
        "--matriz", type=Path, default=RAIZ / "dados" / "matriz.json"
    )
    parser.add_argument(
        "--oferta", type=Path, default=RAIZ / "dados" / "oferta.json"
    )
    parser.add_argument(
        "--historico", type=Path, default=RAIZ / "dados" / "historico.json"
    )
    args = parser.parse_args()

    resultado = construir_planejador(args.matriz, args.oferta, args.historico).analisar()
    print(json.dumps(resultado, ensure_ascii=False))


if __name__ == "__main__":
    main()
