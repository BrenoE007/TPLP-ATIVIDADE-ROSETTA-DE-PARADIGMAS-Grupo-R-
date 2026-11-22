"""Confere a equivalencia semantica dos cinco casos com o arquivo original."""

import json
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PYTHON = sys.executable
MAIN = RAIZ / "oo" / "main.py"
DADOS = RAIZ / "dados"

CASOS = {
    "caso1": ("matriz.json", "historico.json"),
    "caso2": ("caso2_ciclo.json", "historico.json"),
    "caso3": ("matriz.json", "caso3_historico_vazio.json"),
    "caso4": ("matriz.json", "caso4_historico_completo.json"),
    "caso5": ("matriz.json", "caso5_teto_reduzido.json"),
}


def executar() -> None:
    esperado = json.loads((RAIZ / "saidas_esperadas.json").read_text(encoding="utf-8"))
    for caso, (matriz, historico) in CASOS.items():
        processo = subprocess.run(
            [
                PYTHON, str(MAIN),
                "--matriz", str(DADOS / matriz),
                "--oferta", str(DADOS / "oferta.json"),
                "--historico", str(DADOS / historico),
            ],
            text=True,
            capture_output=True,
            check=True,
        )
        obtido = json.loads(processo.stdout)
        assert obtido == esperado[caso], (
            f"{caso} divergiu do gabarito.\n"
            f"Esperado: {esperado[caso]}\nObtido: {obtido}"
        )
        print(f"{caso}: OK")
    print("Os 5 casos passaram.")


if __name__ == "__main__":
    executar()
