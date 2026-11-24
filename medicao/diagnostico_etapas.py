"""Diagnostica em que fase ocorre o atraso das medições frias.

Coloque em medicao/diagnostico_etapas.py, na raiz do repositório execute:
    python -m medicao.diagnostico_etapas

Não altera as implementações nem os resultados anteriores.
"""
from __future__ import annotations

import argparse
import csv
import statistics
import subprocess
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CSV_SAIDA = RAIZ / "medicao" / "resultados" / "diagnostico_etapas.csv"


def medir(nome: str, comando: list[str], capturar: bool, iteracao: int, ordem: int) -> dict:
    inicio_ns = time.perf_counter_ns()
    filho = subprocess.Popen(
        comando,
        cwd=RAIZ,
        stdout=subprocess.PIPE if capturar else subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )
    apos_criacao_ns = time.perf_counter_ns()
    stdout, stderr = filho.communicate()
    final_ns = time.perf_counter_ns()

    if filho.returncode != 0:
        mensagem = stderr.decode("utf-8", errors="replace") if stderr else ""
        raise RuntimeError(f"{nome} falhou ({filho.returncode}): {mensagem}")

    return {
        "ordem_global": ordem,
        "iteracao": iteracao,
        "cenario": nome,
        "criacao_ms": round((apos_criacao_ns - inicio_ns) / 1e6, 3),
        "espera_ms": round((final_ns - apos_criacao_ns) / 1e6, 3),
        "total_ms": round((final_ns - inicio_ns) / 1e6, 3),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Cronometra criacao e espera de subprocessos")
    parser.add_argument("--repeticoes", type=int, default=20)
    args = parser.parse_args()
    if args.repeticoes < 1:
        parser.error("--repeticoes deve ser maior que zero")

    simples = [sys.executable, "-c", "print('ok')"]
    oo = [sys.executable, "-m", "medicao.executar", "--versao", "oo", "--modo", "frio"]
    cenarios = [
        ("python_simples_capturado", simples, True),
        ("python_simples_sem_captura", simples, False),
        ("programa_oo_capturado", oo, True),
    ]

    print(f"Python: {sys.executable}")
    print(f"Medindo {args.repeticoes} repeticoes em cada cenario (3 processos por repeticao)...", flush=True)
    linhas = []
    ordem_global = 0
    for iteracao in range(1, args.repeticoes + 1):
        for nome, comando, capturar in cenarios:
            ordem_global += 1
            linha = medir(nome, comando, capturar, iteracao, ordem_global)
            linhas.append(linha)
            print(
                f"{ordem_global:02d} {nome:28s} "
                f"criar={linha['criacao_ms']:8.2f} ms "
                f"esperar={linha['espera_ms']:8.2f} ms "
                f"total={linha['total_ms']:8.2f} ms",
                flush=True,
            )

    CSV_SAIDA.parent.mkdir(parents=True, exist_ok=True)
    with CSV_SAIDA.open("w", encoding="utf-8", newline="") as f:
        escritor = csv.DictWriter(f, fieldnames=[
            "ordem_global", "iteracao", "cenario", "criacao_ms", "espera_ms", "total_ms"
        ])
        escritor.writeheader()
        escritor.writerows(linhas)

    print("\nRESUMO DOS ATRASOS (>= 500 ms)")
    for coluna, rotulo in (("criacao_ms", "criacao"), ("espera_ms", "espera"), ("total_ms", "total")):
        valores = [r[coluna] for r in linhas]
        print(f"{rotulo}: {sum(v >= 500 for v in valores)}/{len(valores)} lentos; mediana={statistics.median(valores):.2f} ms")
    print(f"\nResultado salvo em: {CSV_SAIDA}")


if __name__ == "__main__":
    main()
