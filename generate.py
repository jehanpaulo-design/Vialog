"""
ViaLog — Gerador Automático de Newsletter Ferroviária
Roda via GitHub Actions todo dia útil às 06h00 (Brasília)
Usa a API do Claude para gerar conteúdo atualizado e injeta no index.html
"""

import anthropic
import json
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Fuso horário de Brasília
BRT = timezone(timedelta(hours=-3))
hoje = datetime.now(BRT)

DIAS_PT = ['Segunda-feira','Terça-feira','Quarta-feira','Quinta-feira','Sexta-feira','Sábado','Domingo']
MESES_PT = ['Janeiro','Fevereiro','Março','Abril','Maio','Junho','Julho','Agosto','Setembro','Outubro','Novembro','Dezembro']
MESES_CURTO = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez']

data_fmt   = f"{DIAS_PT[hoje.weekday()]}, {hoje.day:02d} de {MESES_PT[hoje.month-1]} de {hoje.year}"
data_curta = f"{hoje.day:02d} {MESES_CURTO[hoje.month-1].upper()} {hoje.year}"
data_arq   = f"Nº {hoje.strftime('%j')} · {DIAS_PT[hoje.weekday()][:3]}, {hoje.day:02d} {MESES_CURTO[hoje.month-1]} {hoje.year}"

print(f"📅 Gerando ViaLog para: {data_fmt}")

# ── PROMPT PARA O CLAUDE ──
PROMPT = f"""Você é o ViaLog, sistema de inteligência ferroviária da equipe de Estratégia de Engenharia e Manutenção de Via Permanente da MRS Logística, uma ferrovia de carga pesada brasileira.

Gere o informe ferroviário diário completo em português brasileiro para hoje, {data_fmt}.

Contexto MRS Logística: ferrovia de carga pesada no eixo Rio–São Paulo–Minas Gerais. Clientes âncora: Vale (minério de ferro), CSN Mineração, siderurgia e agronegócio. Carga axial 32,5t, trens de ~18.000t. A equipe de Via Permanente é responsável por estratégia de manutenção, renovação de dormentes (madeira → concreto), trilhos, AMVs, soldas, geometria de via, controle de fratura de trilho e GIV.

FORMATO — retorne APENAS JSON válido, sem markdown ou texto extra:
{{
  "edicao": "número sequencial como string (ex: 003)",
  "data_curta": "{data_curta}",
  "data_completa": "{data_fmt}",
  "destaque": "Uma frase impactante resumindo o maior fato do dia no setor ferroviário e de minério",
  "ticker": [
    {{"label": "nome do indicador", "valor": "valor formatado", "variacao": "+X% ou -X% ou texto", "direcao": "up|down|flat"}}
  ],
  "minerio": {{
    "preco": "valor atual em USD/t (ex: US$ 107,05/t)",
    "variacao12m": "+X,XX%",
    "importacao_china": "volume em Mt com variação a/a",
    "alerta": "principal risco ou oportunidade do dia",
    "analise": "2-3 frases de análise estratégica do mercado de minério com impacto MRS"
  }},
  "brasil": [
    {{
      "categoria": "emoji + nome (ex: ⛏️ Minério | 🏗️ Concessões | ⚡ Tecnologia | 🏭 Material Rodante | ⚠️ Gargalo | 👷 Mão de Obra | 🔭 Futuro)",
      "titulo": "manchete direta e informativa",
      "corpo": "2-3 frases com contexto, dados e implicações",
      "tag": "categoria curta para badge"
    }}
  ],
  "china": [
    {{
      "categoria": "emoji + nome",
      "titulo": "manchete",
      "corpo": "2-3 frases",
      "tag": "tag curta"
    }}
  ],
  "mundo": [
    {{
      "categoria": "emoji + nome",
      "titulo": "manchete",
      "corpo": "2-3 frases",
      "tag": "tag curta"
    }}
  ],
  "radar_mrs": "2-3 frases sobre impacto direto das notícias do dia para a MRS e equipe de Via Permanente",
  "tendencias": "2-3 frases sobre tendências globais relevantes (IHHA, descarbonização, automação, digital twin)",
  "analise_minerio_extra": "2-3 frases adicionais de análise estratégica de minério para o painel dedicado"
}}

REGRAS:
- Gere 4-5 notícias por região (brasil, china, mundo)
- Para ticker: inclua minério Fe 62%, USD/BRL, Baltic Dry Index, e 2-3 outros indicadores relevantes do dia
- Conteúdo baseado em fatos reais do setor ferroviário e de minério — use conhecimento atualizado
- Tom estratégico e técnico, voltado para engenheiros e gestores de via permanente
- Inclua dados numéricos específicos sempre que possível
- Radar MRS deve ter insights diretos para gestão de Via Permanente"""

# ── CHAMAR API ──
client = anthropic.Anthropic()

print("🤖 Chamando Claude para gerar conteúdo...")
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=4000,
    messages=[{"role": "user", "content": PROMPT}]
)

raw = response.content[0].text
# limpar possíveis blocos markdown
raw = re.sub(r'```json\s*', '', raw)
raw = re.sub(r'```\s*', '', raw)
data = json.loads(raw.strip())
print(f"✅ Conteúdo gerado: destaque = {data['destaque'][:60]}...")

# ── HELPERS HTML ──
def esc(s):
    return str(s).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;')

def dir_class(d):
    return {'up':'ti-up','down':'ti-down','flat':'ti-flat'}.get(d,'ti-flat')

def render_ticker(items):
    html = ''
    for t in items:
        html += f'<span class="ti"><span class="ti-dot">●</span><span class="ti-label">{esc(t["label"])}</span><span class="ti-val">{esc(t["valor"])}</span><span class="{dir_class(t["direcao"])}">{esc(t["variacao"])}</span></span>'
    return html * 2  # duplicar para loop infinito

def col_class(region):
    return {'brasil':'br','china':'cn','mundo':'wo'}.get(region,'wo')

def col_title_color(region):
    return {'brasil':'var(--up)','china':'var(--down)','mundo':'#6dd6da'}.get(region,'#6dd6da')

def col_flag(region):
    return {'brasil':'🇧🇷','china':'🇨🇳','mundo':'🌍'}.get(region,'🌍')

def col_title_text(region):
    return {'brasil':'Brasil','china':'China','mundo':'Mundo'}.get(region,region.title())

def render_news_col(region, items):
    cc = col_class(region)
    color = col_title_color(region)
    flag = col_flag(region)
    title = col_title_text(region)
    tag_css = {'br':'background:rgba(0,156,59,.1);color:var(--up)','cn':'background:rgba(222,41,16,.1);color:var(--down)','wo':'background:rgba(0,153,168,.1);color:#6dd6da'}.get(cc,'')
    cat_css = {'br':'color:var(--up)','cn':'color:var(--down)','wo':'color:#6dd6da'}.get(cc,'')

    nis = ''
    for n in items:
        nis += f'''
        <div class="ni">
          <div class="ni-meta"><div class="ni-dot"></div><div class="ni-cat" style="{cat_css}">{esc(n["categoria"])}</div></div>
          <div class="ni-title">{esc(n["titulo"])}</div>
          <div class="ni-body">{esc(n["corpo"])}</div>
          <span class="ni-tag" style="{tag_css}">{esc(n["tag"])}</span>
        </div>'''

    return f'''
      <div class="col-card col-{cc}">
        <div class="col-head"><div class="col-flag">{flag}</div><div class="col-title" style="color:{color}">{title}</div></div>
        <div class="col-body">{nis}</div>
      </div>'''

# ── MONTAR SEÇÕES HTML ──
ticker_html = render_ticker(data.get('ticker', []))

lead_html = esc(data['destaque'])

# mineral bar
m = data['minerio']
mineral_bar_html = f'''
      <div class="mi"><div class="mi-label">⛏️ Minério Fe 62% CFR</div><div class="mi-val">{esc(m["preco"])}</div><div class="mi-chg up">▲ {esc(m["variacao12m"])} em 12 meses</div></div>
      <div class="mi"><div class="mi-label">🏭 Importação China</div><div class="mi-val">{esc(m["importacao_china"])}</div><div class="mi-chg up">▲ aquecimento</div></div>
      <div class="mi"><div class="mi-label">⚠️ Alerta</div><div class="mi-val" style="font-size:13px;color:var(--amber);padding-top:3px">{esc(m["alerta"])}</div><div class="mi-chg warn">Ver análise ⛏️</div></div>'''

# colunas de notícias
brasil_col  = render_news_col('brasil', data.get('brasil', []))
china_col   = render_news_col('china',  data.get('china',  []))
mundo_col   = render_news_col('mundo',  data.get('mundo',  []))

# análise MRS
radar_mrs  = esc(data.get('radar_mrs', ''))
tendencias = esc(data.get('tendencias', ''))
analise_minerio = esc(data.get('analise_minerio_extra', m.get('analise', '')))

# ── LER HTML ATUAL E SUBSTITUIR PLACEHOLDERS ──
html_path = Path('index.html')
html = html_path.read_text(encoding='utf-8')

# Substituições via regex/marcadores — os blocos têm comentários delimitadores
replacements = {
    r'<!-- TICKER_START -->.*?<!-- TICKER_END -->':
        f'<!-- TICKER_START -->{ticker_html}<!-- TICKER_END -->',

    r'<!-- LEAD_START -->.*?<!-- LEAD_END -->':
        f'<!-- LEAD_START -->{lead_html}<!-- LEAD_END -->',

    r'<!-- MINERAL_BAR_START -->.*?<!-- MINERAL_BAR_END -->':
        f'<!-- MINERAL_BAR_START -->{mineral_bar_html}<!-- MINERAL_BAR_END -->',

    r'<!-- BR_COL_START -->.*?<!-- BR_COL_END -->':
        f'<!-- BR_COL_START -->{brasil_col}<!-- BR_COL_END -->',

    r'<!-- CN_COL_START -->.*?<!-- CN_COL_END -->':
        f'<!-- CN_COL_START -->{china_col}<!-- CN_COL_END -->',

    r'<!-- WORLD_COL_START -->.*?<!-- WORLD_COL_END -->':
        f'<!-- WORLD_COL_START -->{mundo_col}<!-- WORLD_COL_END -->',

    r'<!-- RADAR_MRS_START -->.*?<!-- RADAR_MRS_END -->':
        f'<!-- RADAR_MRS_START -->{radar_mrs}<!-- RADAR_MRS_END -->',

    r'<!-- TENDENCIAS_START -->.*?<!-- TENDENCIAS_END -->':
        f'<!-- TENDENCIAS_START -->{tendencias}<!-- TENDENCIAS_END -->',

    r'<!-- MINERIO_ANALISE_START -->.*?<!-- MINERIO_ANALISE_END -->':
        f'<!-- MINERIO_ANALISE_START -->{analise_minerio}<!-- MINERIO_ANALISE_END -->',

    r'<!-- HERO_DATE_START -->.*?<!-- HERO_DATE_END -->':
        f'<!-- HERO_DATE_START -->{data_curta}<!-- HERO_DATE_END -->',

    r'<!-- EDICAO_NUM_START -->.*?<!-- EDICAO_NUM_END -->':
        f'<!-- EDICAO_NUM_START -->Nº {data["edicao"]} · Compilado às 06h00<!-- EDICAO_NUM_END -->',
}

for pattern, replacement in replacements.items():
    html = re.sub(pattern, replacement, html, flags=re.DOTALL)

html_path.write_text(html, encoding='utf-8')
print(f"✅ index.html atualizado para {data_fmt}")
print(f"📌 Edição Nº {data['edicao']}")
