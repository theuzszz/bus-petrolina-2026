# Coleta de Petrolina — primeiro turno de 2026

Primeira publicação do projeto, com código, documentação e os arquivos prontos para uso.

## Pacotes

- **BUs_Petrolina_2026.zip**: 730 PDFs legíveis, 730 BUs originais `.dat`, JSONs decodificados, metadados e índices.
- **BUs_Originais_Petrolina_2026.zip**: somente os originais, em pastas de zona e seção.
- **Script_BUs_Petrolina.zip**: script de download, verificador local, especificação ASN.1 oficial do TSE, dependências e documentação.
- **SHA256SUMS.txt**: resumos SHA-256 dos originais da coleta, com caminhos relativos ao pacote completo.

## Cobertura

| Zona | BUs originais | Agregadas |
| --- | ---: | ---: |
| 0083 | 239 | 3 |
| 0144 | 243 | 2 |
| 0145 | 248 | 4 |

730 BUs correspondem aos 739 registros de seção da configuração oficial, considerando as 9 agregadas. Coleta de 05/10/2026; sem pendências.

## Conferências

Identificação e somas dos votos conferidas a partir dos originais. As 239 seções principais da zona 0083 também foram comparadas com 257 downloads anteriores do portal: todos os arquivos correspondentes são idênticos por SHA-256. Os ZIPs foram verificados.

## Antes de usar

Extraia o pacote completo e abra `indice.html`. Os PDFs são conversões, com leiaute próprio, e não reproduções do impresso da urna. Alguns candidatos aparecem apenas pelo número porque seus nomes não foram encontrados na lista consultada. A assinatura criptográfica não foi validada. O código tem escopo específico para Petrolina e esta eleição.

Consulte o README para instalar, executar ou adaptar para análises.
