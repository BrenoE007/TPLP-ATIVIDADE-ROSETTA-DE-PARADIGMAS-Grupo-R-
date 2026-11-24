"""Medidor comparativo frio/quente com dados brutos, mediana, mínimo e IQR.

Execução completa: python -m medicao.medir
Apenas diagnóstico rápido: --repeticoes-frias 2 --iteracoes-quentes 20 --aquecimento 5
"""
from __future__ import annotations

import argparse
import csv
import json
import platform
import statistics
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from medicao.adaptadores import RAIZ, VERSOES
from medicao.gerar_matriz import ARQUIVO_PADRAO, gerar
from medicao.testar import DADOS, executar_versao, verificar


def percentil_ordenado(valores: list[int], p: float) -> float:
    """Percentil linear inclusivo: interpolação na posição (n - 1) * p."""
    ordenados = sorted(valores)
    posicao = (len(ordenados) - 1) * p
    inferior = int(posicao)
    superior = min(inferior + 1, len(ordenados) - 1)
    parcela = posicao - inferior
    return ordenados[inferior] + parcela * (ordenados[superior] - ordenados[inferior])


def resumir(duracoes_ns: list[int]) -> dict[str, float | int]:
    if not duracoes_ns:
        raise ValueError("Não há tempos para calcular estatísticas")
    # Todos os tempos de saída estão em milissegundos, inclusive os do quente.
    return {
        "amostras": len(duracoes_ns),
        "mediana_ms": round(statistics.median(duracoes_ns) / 1_000_000, 6),
        "minimo_ms": round(min(duracoes_ns) / 1_000_000, 6),
        "iqr_ms": round((percentil_ordenado(duracoes_ns, 0.75) -
                          percentil_ordenado(duracoes_ns, 0.25)) / 1_000_000, 6),
    }


def comando_runner(versao: str, matriz: Path, modo: str,
                    iteracoes: int, aquecimento: int) -> list[str]:
    return [
        sys.executable, "-m", "medicao.executar", "--versao", versao,
        "--modo", modo, "--matriz", str(matriz),
        "--oferta", str(DADOS / "oferta.json"),
        "--historico", str(DADOS / "historico.json"),
        "--iteracoes", str(iteracoes), "--aquecimento", str(aquecimento),
    ]


def processo(comando: list[str]) -> subprocess.CompletedProcess[str]:
    retorno = subprocess.run(
        comando, cwd=RAIZ, capture_output=True, text=True, encoding="utf-8"
    )
    if retorno.returncode != 0:
        raise RuntimeError(
            f"Falha na execução de {' '.join(comando)}\n"
            f"STDERR: {retorno.stderr}\nSTDOUT: {retorno.stdout}"
        )
    return retorno


def medir_frio(versao: str, matriz: Path, repeticoes: int, esperado: dict) -> list[int]:
    comando = comando_runner(versao, matriz, "frio", 1, 0)
    duracoes = []
    for _ in range(repeticoes):
        inicio = time.perf_counter_ns()
        retorno = processo(comando)
        duracoes.append(time.perf_counter_ns() - inicio)
        resultado = json.loads(retorno.stdout)
        if resultado != esperado:
            raise ValueError(f"Resultado incorreto: {versao} / {matriz.name}, regime frio")
    return duracoes


def medir_quente(versao: str, matriz: Path, iteracoes: int, aquecimento: int,
                  esperado: dict) -> list[int]:
    retorno = processo(comando_runner(versao, matriz, "quente", iteracoes, aquecimento))
    dados = json.loads(retorno.stdout)
    if dados["ultimo_resultado"] != esperado:
        raise ValueError(f"Resultado incorreto: {versao} / {matriz.name}, regime quente")
    duracoes = dados["duracoes_ns"]
    if len(duracoes) != iteracoes:
        raise ValueError("O processo filho não devolveu todas as iterações")
    return duracoes


def salvar_csv(caminho: Path, colunas: list[str], registros: list[dict]) -> None:
    with caminho.open("w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=colunas)
        escritor.writeheader()
        escritor.writerows(registros)


def main() -> None:
    parser = argparse.ArgumentParser(description="Arnês frio/quente das 3 versões")
    parser.add_argument("--repeticoes-frias", type=int, default=20)
    parser.add_argument("--iteracoes-quentes", type=int, default=1000)
    parser.add_argument("--aquecimento", type=int, default=100)
    parser.add_argument("--cenarios", choices=("ambos", "original", "ampliado"),
                        default="ambos")
    parser.add_argument("--saida", type=Path, default=RAIZ / "medicao" / "resultados")
    args = parser.parse_args()
    if args.repeticoes_frias < 1 or args.iteracoes_quentes < 1 or args.aquecimento < 0:
        parser.error("Repetições/iterações devem ser positivas; aquecimento >= 0")
    if args.repeticoes_frias < 20 or args.iteracoes_quentes < 1000:
        print("AVISO: execução de diagnóstico; não atende à quantidade de repetições do enunciado.",
              file=sys.stderr)

    print("Verificando equivalência dos 5 casos antes da medição...", flush=True)
    verificar()
    gerar(ARQUIVO_PADRAO)

    esperado = json.loads((RAIZ / "saidas_esperadas.json").read_text(encoding="utf-8"))["caso1"]
    cenarios = []
    if args.cenarios in ("ambos", "original"):
        cenarios.append(("original", DADOS / "matriz.json"))
    if args.cenarios in ("ambos", "ampliado"):
        cenarios.append(("ampliado_200", ARQUIVO_PADRAO))

    # Validação do cenário ampliado: o gerador preserva a oferta e a matriz original.
    for nome, matriz in cenarios:
        for versao in VERSOES:
            resultado = executar_versao(versao, matriz, DADOS / "historico.json")
            if resultado != esperado:
                raise ValueError(f"{versao} falhou na validação prévia: {nome}")

    saida = args.saida.resolve()
    saida.mkdir(parents=True, exist_ok=True)
    brutos = []
    resumos = []

    # Alternar o ponto de partida reduz o viés de ordem nas execuções frias.
    for nome, matriz in cenarios:
        print(f"\nCenário: {nome} ({matriz.name})", flush=True)
        frio = {versao: [] for versao in VERSOES}
        for repeticao in range(args.repeticoes_frias):
            ordem = VERSOES[repeticao % len(VERSOES):] + VERSOES[:repeticao % len(VERSOES)]
            for versao in ordem:
                frio[versao].extend(medir_frio(versao, matriz, 1, esperado))
        for versao in VERSOES:
            dados = frio[versao]
            estatisticas = resumir(dados)
            resumos.append({"cenario": nome, "regime": "frio", "versao": versao,
                            **estatisticas})
            brutos.extend({"cenario": nome, "regime": "frio", "versao": versao,
                           "iteracao": i + 1, "duracao_ns": valor}
                          for i, valor in enumerate(dados))
            print(f"  Frio   {versao:10} mediana={estatisticas['mediana_ms']:.4f} ms", flush=True)

        for versao in VERSOES:
            dados = medir_quente(versao, matriz, args.iteracoes_quentes, args.aquecimento,
                                 esperado)
            estatisticas = resumir(dados)
            resumos.append({"cenario": nome, "regime": "quente", "versao": versao,
                            **estatisticas})
            brutos.extend({"cenario": nome, "regime": "quente", "versao": versao,
                           "iteracao": i + 1, "duracao_ns": valor}
                          for i, valor in enumerate(dados))
            print(f"  Quente {versao:10} mediana={estatisticas['mediana_ms']:.4f} ms", flush=True)

    salvar_csv(saida / "amostras.csv", ["cenario", "regime", "versao", "iteracao", "duracao_ns"], brutos)
    salvar_csv(saida / "resumo.csv", ["cenario", "regime", "versao", "amostras",
                                      "mediana_ms", "minimo_ms", "iqr_ms"], resumos)
    dados_json = {
        "gerado_em_utc": datetime.now(timezone.utc).isoformat(),
        "ambiente": {
            "sistema": platform.platform(),
            "python": sys.version,
            "implementacao_python": platform.python_implementation(),
            "processador": platform.processor() or "não informado pelo sistema",
            "arquitetura": platform.machine(),
        },
        "metodo": {
            "repeticoes_frias": args.repeticoes_frias,
            "iteracoes_quentes": args.iteracoes_quentes,
            "aquecimento_descartado": args.aquecimento,
            "percentis": "interpolação linear na posição (n - 1) * p; IQR = P75 - P25",
            "unidade_resumo": "milissegundos",
            "relogio": "time.perf_counter_ns()",
            "frio": "processo filho novo + import + leitura + adaptação + resolução + stdout",
            "quente": "mesmo processo; somente resolução e formatação do objeto de resposta; sem E/S",
        },
        "resumos": resumos,
    }
    (saida / "resumo.json").write_text(
        json.dumps(dados_json, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"\nArquivos gerados em {saida}:", flush=True)
    print("  amostras.csv, resumo.csv, resumo.json", flush=True)


if __name__ == "__main__":
    main()
