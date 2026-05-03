import anthropic
import json
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path

BRT = timezone(timedelta(hours=-3))
hoje = datetime.now(BRT)

DIAS_PT = ['Segunda-feira','Terca-feira','Quarta-feira','Quinta-feira','Sexta-feira','Sabado','Domingo']
MESES_PT = ['Janeiro','Fevereiro','Marco','Abril','Maio','Junho','Julho','Agosto','Setembro','Outubro','Novembro','Dezembro']
MESES_CURTO = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez']

data_fmt = DIAS_PT[hoje.weekday()] + ', ' + str(hoje.day).zfill(2) + ' de ' + MESES_PT[hoje.month-1] + ' de ' + str(hoje.year)
data_curta = str(hoje.day).zfill(2) + ' ' + MESES_CURTO[hoje.month-1].upper() + ' ' + str(hoje.year)
data_iso = hoje.strftime('%Y-%m-%d')

print('Gerando ViaLog para: ' + data_fmt)

PROMPT = '''Voce e o ViaLog, curador de inteligencia ferroviaria da MRS Logistica.

Hoje e ''' + data_fmt + ''' (''' + data_iso + ''').

MISSAO: Buscar APENAS noticias REAIS publicadas hoje ou nos ultimos 2 dias. NAO invente nada.

Use a ferramenta web_search para buscar noticias reais nestas fontes:
- railwaygazette.com, railjournal.com, globalrailwayreview.com
- bnamericas.com, progressiverailroading.com, railway-technology.com
- reuters.com, mining.com, steelorbis.com, tradingeconomics.com
- agenciabrasil.ebc.com.br

Busque:
1. "railway news ''' + data_iso + '''"
2. "iron ore price today ''' + hoje.strftime('%B %Y') + '''"
3. "AI artificial intelligence railway 2026"
4. "ferrovia brasil 2026"
5. "China railway news ''' + data_iso + '''"

REGRAS:
- Cada noticia DEVE ter URL real da fonte
- Se nao encontrar noticia real, omita
- Secao IA na Ferrovia e obrigatoria
- Cotacoes: use valores reais encontrados via busca

Retorne APENAS JSON valido sem markdown sem aspas curvas sem caracteres especiais:
{
  "edicao": "''' + hoje.strftime('%j') + '''",
  "data_curta": "''' + data_curta + '''",
  "destaque": "manchete real do maior fato encontrado",
  "ticker": [
    {"label": "indicador", "valor": "valor real", "variacao": "variacao real", "direcao": "up"}
  ],
  "minerio": {
    "preco": "cotacao real USD/t",
    "variacao12m": "variacao real",
    "importacao_china": "dado real recente",
    "alerta": "alerta baseado em noticia real",
    "fonte_url": "url real da cotacao"
  },
  "brasil": [
    {
      "categoria": "emoji + categoria",
      "titulo": "titulo real da noticia",
      "corpo": "resumo fiel 2-3 frases",
      "tag": "tag curta",
      "fonte_nome": "nome da publicacao",
      "fonte_url": "url real da noticia"
    }
  ],
  "china": [
    {
      "categoria": "emoji + categoria",
      "titulo": "titulo real",
      "corpo": "resumo fiel 2-3 frases",
      "tag": "tag curta",
      "fonte_nome": "nome da publicacao",
      "fonte_url": "url real"
    }
  ],
  "mundo": [
    {
      "categoria": "emoji + categoria",
      "titulo": "titulo real",
      "corpo": "resumo fiel 2-3 frases",
      "tag": "tag curta",
      "fonte_nome": "nome da publicacao",
      "fonte_url": "url real"
    }
  ],
  "ia_ferrovia": [
    {
      "titulo": "titulo real sobre IA em ferrovias",
      "corpo": "resumo fiel 2-3 frases",
      "impacto_mrs": "impacto para Via Permanente MRS",
      "fonte_nome": "nome da publicacao",
      "fonte_url": "url real"
    }
  ],
  "radar_mrs": "analise baseada nas noticias encontradas",
  "tendencias": "tendencias observadas nas noticias reais do dia"
}'''

client = anthropic.Anthropic()

print('Buscando noticias reais na web...')
response = client.messages.create(
    model='claude-sonnet-4-6',
    max_tokens=8000,
    tools=[{'type': 'web_search_20250305', 'name': 'web_search'}],
    messages=[{'role': 'user', 'content': PROMPT}]
)

raw = ''
for block in response.content:
    if hasattr(block, 'text'):
        raw += block.text

raw = re.sub(r'```json\s*', '', raw)
raw = re.sub(r'```\s*', '', raw)
raw = raw.strip()

json_match = re.search(r'\{.*\}', raw, re.DOTALL)
if json_match:
    raw = json_match.group(0)

data = json.loads(raw)
print('Noticias encontradas: ' + data.get('destaque','')[:60])

def esc(s):
    return str(s).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;')

def dir_class(d):
    return {'up':'ti-up','down':'ti-down','flat':'ti-flat'}.get(d,'ti-flat')

def render_ticker(items):
    html = ''
    for t in items:
        html += '<span class="ti"><span class="ti-dot">&#9679;</span><span class="ti-label">' + esc(t['label']) + '</span><span class="ti-val">' + esc(t['valor']) + '</span><span class="' + dir_class(t['direcao']) + '">' + esc(t['variacao']) + '</span></span>'
    return html * 2

def render_item(n, cat_css, tag_css):
    url = n.get('fonte_url','')
    fonte = n.get('fonte_nome','Fonte')
    titulo = esc(n.get('titulo',''))
    corpo = esc(n.get('corpo',''))
    cat = esc(n.get('categoria',''))
    lo = '<a href="' + url + '" target="_blank" rel="noopener" style="text-decoration:none;color:inherit">' if url else ''
    lc = '</a>' if url else ''
    badge = '<a href="' + url + '" target="_blank" rel="noopener" style="display:inline-flex;align-items:center;gap:4px;margin-top:6px;font-size:9px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;padding:3px 9px;border-radius:3px;text-decoration:none;' + tag_css + '">&#128206; ' + esc(fonte) + ' &#8599;</a>' if url else ''
    return '<div class="ni"><div class="ni-meta"><div class="ni-dot"></div><div class="ni-cat" style="' + cat_css + '">' + cat + '</div></div>' + lo + '<div class="ni-title">' + titulo + ('&nbsp;&#8599;' if url else '') + '</div>' + lc + '<div class="ni-body">' + corpo + '</div>' + badge + '</div>'

def render_col(region, items):
    cfg = {
        'brasil': ('br','var(--up)','&#127463;&#127479;','Brasil','background:rgba(0,156,59,.1);color:var(--up)','color:var(--up)'),
        'china':  ('cn','var(--down)','&#127464;&#127475;','China','background:rgba(222,41,16,.1);color:var(--down)','color:var(--down)'),
        'mundo':  ('wo','#6dd6da','&#127757;','Mundo','background:rgba(0,153,168,.1);color:#6dd6da','color:#6dd6da')
    }
    cc,color,flag,title,tag_css,cat_css = cfg.get(region,cfg['mundo'])
    nis = ''.join(render_item(n,cat_css,tag_css) for n in items)
    return '<div class="col-card col-' + cc + '"><div class="col-head"><div class="col-flag">' + flag + '</div><div class="col-title" style="color:' + color + '">' + title + '</div></div><div class="col-body">' + nis + '</div></div>'

def render_ia(items):
    if not items:
        return ''
    cards = ''
    for n in items:
        url = n.get('fonte_url','')
        fonte = n.get('fonte_nome','Fonte')
        impacto = esc(n.get('impacto_mrs',''))
        lo = '<a href="' + url + '" target="_blank" rel="noopener" style="text-decoration:none;color:inherit">' if url else ''
        lc = '</a>' if url else ''
        badge = '<a href="' + url + '" target="_blank" rel="noopener" style="display:inline-flex;align-items:center;gap:4px;margin-top:8px;font-size:9px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;padding:3px 9px;border-radius:3px;background:rgba(139,92,246,.15);color:#a78bfa;text-decoration:none">&#128206; ' + esc(fonte) + ' &#8599;</a>' if url else ''
        imp_block = '<div style="margin-top:6px;padding:6px 10px;background:rgba(232,93,4,.07);border-left:3px solid var(--orange);border-radius:3px;font-size:11px;color:var(--amber)">&#128642; MRS: ' + impacto + '</div>' if impacto else ''
        cards += '<div class="ni"><div class="ni-meta"><div class="ni-dot" style="background:#8b5cf6"></div><div class="ni-cat" style="color:#a78bfa">&#129302; IA na Ferrovia</div></div>' + lo + '<div class="ni-title">' + esc(n.get('titulo','')) + ('&nbsp;&#8599;' if url else '') + '</div>' + lc + '<div class="ni-body">' + esc(n.get('corpo','')) + '</div>' + imp_block + badge + '</div>'
    return '<div class="region-panel" id="rpanel-ia"><div class="region-cols"><div class="col-card" style="border-top:4px solid #8b5cf6;background:var(--surface);border:1px solid var(--border);border-radius:8px;overflow:hidden"><div class="col-head" style="padding:13px 18px 11px;border-bottom:1px solid var(--border);display:flex;align-items:center;gap:10px"><div class="col-flag">&#129302;</div><div class="col-title" style="font-family:Bebas Neue,sans-serif;font-size:22px;letter-spacing:.07em;color:#a78bfa">IA na Ferrovia</div></div><div class="col-body" style="padding:14px 16px">' + cards + '</div></div></div></div>'

m = data.get('minerio',{})
minerio_url = m.get('fonte_url','')
fonte_link = '<a href="' + minerio_url + '" target="_blank" style="font-size:9px;color:var(--amber);text-decoration:none">Ver fonte &#8599;</a>' if minerio_url else ''
mineral_bar_html = '<div class="mi"><div class="mi-label">Minerio Fe 62% CFR</div><div class="mi-val">' + esc(m.get('preco','--')) + '</div><div class="mi-chg up">&#9650; ' + esc(m.get('variacao12m','')) + ' em 12 meses</div></div><div class="mi"><div class="mi-label">Importacao China</div><div class="mi-val">' + esc(m.get('importacao_china','--')) + '</div><div class="mi-chg up">&#9650; dado recente</div></div><div class="mi"><div class="mi-label">Alerta do Dia</div><div class="mi-val" style="font-size:12px;color:var(--amber);padding-top:3px">' + esc(m.get('alerta','--')) + '</div>' + fonte_link + '</div>'

ticker_html = render_ticker(data.get('ticker',[]))
lead_html = esc(data.get('destaque',''))
brasil_col = render_col('brasil', data.get('brasil',[]))
china_col  = render_col('china',  data.get('china',[]))
mundo_col  = render_col('mundo',  data.get('mundo',[]))
ia_section = render_ia(data.get('ia_ferrovia',[]))
radar_mrs  = esc(data.get('radar_mrs',''))
tendencias = esc(data.get('tendencias',''))
analise_min = esc(m.get('analise', data.get('radar_mrs','')))

html_path = Path('index.html')
html = html_path.read_text(encoding='utf-8')

replacements = {
    r'<!-- TICKER_START -->.*?<!-- TICKER_END -->':           '<!-- TICKER_START -->' + ticker_html + '<!-- TICKER_END -->',
    r'<!-- LEAD_START -->.*?<!-- LEAD_END -->':               '<!-- LEAD_START -->' + lead_html + '<!-- LEAD_END -->',
    r'<!-- MINERAL_BAR_START -->.*?<!-- MINERAL_BAR_END -->': '<!-- MINERAL_BAR_START -->' + mineral_bar_html + '<!-- MINERAL_BAR_END -->',
    r'<!-- BR_COL_START -->.*?<!-- BR_COL_END -->':           '<!-- BR_COL_START -->' + brasil_col + '<!-- BR_COL_END -->',
    r'<!-- CN_COL_START -->.*?<!-- CN_COL_END -->':           '<!-- CN_COL_START -->' + china_col + '<!-- CN_COL_END -->',
    r'<!-- WORLD_COL_START -->.*?<!-- WORLD_COL_END -->':     '<!-- WORLD_COL_START -->' + mundo_col + '<!-- WORLD_COL_END -->',
    r'<!-- IA_SECTION_START -->.*?<!-- IA_SECTION_END -->':   '<!-- IA_SECTION_START -->' + ia_section + '<!-- IA_SECTION_END -->',
    r'<!-- RADAR_MRS_START -->.*?<!-- RADAR_MRS_END -->':     '<!-- RADAR_MRS_START -->' + radar_mrs + '<!-- RADAR_MRS_END -->',
    r'<!-- TENDENCIAS_START -->.*?<!-- TENDENCIAS_END -->':    '<!-- TENDENCIAS_START -->' + tendencias + '<!-- TENDENCIAS_END -->',
    r'<!-- MINERIO_ANALISE_START -->.*?<!-- MINERIO_ANALISE_END -->': '<!-- MINERIO_ANALISE_START -->' + analise_min + '<!-- MINERIO_ANALISE_END -->',
    r'<!-- HERO_DATE_START -->.*?<!-- HERO_DATE_END -->':      '<!-- HERO_DATE_START -->' + data_curta + '<!-- HERO_DATE_END -->',
    r'<!-- EDICAO_NUM_START -->.*?<!-- EDICAO_NUM_END -->':    '<!-- EDICAO_NUM_START -->No ' + data.get('edicao','--') + ' - Compilado as 06h00<!-- EDICAO_NUM_END -->',
}

for pattern, replacement in replacements.items():
    html = re.sub(pattern, replacement, html, flags=re.DOTALL)

html_path.write_text(html, encoding='utf-8')
print('ViaLog publicado com noticias reais para ' + data_fmt)
