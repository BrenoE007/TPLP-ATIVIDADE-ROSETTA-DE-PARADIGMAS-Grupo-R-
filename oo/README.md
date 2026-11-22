# T2 – Versão Orientada a Objetos (Python)

Implementação independente seguindo o contrato JSON do professor, testada contra `saidas_esperadas.json`.
Python 3.10+; nenhuma dependência de terceiros.

## Executar (a partir da raiz do projeto)

```bash
python oo/main.py
python oo/main.py --matriz dados/caso2_ciclo.json
python oo/main.py --historico dados/caso3_historico_vazio.json
python oo/main.py --historico dados/caso4_historico_completo.json
python oo/main.py --historico dados/caso5_teto_reduzido.json
```

Use `--oferta dados/oferta.json` para informar outra oferta. A saída padrão contém **apenas um JSON**.

## Testar

```bash
python oo/testes.py
```

## Organização

- `main.py`: entrada, leitura dos JSONs, montagem do modelo e serialização da saída. Não contém regras de negócio.
- `dominio.py`: entidades do domínio (`Aluno`, `Disciplina`, `Horario`, `DisciplinaOfertada`, `MatrizCurricular`, `Grade`), o contrato polimórfico `Restricao`, duas implementações e o serviço de busca `BuscadorDeGrades`, além de `PlanejadorDeMatricula`, que apenas coordena objetos.
- `testes.py`: valida os cinco casos por comparação de objetos JSON.

## Conceitos de POO que aparecem no código

1. **Encapsulamento de comportamento:** `Disciplina.prerequisitos_faltantes(aluno)`, `Aluno.aprovou(codigo)`, `DisciplinaOfertada.conflita_com(outra)`, `Grade.carga_horaria()` e `Grade.sem_conflitos()`.
2. **Abstração:** `Restricao` declara `permite(grade)` sem determinar como cada regra funciona.
3. **Herança e polimorfismo:** `TetoDeCargaHoraria` e `ConflitoDeHorario` implementam `Restricao`; `BuscadorDeGrades._permite()` chama `restricao.permite(grade)` sem testar a classe concreta.
4. **Composição:** uma `Grade` é formada por várias `DisciplinaOfertada`, que por sua vez combina uma `Disciplina` com `Horario`.
5. **Separação de responsabilidades:** a matriz detecta ciclos, a disciplina decide pré-requisitos, a grade sabe avaliar sua própria composição e o buscador escolhe as combinações.

Observação: as `dataclasses` são usadas como conveniência de construção, igualdade e imutabilidade; as entidades possuem métodos de negócio e não são apenas recipientes de dados.

Este pacote inclui cópias **não modificadas** dos JSONs de entrada e do gabarito apenas para permitir executar o projeto de forma independente. Ao integrar ao repositório da equipe, copie somente a pasta `oo/` para a raiz existente.
