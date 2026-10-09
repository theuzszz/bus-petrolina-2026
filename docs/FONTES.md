# Fontes e atribuições

## Tribunal Superior Eleitoral

- [Documentação técnica da divulgação de resultados de 2026](https://www.tse.jus.br/eleicoes/informacoes-tecnicas-sobre-a-divulgacao-de-resultados): procedimento de consumo dos arquivos e referências EA11, EA16 e EA18.
- [Página das Eleições 2026](https://www.tse.jus.br/eleicoes/eleicoes-2026): seção “Urna eletrônica”, link “Formato dos arquivos de BU, RDV e assinatura digital”.
- [Pacote oficial de formatos](https://www.tse.jus.br/eleicoes/eleicoes-2026-content/arquivos/formato-arquivos-de-bu-rdv-e-assinatura-digital): origem do arquivo `spec/bu.asn1`, incluído no repositório como `bu.asn1`.
- [Portal Resultados](https://resultados.tse.jus.br/oficial/app/index.html): consulta visual dos mesmos boletins.

Servidor de download: `https://resultados.tse.jus.br/oficial`.

Identificadores usados nesta coleta: ciclo `ele2026`, pleito `3220`, eleição federal `6257`, eleição estadual `6259`, UF `pe`, município `25216`.

`bu.asn1` é a especificação do TSE distribuída para leitura dos arquivos e foi preservada sem alterações. A licença MIT do código próprio não se aplica a esse arquivo ou aos dados eleitorais.

## Bibliotecas

- [asn1tools](https://github.com/eerimoq/asn1tools): decodificação ASN.1/BER.
- [ReportLab](https://www.reportlab.com/): criação dos PDFs.

## Procedência da coleta publicada

Downloads e conversão realizados em 05/10/2026. Nenhuma chave, credencial, caminho pessoal ou log de outras tarefas faz parte do pacote publicado. O PDF é uma apresentação derivada, identificada como tal, e o original `.dat` é preservado.
