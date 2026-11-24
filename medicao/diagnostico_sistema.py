"""Diagnóstico comparativo de criação de processos no Windows.

Uso, na raiz do repositório:
    python -m medicao.diagnostico_sistema

Não altera arquivos das três implementações. Usa somente a biblioteca padrão.
"""

import csv
import os
import random
import statistics
import subprocess
import sys
import time
from pathlib import Path


REPETICOES_POR_CENARIO = 20
LIMIAR_LENTO_MS = 500.0


def medir(comando):
    inicio = time.perf_counter_ns()
    processo = subprocess.Popen(
        comando,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    criado = time.perf_counter_ns()
    codigo = processo.wait()
    fim = time.perf_counter_ns()
    return (
        (criado - inicio) / 1_000_000,
        (fim - criado) / 1_000_000,
        (fim - inicio) / 1_000_000,
        codigo,
    )


def main():
    if os.name != "nt":
        print("Este diagnóstico foi preparado para Windows (cmd.exe).")
        return 2

    python_cmd = [sys.executable, "-c", "pass"]
    windows_cmd = [os.environ.get("ComSpec", "cmd.exe"), "/d", "/c", "exit /b 0"]
    cenarios = {
        "python_vazio": python_cmd,
        "cmd_windows_vazio": windows_cmd,
    }

    # Mesma quantidade de cada cenário, mas ordem embaralhada para não
    # confundir um atraso alternado entre processos com um efeito do programa.
    ordem = [nome for nome in cenarios for _ in range(REPETICOES_POR_CENARIO)]
    random.Random(20261123).shuffle(ordem)

    destino = Path("medicao") / "resultados" / "diagnostico_sistema.csv"
    destino.parent.mkdir(parents=True, exist_ok=True)
    registros = []

    print("Teste de controle de criacao de processos (Python x cmd.exe)")
    print(f"Interpretador: {sys.executable}")
    print(f"Quantidade: {len(ordem)} execucoes, ordem embaralhada.\n")

    for pos, nome in enumerate(ordem, start=1):
        criacao, espera, total, codigo = medir(cenarios[nome])
        registro = {
            "ordem_global": pos,
            "cenario": nome,
            "criacao_ms": round(criacao, 3),
            "espera_ms": round(espera, 3),
            "total_ms": round(total, 3),
            "codigo_saida": codigo,
        }
        registros.append(registro)
        if codigo != 0:
            print(f"ATENCAO: execucao {pos} terminou com codigo {codigo}")

    with destino.open("w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=list(registros[0]))
        escritor.writeheader()
        escritor.writerows(registros)

    print("RESUMO (ms):")
    for nome in cenarios:
        itens = [r for r in registros if r["cenario"] == nome]
        tempos = [r["criacao_ms"] for r in itens]
        lentos = sum(t >= LIMIAR_LENTO_MS for t in tempos)
        print(
            f"{nome}: criacao minima={min(tempos):.2f}, "
            f"mediana={statistics.median(tempos):.2f}, "
            f"maxima={max(tempos):.2f}, "
            f"criacao >=500 ms={lentos}/{len(tempos)}"
        )
    print(f"\nCSV salvo em: {destino}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
