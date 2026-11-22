"""Entidades e regras da versao orientada a objetos do T2 Rosetta de Paradigmas.

Cada entidade e responsavel por decisoes relacionadas aos dados que possui.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class Aluno:
    aprovadas: frozenset[str]
    teto_ch: int

    def aprovou(self, codigo: str) -> bool:
        """Informa se o aluno ja concluiu uma disciplina."""
        return codigo in self.aprovadas


@dataclass(frozen=True)
class Disciplina:
    codigo: str
    nome: str
    ch: int
    prerequisitos: tuple[str, ...]

    def prerequisitos_faltantes(self, aluno: Aluno) -> list[str]:
        """Apenas requisitos DIRETOS: a regra pertence a Disciplina."""
        return sorted(
            codigo for codigo in self.prerequisitos if not aluno.aprovou(codigo)
        )

    def pode_ser_cursada_por(self, aluno: Aluno) -> bool:
        return not aluno.aprovou(self.codigo) and not self.prerequisitos_faltantes(aluno)


@dataclass(frozen=True)
class Horario:
    dia: str
    turno: str


@dataclass(frozen=True)
class DisciplinaOfertada:
    disciplina: Disciplina
    horarios: frozenset[Horario]

    def conflita_com(self, outra: DisciplinaOfertada) -> bool:
        """Dois encontros coincidem quando dia E turno sao iguais."""
        return not self.horarios.isdisjoint(outra.horarios)


class MatrizCurricular:
    def __init__(self, disciplinas: list[Disciplina]):
        self._disciplinas = {d.codigo: d for d in disciplinas}

    def disciplina(self, codigo: str) -> Disciplina:
        return self._disciplinas[codigo]

    def detectar_ciclo(self) -> list[str] | None:
        """DFS com estados: 0 (nao visitado), 1 (na pilha), 2 (concluido)."""
        estado: dict[str, int] = {}
        caminho: list[str] = []
        posicao_na_pilha: dict[str, int] = {}

        def visitar(codigo: str) -> list[str] | None:
            estado[codigo] = 1
            posicao_na_pilha[codigo] = len(caminho)
            caminho.append(codigo)

            atual = self.disciplina(codigo)
            for requisito in sorted(atual.prerequisitos):
                if requisito not in self._disciplinas:
                    raise ValueError(
                        f"Pre-requisito {requisito} de {codigo} nao existe na matriz"
                    )

                if estado.get(requisito, 0) == 1:
                    inicio = posicao_na_pilha[requisito]
                    return caminho[inicio:] + [requisito]

                if estado.get(requisito, 0) == 0:
                    ciclo = visitar(requisito)
                    if ciclo is not None:
                        return ciclo

            caminho.pop()
            del posicao_na_pilha[codigo]
            estado[codigo] = 2
            return None

        for codigo in sorted(self._disciplinas):
            if estado.get(codigo, 0) == 0:
                ciclo = visitar(codigo)
                if ciclo is not None:
                    return ciclo
        return None


@dataclass(frozen=True)
class Grade:
    disciplinas: tuple[DisciplinaOfertada, ...] = ()

    def incluir(self, ofertada: DisciplinaOfertada) -> Grade:
        return Grade(self.disciplinas + (ofertada,))

    def quantidade(self) -> int:
        return len(self.disciplinas)

    def carga_horaria(self) -> int:
        return sum(item.disciplina.ch for item in self.disciplinas)

    def sem_conflitos(self) -> bool:
        for indice, atual in enumerate(self.disciplinas):
            for outra in self.disciplinas[indice + 1:]:
                if atual.conflita_com(outra):
                    return False
        return True

    def codigos(self) -> list[str]:
        return sorted(item.disciplina.codigo for item in self.disciplinas)


class Restricao(ABC):
    """Contrato OO: todas as restricoes respondem a mesma mensagem."""

    @abstractmethod
    def permite(self, grade: Grade) -> bool:
        pass


class TetoDeCargaHoraria(Restricao):
    def __init__(self, teto: int):
        self._teto = teto

    def permite(self, grade: Grade) -> bool:
        return grade.carga_horaria() <= self._teto


class ConflitoDeHorario(Restricao):
    def permite(self, grade: Grade) -> bool:
        return grade.sem_conflitos()


class BuscadorDeGrades:
    def __init__(self, restricoes: list[Restricao]):
        self._restricoes = tuple(restricoes)
        self._melhores: list[Grade] = []
        self._maior = -1

    def _permite(self, grade: Grade) -> bool:
        # Despacho dinamico REAL: a classe concreta decide qual permite() rodar.
        for restricao in self._restricoes:
            if not restricao.permite(grade):
                return False
        return True

    def encontrar(self, ofertas: list[DisciplinaOfertada]) -> list[list[str]]:
        """Backtracking: maximiza numero de disciplinas e preserva empates."""
        self._melhores = []
        self._maior = -1
        ordenadas = sorted(ofertas, key=lambda oferta: oferta.disciplina.codigo)
        self._explorar(ordenadas, 0, Grade())
        return sorted(grade.codigos() for grade in self._melhores)

    def _explorar(
        self, ofertas: list[DisciplinaOfertada], indice: int, grade: Grade
    ) -> None:
        restantes = len(ofertas) - indice
        # Nem escolhendo todas as restantes seria possivel superar/empatar.
        if grade.quantidade() + restantes < self._maior:
            return

        if indice == len(ofertas):
            quantidade = grade.quantidade()
            if quantidade > self._maior:
                self._maior = quantidade
                self._melhores = [grade]
            elif quantidade == self._maior:
                self._melhores.append(grade)
            return

        nova_grade = grade.incluir(ofertas[indice])
        if self._permite(nova_grade):
            self._explorar(ofertas, indice + 1, nova_grade)

        self._explorar(ofertas, indice + 1, grade)


class PlanejadorDeMatricula:
    """Coordena objetos; delega a eles as regras que conhecem."""

    def __init__(
        self, matriz: MatrizCurricular, aluno: Aluno, ofertas: list[DisciplinaOfertada]
    ):
        self._matriz = matriz
        self._aluno = aluno
        self._ofertas = ofertas

    def analisar(self) -> dict:
        ciclo = self._matriz.detectar_ciclo()
        if ciclo is not None:
            return {
                "ciclo": ciclo,
                "liberadas": None,
                "bloqueadas": None,
                "grades_maximas": None,
            }

        liberadas: list[DisciplinaOfertada] = []
        bloqueadas: list[dict] = []

        for oferta in self._ofertas:
            disciplina = oferta.disciplina
            if self._aluno.aprovou(disciplina.codigo):
                continue

            faltam = disciplina.prerequisitos_faltantes(self._aluno)
            if faltam:
                bloqueadas.append({"codigo": disciplina.codigo, "faltam": faltam})
            else:
                liberadas.append(oferta)

        restricoes: list[Restricao] = [
            TetoDeCargaHoraria(self._aluno.teto_ch),
            ConflitoDeHorario(),
        ]
        buscador = BuscadorDeGrades(restricoes)
        return {
            "ciclo": None,
            "liberadas": sorted(o.disciplina.codigo for o in liberadas),
            "bloqueadas": sorted(bloqueadas, key=lambda b: b["codigo"]),
            "grades_maximas": buscador.encontrar(liberadas),
        }
