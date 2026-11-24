"""Um comando: verifica as três implementações nos cinco casos oficiais.

Executar a partir da raiz: python -m medicao.testar
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from medicao.adaptadores import RAIZ, VERSOES

DADOS = RAIZ / "dados"
CASOS = {
    "caso1": ("matriz.json", "historico.json"),
    "caso2": ("caso2_ciclo.json", "historico.json"),
    "caso3": ("matriz.json", "caso3_historico_vazio.json"),
    "caso4": ("matriz.json", "caso4_historico_completo.json"),
    "caso5": ("matriz.json", "caso5_teto_reduzido.json"),
}


def executar_versao(versao: str, matriz: Path, historico: Path) -> dict:
    comando = [
        sys.executable, "-m", "medicao.executar", "--versao", versao,
        "--matriz", str(matriz), "--oferta", str(DADOS / "oferta.json"),
        "--historico", str(historico),
    ]
    processo = subprocess.run(
        comando, cwd=RAIZ, capture_output=True, text=True, encoding="utf-8", check=True
    )
    return json.loads(processo.stdout)


def verificar() -> None:
    gabarito = json.loads((RAIZ / "saidas_esperadas.json").read_text(encoding="utf-8"))
    falhas = []
    for nome, (matriz, historico) in CASOS.items():
        for versao in VERSOES:
            try:
                resultado = executar_versao(versao, DADOS / matriz, DADOS / historico)
                if resultado != gabarito[nome]:
                    falhas.append(f"{versao}/{nome}: resultado diferente do gabarito")
                    print(f"FALHOU {versao:10} {nome}")
                else:
                    print(f"OK     {versao:10} {nome}")
            except (OSError, subprocess.CalledProcessError, json.JSONDecodeError) as exc:
                falhas.append(f"{versao}/{nome}: {exc}")
                print(f"ERRO   {versao:10} {nome}: {exc}")
    if falhas:
        raise SystemExit("\n" + "\n".join(falhas))
    print("\nTodas as 15 combinações (3 versões × 5 casos) passaram.")


if __name__ == "__main__":
    verificar()
