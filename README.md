# README — Agile Estimator

**Resumo rápido** Este repositório reúne scripts e notebooks criados para coletar e validar dados de sprints ágeis usando a API do Trello, gerar datasets sintéticos, criar relatórios (CSV/JSON/PDF) e validar conformidade com o modelo de dados (RSL). O README abaixo resume passos de setup, uso dos principais scripts, limitações encontradas e dicas práticas.

---

# 1. Quick start

## Pré-requisitos

- Python 3.10+ (ou 3.8+) instalado
- `venv` (virtualenv) recomendado
- Conta Trello e *API Key* + *Token* (veja seção Trello)

## Criar ambiente virtual e instalar libs

```bash
python -m venv venv
source venv/bin/activate   # Linux / macOS
# .\venv\Scripts\activate  # Windows PowerShell
pip install -r requirements.txt
```

> Se você ainda não tem `requirements.txt`, crie com as libs mínimas usadas neste projeto:

```
requests
pandas
python-dotenv
matplotlib
reportlab
python-docx
fpdf
```

## Criar `.env`

Crie um arquivo `.env` na raiz com:

```
TRELLO_KEY=your_trello_key_here
TRELLO_TOKEN=your_trello_token_here
BOARD_ID=your_board_id_here
```

**IMPORTANTE:** não commit seu `.env` (adicione abaixo no `.gitignore`).

## .gitignore mínimo

Inclua pelo menos:

```
.env
venv/
__pycache__/
*.pyc
```

---

# 2. Arquivos principais e propósito

- `agile_estimator_kickoff.ipynb` — Notebook de kickoff com:

  - carregamento de `.env`,
  - teste de requisição simples ao Trello,
  - demo de manipulação de dados com `pandas`.

- `gerador_sprints.py` — Gera dataset sintético de sprints (`sprints_simuladas.csv`) com colunas do modelo RSL.

- `gerador_apresentacao.py` — Gera apresentação PDF com preview (10 linhas) e gráficos a partir de `sprints_simuladas.csv`.

- `storypoints_bugs_ciclo.py` (ou script Trello export) — Exporta cards do board para CSV/JSON (ex.: `storypoints_bugs_ciclo.csv`, `storypoints_bugs_ciclo.json`) trazendo membros, custom fields, labels e comentários.

- `trello_cards_export.py` — Versão que obtém listas e cards do board e salva os dados (ex: `trello_board_lists.csv`).

- `validate_rsl.py` — Script/Notebook que analisa um CSV (`sprints_simuladas.csv`) e gera um relatório (PDF) mostrando se os dados seguem o modelo RSL.

- `documentacao_trello.docx` / `documentacao_trello.pdf` — Documentação compilada com limitações, plano B e recomendações.

---

# 3. Como rodar os scripts mais usados

### Gerar sprints sintéticas

```bash
python gerador_sprints.py
# gera sprints_simuladas.csv (por default 10 ou 30 sprints conforme arg)
```

### Gerar apresentação (PDF)

```bash
python gerador_apresentacao.py
# gera apresentacao_sprints.pdf
```

### Exportar cards do Trello (CSV + JSON)

```bash
python storypoints_bugs_ciclo.py
# gera storypoints_bugs_ciclo.csv e storypoints_bugs_ciclo.json
```

### Validar dataset contra o RSL e gerar relatório

```bash
python validate_rsl.py
# gera rsl_validation_report.pdf (ou nome similar)
```

---

# 4. Trello — como integrar e pontos importantes

## Obter Key e Token

- API Key: [https://trello.com/app-key](https://trello.com/app-key)
- Token: gerado a partir do link exibido quando você visita sua app-key (ou usar OAuth se preferir). Coloque os valores em `.env`.

## Variáveis esperadas no `.env`

```
TRELLO_KEY=...
TRELLO_TOKEN=...
BOARD_ID=...
```

## Campos especiais / custom fields

- Para obter o `name` de um custom field, é preciso primeiro buscar `/1/boards/{BOARD_ID}/customFields` e mapear `id -> name`.
- Endpoint usado para obter muitos cards de uma só vez: `/1/boards/{BOARD_ID}/cards` com parâmetros `members=true`, `customFieldItems=true` e `actions=...` (note: `actions` às vezes não é totalmente suportado ali — ver Observações abaixo).

## Como calcular data de criação do card

O ID do card contém timestamp (os 8 primeiros caracteres hex representam o timestamp Unix). Exemplo:

```py
from datetime import datetime, timezone
created = datetime.fromtimestamp(int(card_id[:8], 16), tz=timezone.utc)
```

## Como detectar conclusão do card (data\_conclusao)

- Preferível: procurar `actions` do tipo `updateCard` com `old.closed == False` e `card.closed == True` (procure `action['data']`).
- Alternativa: detectar `dueComplete == true` e usar campo `due` (se equipe usar data de entrega real).
- Outra heurística: movimento para lista chamada "Concluído/Done" (ver `updateCard:idList`).

---

# 5. Campos que conseguimos coletar / limitações (resumo)

| Dado Necessário | Obtido via API? | Observações                                                       |
| --------------- | --------------- | ----------------------------------------------------------------- |
| Tempo de ciclo  | Parcial         | Exige cálculo com ID e actions/dateLastActivity                   |
| Story points    | Parcial         | Só aparece se configurado como custom field                       |
| Retrabalho      | ❌               | Não existe um campo nativo; depende de processos (label/processo) |
| Complexidade    | Parcial         | Depende de custom field ou estimativa externa                     |
| Tipo de tarefa  | Parcial         | Usa labels; precisa padronização                                  |

**Limitações importantes**:

- A API não fornece diretamente "tempo de ciclo" — precisa-se calcular.
- `custom fields` são opcionais (nem todos boards/cartões os terão).
- `actions` podem exigir chamadas adicionais por card em alguns casos (a agregação por board nem sempre retorna tudo).

---

# 6. Plano B (soluções práticas)

- **Tempo de ciclo**: calcular via ID do card (creation timestamp) e `actions` (`updateCard:closed` / `updateCard:idList`) ou `dateLastActivity`.
- **Retrabalho**: padronizar uso de uma label `rework`/`retrabalho` e treinar equipes.
- **Story points ausentes**: criar e popular campo custom `Story Points` em boards piloto; caso contrário, simular dados para MVP.
- **Complexidade**: usar custom field `Complexidade` ou estimar via heurística textual (NLP) no futuro.

---

# 7. Git / GitHub / Jira — notas práticas

- \*\*Adicionar `` no \*\*`** antes de **`: isso evita erros ao indexar arquivos binários da venv (WSL/Windows causou erros como `error: open("venv/bin/python"): Invalid argument`).
- **Autenticação GitHub**: push via HTTPS exige **Personal Access Token (PAT)**; não funciona mais com senha. Alternativa: configurar SSH keys.

Exemplos:

```bash
git checkout -b AE-3-configurar-ambiente-python-local-com-venv-e-libs
git add .
git commit -m "AE-3 Configurar ambiente Python local com venv e libs"
git push -u origin AE-3-configurar-ambiente-python-local-com-venv-e-libs
```

- **Jira**: inclua a chave do ticket na mensagem de commit para vinculação automática, ex: `AE-5 Estudar o modelo de dados definido para a RSL`.

---

# 8. Boas práticas e troubleshooting

### Erros comuns e soluções rápidas

- `ModuleNotFoundError: No module named 'pandas'` → `pip install pandas` dentro do venv.
- `PermissionError: [Errno 13] Permission denied: 'sprints_simuladas.csv'` → conferir permissões e se o arquivo está aberto em outro processo, ou rodar script em pasta com permissão de escrita.
- `wkhtmltoimage` / `imgkit` erro → pacote externo não disponível; preferir solução com `matplotlib` + `PdfPages` para criar PDFs sem dependências adicionais.
- Git index errors com `venv/` → adicionar `venv/` no `.gitignore` e remover do índice: `git rm -r --cached venv`.

### Expor Jupyter Notebook fora da rede

Opções:

- SSH com túnel: habilitar `ssh` (ver `sudo systemctl status ssh`) e usar `ssh -L` para encaminhar porto.
- Ngrok (ou similar) para expor porta https temporária — atenção a riscos de segurança.

---

# 9. Entregáveis (arquivos que o repositório contém/gerou durante as tarefas)

- `agile_estimator_kickoff.ipynb` — notebook de kickoff
- `sprints_simuladas.csv` — dataset sintético (gerado)
- `sprints_simuladas.xlsx` — versão Excel formatada (se gerada)
- `apresentacao_sprints.pdf` — PDF com preview e gráficos
- `storypoints_bugs_ciclo.csv`, `storypoints_bugs_ciclo.json` — export Trello cards
- `documentacao_trello.docx` / `.pdf` — documentação de limitações e plano B
- `documentacao_trello` README e scripts auxiliares

---

