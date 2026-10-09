"""Baixa e converte os BUs oficiais de Petrolina, primeiro turno de 2026.
Requer Python, asn1tools e reportlab. Execute: python baixar_bus.py
"""
import concurrent.futures, csv, hashlib, html, json, time, urllib.request, zipfile
from pathlib import Path
import asn1tools
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4

ROOT=Path(__file__).resolve().parent
DEST=ROOT/'BUs_Petrolina_2026'
BASE='https://resultados.tse.jus.br/oficial'
styles=getSampleStyleSheet()

def get(url):
    for attempt in range(3):
        try:
            with urllib.request.urlopen(url,timeout=45) as r: return r.read()
        except Exception:
            if attempt==2: raise
            time.sleep(2*(attempt+1))

def js(url): return json.loads(get(url))
def write_json(path,obj):
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2,default=lambda b:b.hex() if isinstance(b,bytes) else str(b)),encoding='utf8')
def p(s,style='Normal'): return Paragraph(html.escape(str(s)),styles[style])

def pdf(path,b,names,source,sha):
    ident=b['identificacaoSecao']; mz=ident['municipioZona']
    story=[p('Boletim de Urna - Petrolina / PE','Title'),p(f"1º turno de 2026 | Zona {mz['zona']:04d} | Seção {ident['secao']:04d}",'Heading2'),p('Versão legível gerada a partir do arquivo original do TSE. Não reproduz a diagramação do impresso da urna.'),Spacer(1,10)]
    def dt(value):
        return f'{value[6:8]}/{value[4:6]}/{value[:4]} {value[9:11]}:{value[11:13]}:{value[13:15]}' if isinstance(value,str) and len(value)==15 else str(value)
    story += [p(f"Local de votação: {ident['local']} | Urna: {b['urna']['correspondenciaResultado']['carga']['numeroInternoUrna']}"),p(f"Emissão: {dt(b['dataHoraEmissao'])} | Comparecimento: {b['qtdEleitoresCompareceram']}")]
    dados=b.get('dadosSecaoSA',('',{}))[1]
    story += [p(f"Abertura: {dt(dados.get('dataHoraAbertura',''))} | Encerramento: {dt(dados.get('dataHoraEncerramento',''))}")]
    biom=b.get('detalhamentoComparecimento',{})
    story += [p(f"Biometria: {biom.get('qtdEleitoresHabilitadosPorBiometria','')} | Biografia: {biom.get('qtdEleitoresHabilitadosPorBiografia','')} | Sem biometria: {biom.get('qtdEleitoresCompareceramSemBiometria','')}")]
    story += [p('Código da carga: '+b['urna']['correspondenciaResultado']['carga']['codigoCarga'])]
    for e in b['resultadosVotacaoPorEleicao']:
        story += [p(f"Eleição {e['idEleicao']} | Aptos: {e['qtdEleitoresAptos']}",'Heading2'),p(f"Aptos originais: {e.get('qtdEleitoresAptosSecao','')} | Temporários: {e.get('qtdEleitoresAptosTTE','')} | Faltosos: {e['qtdEleitoresAptos']-b['qtdEleitoresCompareceram']}")]
        for result in e['resultadosVotacao']:
            for cargo in sorted(result['totaisVotosCargo'],key=lambda x:x['ordemImpressao']):
                name=cargo['codigoCargo'][1]
                story.append(p(str(name).replace('deputado','Deputado ').title(),'Heading2'))
                rows=[[p('Número / tipo'),p('Candidato / descrição'),p('Votos')]]
                total=0
                for v in cargo['votosVotaveis']:
                    identv=v.get('identificacaoVotavel',{})
                    code=identv.get('codigo','')
                    typ=v['tipoVoto']; count=v['quantidadeVotos']; total+=count
                    label=names.get((name,str(code)),str(code)) if typ=='nominal' else {'branco':'Brancos','nulo':'Nulos','legenda':'Votos de legenda'}.get(typ,typ)
                    rows.append([p(code or typ),p(label),p(count)])
                rows.append([p('TOTAL'),p('Total apurado'),p(total)])
                table=Table(rows,colWidths=[95,330,65],repeatRows=1,hAlign='LEFT')
                table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e5edf4')),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,0),.5,colors.grey),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
                story += [table,Spacer(1,8)]
    story += [p('Origem e integridade','Heading2'),p(source),p('SHA-256 do arquivo original: '+sha),p('A assinatura criptográfica do BU não foi validada por esta conversão.')]
    def footer(c,d):
        c.setFont('Helvetica',8);c.drawString(40,25,f"Petrolina - Zona {mz['zona']:04d} - Seção {ident['secao']:04d}");c.drawRightString(555,25,str(d.page))
    SimpleDocTemplate(str(path),pagesize=A4,rightMargin=40,leftMargin=40,topMargin=35,bottomMargin=40).build(story,onFirstPage=footer,onLaterPages=footer)

def main():
    DEST.mkdir(exist_ok=True)
    config=js(BASE+'/comum/config/ele-c.json')
    pleito=next(x for x in config['pl'] if x['dt']=='04/10/2026' and x['c']=='ele2026')
    assert config['f']=='o'
    cd=pleito['cd']; prefix=f'p{int(cd):06d}'
    urnabase=f'{BASE}/{pleito["c"]}/arquivo-urna/{cd}'
    sections=js(f'{urnabase}/config/pe/pe-{prefix}-cs.json')
    assert sections['f']=='o'
    write_json(DEST/'configuracao_secoes.json',sections)
    city=next(m for a in sections['abr'] if a['cd']=='pe' for m in a['mu'] if m['cd']=='25216')
    names={}; cargos={1:'presidente',3:'governador',5:'senador',6:'deputadoFederal',7:'deputadoEstadual'}
    for code,label in cargos.items():
        election=6257 if code==1 else 6259
        result=js(f'{BASE}/ele2026/{election}/dados/pe/pe25216-c{code:04d}-e{election:06d}-u.json')
        for cargo in result['carg']:
            for agr in cargo.get('agr',[]):
                for party in agr.get('par',[]):
                    for cand in party.get('cand',[]): names[(label,cand['n'])]=cand.get('nmu',cand['nm'])
    decoder=asn1tools.compile_files(str(ROOT/'bu.asn1'),codec='ber')
    jobs=[]; rows=[]
    for zone in city['zon']:
        assert zone['cd'] in ('0083','0144','0145')
        for sec in zone['sec']:
            if sec.get('nsp'):
                rows.append({'zona':zone['cd'],'secao':sec['ns'],'situacao':'agregada','principal':sec['nsp'],'pdf':f"zona_{zone['cd']}/BU_{zone['cd']}_{sec['nsp']}.pdf"})
            else: jobs.append((zone['cd'],sec['ns']))
    def process(job):
        z,s=job; folder=DEST/f'zona_{z}'; folder.mkdir(exist_ok=True)
        stem=f'BU_{z}_{s}'; local=f'{urnabase}/dados/pe/25216/{z}/{s}'
        try:
            aux=js(f'{local}/{prefix}-pe-m25216-z{z}-s{s}-aux.json'); assert aux['f']=='o'
            write_json(folder/(stem+'_aux.json'),aux)
            selected=[h for h in aux['hashes'] if h['st'].lower()=='totalizado']
            if not selected: return dict(zona=z,secao=s,situacao=aux['st'],principal=s,pdf='')
            h=selected[-1]; file=next(a['nm'] for a in h['arq'] if a['tp']=='bu')
            url=f'{local}/{h["hash"]}/{file}'
            rawpath=folder/file
            raw=rawpath.read_bytes() if rawpath.exists() else get(url)
            env=decoder.decode('EntidadeEnvelopeGenerico',raw); b=decoder.decode('EntidadeBoletimUrna',env['conteudo'])
            assert b['fase']=='oficial' and b['cabecalho']['idEleitoral'][1]==int(cd)
            i=b['identificacaoSecao']; assert i['municipioZona']=={'municipio':25216,'zona':int(z)} and i['secao']==int(s)
            rawpath.write_bytes(raw); write_json(folder/(stem+'.json'),b)
            pdf(folder/(stem+'.pdf'),b,names,url,hashlib.sha256(raw).hexdigest())
            return dict(zona=z,secao=s,situacao='convertido',principal=s,pdf=f'zona_{z}/{stem}.pdf')
        except Exception as exc: return dict(zona=z,secao=s,situacao='ERRO: '+str(exc),principal=s,pdf='')
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        for n,row in enumerate(pool.map(process,jobs),1):
            rows.append(row)
            if n%25==0: print(f'{n}/{len(jobs)} processados',flush=True)
    rows.sort(key=lambda r:(r['zona'],r['secao']))
    with (DEST/'indice.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['zona','secao','situacao','principal','pdf']);w.writeheader();w.writerows(rows)
    links=''.join(f'<tr><td>{r["zona"]}</td><td>{r["secao"]}</td><td>{html.escape(r["situacao"])}</td><td>{r["principal"]}</td><td><a href="{r["pdf"]}">Abrir PDF</a></td></tr>' for r in rows if r['pdf'])
    (DEST/'indice.html').write_text('<meta charset="utf-8"><title>BUs Petrolina 2026</title><h1>BUs de Petrolina - 1º turno 2026</h1><p>Seções agregadas compartilham o BU da seção principal. PDFs convertidos dos originais do TSE.</p><table border="1" cellpadding="6"><tr><th>Zona</th><th>Seção</th><th>Situação</th><th>Principal</th><th>PDF</th></tr>'+links+'</table>',encoding='utf8')
    summary={'registros':len(rows),'pdfs':sum(r['situacao']=='convertido' for r in rows),'agregadas':sum(r['situacao']=='agregada' for r in rows),'pendencias':[r for r in rows if r['situacao'] not in ('agregada','convertido')]}
    write_json(DEST/'resumo.json',summary)
    with zipfile.ZipFile(ROOT/'BUs_Petrolina_2026.zip','w',zipfile.ZIP_DEFLATED) as out:
        for file in DEST.rglob('*'):
            if file.is_file():out.write(file,file.relative_to(ROOT))
    print(json.dumps(summary,ensure_ascii=False),flush=True)

if __name__=='__main__': main()
