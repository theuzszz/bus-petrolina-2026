"""Conferência local de cobertura, identificação e somas; não valida assinaturas."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import asn1tools


def validate(root):
    decoder = asn1tools.compile_files(str(Path(__file__).with_name('bu.asn1')), codec='ber')
    with (root / 'indice.csv').open(encoding='utf-8-sig', newline='') as stream:
        rows = list(csv.DictReader(stream))
    seen = set()
    hashes = []
    principal = agregadas = 0
    for row in rows:
        key = (row['zona'], row['secao'])
        if key in seen:
            raise ValueError(f'Seção duplicada: {key}')
        seen.add(key)
        if row['situacao'] not in ('convertido', 'agregada'):
            raise ValueError(f'Seção pendente: {key}: {row["situacao"]}')
        if not (root / row['pdf']).is_file():
            raise ValueError(f'PDF ausente: {key}')
        if row['situacao'] == 'agregada':
            agregadas += 1
            continue
        z, s = key
        rawpath = root / f'zona_{z}' / f'o03220pe25216{z}{s}-bu.dat'
        raw = rawpath.read_bytes()
        envelope = decoder.decode('EntidadeEnvelopeGenerico', raw)
        bu = decoder.decode('EntidadeBoletimUrna', envelope['conteudo'])
        identification = bu['identificacaoSecao']
        if (bu['fase'] != 'oficial' or bu['cabecalho']['idEleitoral'][1] != 3220
                or identification['municipioZona'] != {'municipio': 25216, 'zona': int(z)}
                or identification['secao'] != int(s)):
            raise ValueError(f'Identificação divergente: {key}')
        for election in bu['resultadosVotacaoPorEleicao']:
            for result in election['resultadosVotacao']:
                for office in result['totaisVotosCargo']:
                    name = office['codigoCargo'][1]
                    total = sum(v['quantidadeVotos'] for v in office['votosVotaveis'])
                    expected = result['qtdComparecimento'] * (2 if name == 'senador' else 1)
                    if total != expected:
                        raise ValueError(f'Soma divergente: {key} {name}: {total} != {expected}')
        principal += 1
        hashes.append(f'{hashlib.sha256(raw).hexdigest()}  {rawpath.relative_to(root).as_posix()}')
    for row in rows:
        if row['situacao'] == 'agregada':
            main = next((r for r in rows if r['zona'] == row['zona']
                         and r['secao'] == row['principal']), None)
            if not main or main['situacao'] != 'convertido' or row['pdf'] != main['pdf']:
                raise ValueError(f'Vínculo inválido: {row}')
    (root / 'SHA256SUMS.txt').write_text('\n'.join(hashes) + '\n', encoding='utf-8')
    print(json.dumps({'registros': len(rows), 'bus_conferidos': principal,
                      'agregadas': agregadas, 'resultado': 'ok'}, ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pasta', type=Path, help='Pasta BUs_Petrolina_2026 extraída')
    validate(parser.parse_args().pasta)
