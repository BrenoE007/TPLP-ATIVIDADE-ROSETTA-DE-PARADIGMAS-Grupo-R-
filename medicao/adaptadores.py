"""Fronteira de entrada comum para as implementações EXISTENTES do grupo.

A normalização acontece antes da região cronometrada no regime quente.
Nenhum algoritmo de resolução foi reescrito neste módulo.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Callable

RAIZ = Path(__file__).resolve().parent.parent
VERSOES = ("imperativa", "funcional", "oo")


def ler_entradas(matriz: Path, oferta: Path, historico: Path) -> tuple[list, list, dict]:
    with matriz.open(encoding="utf-8") as arquivo:
        materias = json.load(arquivo)["disciplinas"]
    with oferta.open(encoding="utf-8") as arquivo:
        ofertas = json.load(arquivo)["oferta"]
    with historico.open(encoding="utf-8") as arquivo:
        aluno = json.load(arquivo)
    return materias, ofertas, aluno


def _ofertas_com_horarios_textuais(ofertas: list) -> list:
    # Ambas as versões existentes usam igualdade de strings para horários.
    return [
        {
            "codigo": oferta["codigo"],
            "horarios": [f'{h["dia"]}/{h["turno"]}' for h in oferta["horarios"]],
        }
        for oferta in ofertas
    ]


def preparar(
    versao: str, matriz: list, oferta: list, historico: dict
) -> Callable[[], dict]:
    """Cria uma função que executa as quatro perguntas sobre entradas já preparadas.

    Cada chamada retorna um dicionário JSON-equivalente. Todas as conversões
    necessárias entre formatos ficam FORA da função cronometrada no modo quente.
    """
    if versao == "imperativa":
        from imperativa import imperativo

        # Imperativo.py lê 'prereqs' e 'teto'; JSON oficial usa outros nomes.
        matriz_compat = [
            {"codigo": d["codigo"], "ch": d["ch"],
             "prereqs": list(d["prerequisitos"])}
            for d in matriz
        ]
        oferta_compat = _ofertas_com_horarios_textuais(oferta)
        aluno_compat = {
            "aprovadas": list(historico["aprovadas"]),
            "teto": historico["teto_ch"],
        }

        def executar() -> dict:
            return imperativo.resolver_matricula(matriz_compat, oferta_compat, aluno_compat)

        return executar

    if versao == "funcional":
        from Funcional import funcional

        # congelar_dados() espera coleções de registros, 'prereqs' e 'teto'.
        matriz_compat = [
            {"codigo": d["codigo"], "ch": d["ch"],
             "prereqs": list(d["prerequisitos"])}
            for d in matriz
        ]
        oferta_compat = _ofertas_com_horarios_textuais(oferta)
        aluno_compat = {
            "aprovadas": list(historico["aprovadas"]),
            "teto": historico["teto_ch"],
        }
        matriz_tup, oferta_tup, aprovadas, teto = funcional.congelar_dados(
            matriz_compat, oferta_compat, aluno_compat
        )

        def executar() -> dict:
            resultado = funcional.resolver_funcional(matriz_tup, oferta_tup, aprovadas, teto)
            return funcional.formatar_para_json(resultado)

        return executar

    if versao == "oo":
        from oo.dominio import (
            Aluno, Disciplina, DisciplinaOfertada, Horario,
            MatrizCurricular, PlanejadorDeMatricula,
        )

        disciplinas = [
            Disciplina(
                codigo=d["codigo"], nome=d["nome"], ch=d["ch"],
                prerequisitos=tuple(d["prerequisitos"]),
            )
            for d in matriz
        ]
        curriculo = MatrizCurricular(disciplinas)
        aluno = Aluno(
            aprovadas=frozenset(historico["aprovadas"]),
            teto_ch=historico["teto_ch"],
        )
        disciplinas_ofertadas = [
            DisciplinaOfertada(
                disciplina=curriculo.disciplina(d["codigo"]),
                horarios=frozenset(
                    Horario(dia=h["dia"], turno=h["turno"])
                    for h in d["horarios"]
                ),
            )
            for d in oferta
        ]
        planejador = PlanejadorDeMatricula(curriculo, aluno, disciplinas_ofertadas)
        return planejador.analisar

    raise ValueError(f"Versão desconhecida: {versao}")
