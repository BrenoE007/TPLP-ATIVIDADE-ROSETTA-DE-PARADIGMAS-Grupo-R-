"""Diagnóstico de atrasos intermitentes na medição fria do T2.

Coloque este arquivo em medicao/diagnostico_frio.py e execute, na raiz:
    python -m medicao.diagnostico_frio

Não altera os algoritmos nem os resultados já existentes.
"""
from __future__ import annotations

import csv
import statistics
import subprocess
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DESTINO = RAIZ / "medicao" / "resultados" / "diagnostico_frio.csv"
REPETICOES = 20


def medir(nome: str, comando: list[str], capturar: bool) -> float:
    inicio = time.perf_counter_ns()
    retorno = subprocess.run(
        comando,
        cwd=RAIZ,
        stdout=subprocess.PIPE if capturar else subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )
    duracao_ms = (time.perf_counter_ns() - inicio) / 1_000_000
    if retorno.returncode != 0:
        erro = retorno.stderr.decode("utf-8", errors="replace")
        raise RuntimeError(f"Falha em {nome}: {erro}")
    return duracao_ms


def main() -> None:
    simples = [sys.executable, "-c", "print('ok')"]
    projeto = [
        sys.executable, "-m", "medicao.executar",
        "--versao", "oo", "--modo", "frio",
    ]
    casos = [
        ("python_simples_capturado", simples, True),
        ("python_simples_sem_captura", simples, False),
        ("programa_oo_capturado", projeto, True),
    ]
    resultados = {nome: [] for nome, _, _ in casos}
    linhas = []
    print(f"Interpretador: {sys.executable}")
    print(f"Rodando {REPETICOES} repetições por cenário...", flush=True)
    for i in range(1, REPETICOES + 1):
        for nome, comando, capturar in casos:
            tempo = medir(nome, comando, capturar)
            resultados[nome].append(tempo)
            linhas.append({"cenario": nome, "iteracao": i, "duracao_ms": f"{tempo:.6f}"})
        print(f"Repetição {i}/{REPETICOES} concluída", flush=True)

    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    with DESTINO.open("w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=["cenario", "iteracao", "duracao_ms"])
        escritor.writeheader()
        escritor.writerows(linhas)

    print("\nRESUMO (milissegundos)")
    for nome, _, _ in casos:
        valores = resultados[nome]
        lentas = sum(v >= 500 for v in valores)
        print(
            f"{nome}: minimo={min(valores):.2f}, "
            f"mediana={statistics.median(valores):.2f}, "
            f"maximo={max(valores):.2f}, "
            f"execucoes >=500ms={lentas}/{len(valores)}"
        )
    print(f"\nDados detalhados em: {DESTINO}")


if __name__ == "__main__":
    main()
