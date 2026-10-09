# Adaptar os dados para filtros e cálculos

Não é necessário baixar novamente os arquivos para trabalhar com o conjunto publicado. Use os JSONs decodificados das pastas de zona, sem os arquivos com sufixo `_aux.json`.

## Campos

```text
resultadosVotacaoPorEleicao[]
  idEleicao
  resultadosVotacao[]
    totaisVotosCargo[]
      codigoCargo = [tipo, nome do cargo]
      votosVotaveis[]
        tipoVoto
        quantidadeVotos
        identificacaoVotavel.codigo
```

`nominal` identifica votos do candidato. Brancos, nulos e legenda precisam de tratamento separado. O número de candidato deve ser interpretado junto com cargo e eleição.

## Exemplo: candidatos com pelo menos mil votos na cidade

Execute o exemplo dentro da pasta que contém `BUs_Petrolina_2026/`:

```python
import json
from pathlib import Path
from collections import defaultdict

totais = defaultdict(int)
for arquivo in Path('BUs_Petrolina_2026').glob('zona_*/BU_*.json'):
    if arquivo.name.endswith('_aux.json'):
        continue
    bu = json.loads(arquivo.read_text(encoding='utf-8'))
    for eleicao in bu['resultadosVotacaoPorEleicao']:
        for resultado in eleicao['resultadosVotacao']:
            for cargo in resultado['totaisVotosCargo']:
                for voto in cargo['votosVotaveis']:
                    if voto['tipoVoto'] == 'nominal':
                        chave = (
                            eleicao['idEleicao'],
                            cargo['codigoCargo'][1],
                            voto['identificacaoVotavel']['codigo'],
                        )
                        totais[chave] += voto['quantidadeVotos']

for chave, total in sorted(totais.items()):
    if total >= 1000:
        print(chave, total)
```

Para exatamente X votos, use `total == X`. Para uma faixa, use `minimo <= total <= maximo`. Para uma fórmula própria, aplique-a depois da agregação, usando as unidades e os denominadores corretos.

Este exemplo considera a estrutura do pacote, que contém um JSON por seção principal. Não replique arquivos para as agregadas antes de somar. Confira a cobertura em `resumo.json` e compare os totais municipais com os resultados oficiais antes de publicar uma análise.

Votos registrados no BU e votos considerados válidos na totalização podem exigir interpretações diferentes por causa da destinação de votos ou da situação dos candidatos. O exemplo soma os registros nominais do BU; ele não calcula quociente eleitoral, vagas ou classificação oficial.
