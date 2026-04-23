# 🚂 ViaLog — Informe Ferroviário Diário

Site do informe ferroviário diário da equipe de **Estratégia de Engenharia e Manutenção de Via Permanente — MRS Logística**.

Atualização automática todo dia útil às **06h00 (Brasília)** via GitHub Actions + Claude AI.

---

## 🚀 Como configurar (passo a passo — 10 minutos)

### 1. Criar o repositório no GitHub

1. Acesse [github.com](https://github.com) e faça login
2. Clique em **"New repository"** (botão verde no canto superior direito)
3. Nome do repositório: `vialog` (ou qualquer nome que preferir)
4. Marque **"Public"** (obrigatório para GitHub Pages gratuito)
5. Clique em **"Create repository"**

---

### 2. Fazer upload dos arquivos

Após criar o repositório, faça upload dos seguintes arquivos:

```
vialog/
├── index.html          ← site principal
├── generate.py         ← script de atualização automática
└── .github/
    └── workflows/
        └── daily-update.yml  ← agendamento automático
```

> **Dica:** No GitHub, clique em "uploading an existing file" e arraste todos os arquivos de uma vez.

---

### 3. Ativar o GitHub Pages

1. No repositório, clique em **Settings** (engrenagem)
2. No menu lateral, clique em **Pages**
3. Em **"Source"**, selecione: **Deploy from a branch**
4. Em **"Branch"**, selecione: **main** → **/ (root)**
5. Clique em **Save**

Após 1-2 minutos, seu site estará disponível em:
```
https://SEU_USUARIO.github.io/vialog/
```

---

### 4. Adicionar a chave da API do Claude

Para a atualização automática funcionar, você precisa de uma chave da API da Anthropic:

1. Acesse [console.anthropic.com](https://console.anthropic.com)
2. Vá em **API Keys** → **Create Key**
3. Copie a chave gerada

No GitHub:
1. Vá em **Settings** do repositório
2. Clique em **Secrets and variables** → **Actions**
3. Clique em **New repository secret**
4. Nome: `ANTHROPIC_API_KEY`
5. Valor: cole a chave copiada
6. Clique em **Add secret**

---

### 5. Testar a atualização manual

1. No repositório, clique na aba **Actions**
2. Clique em **"ViaLog — Atualização Diária"**
3. Clique em **"Run workflow"** → **"Run workflow"** (botão verde)
4. Aguarde ~1 minuto
5. Acesse seu site — estará com conteúdo novo! ✅

---

## 📅 Agendamento automático

O site atualiza automaticamente:
- **Dias:** Segunda a Sexta
- **Horário:** 06h00 (horário de Brasília)

Para alterar o horário, edite o arquivo `.github/workflows/daily-update.yml`:
```yaml
- cron: '0 9 * * 1-5'   # 09h UTC = 06h Brasília
```

---

## 📱 Enviar link pelo WhatsApp

Após configurar, basta enviar o link para o grupo do time:

```
🚂 *ViaLog — Informe Ferroviário Diário*
Acesse as principais notícias ferroviárias e de minério:
https://SEU_USUARIO.github.io/vialog/

Atualizado toda manhã às 06h00 ☕
```

---

## 🔧 Atualizar manualmente

Se quiser atualizar fora do horário agendado:
1. Vá em **Actions** no GitHub
2. Clique em **"ViaLog — Atualização Diária"**
3. Clique em **"Run workflow"**

---

## 📁 Estrutura dos arquivos

| Arquivo | Função |
|---------|--------|
| `index.html` | Site completo com o newsletter interativo |
| `generate.py` | Script Python que chama a Claude API e atualiza o HTML |
| `.github/workflows/daily-update.yml` | Agendamento automático (GitHub Actions) |

---

## ❓ Dúvidas frequentes

**O site não atualizou no horário?**
- Verifique se a `ANTHROPIC_API_KEY` está correta em Settings → Secrets
- Verifique os logs em Actions → clique no workflow → veja o log de erro

**Quero mudar o horário?**
- Edite `daily-update.yml` e ajuste o `cron`. Use [crontab.guru](https://crontab.guru) para converter horários.

**Como adicionar novas edições ao arquivo?**
- O script `generate.py` pode ser expandido para salvar edições anteriores como JSON e listá-las no arquivo.

---

*ViaLog · Estratégia de Engenharia e Manutenção · Via Permanente · MRS Logística*
