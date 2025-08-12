# Extração de Dados do Trello

Este projeto contém dois scripts em Python para interagir com a API do Trello:

- **`get_lists_trello.py`** → Obtém todas as listas de um board e salva em CSV.
- **`extrair_cartoes_por_lista.py`** → Extrai todos os cartões de cada lista, incluindo campos customizados e comentários, e salva em CSV.

---

## 1. Como chamar as funções (exemplos de uso)

> Os scripts usam variáveis definidas no `.env`:  
> `TRELLO_KEY`, `TRELLO_TOKEN`, `BOARD_ID`.

### Obter listas do board
```bash
python get_lists_trello.py
```
Saída esperada:
```
✅ CSV salvo com sucesso: listas_boards.csv
```

### Extrair cartões por lista
```bash
python extrair_cartoes_por_lista.py
```
Saída esperada:
```
✅ Arquivo 'cartoes_por_lista.csv' gerado com sucesso!
```

---

## 2. Descrição dos campos retornados

### `listas_boards.csv`
| Campo        | Descrição |
|--------------|-----------|
| board_name   | Nome do board |
| board_id     | ID do board |
| list_name    | Nome da lista |
| list_id      | ID da lista |

---

### `cartoes_por_lista.csv`
| Campo               | Descrição |
|---------------------|-----------|
| list_id             | ID da lista onde o cartão está |
| list_name           | Nome da lista |
| card_id             | ID do cartão |
| card_name           | Nome/título do cartão |
| card_url            | URL do cartão no Trello |
| card_due            | Data de entrega (se definida) |
| card_labels         | Lista de labels associadas |
| card_members        | Membros atribuídos ao cartão |
| custom_*            | Campos customizados do board (prefixados com `custom_`) |
| card_comments       | Comentários do cartão (separados por `" | "`) |

> **Obs.:** Os nomes dos campos customizados vêm do board. Caso um campo não tenha nome mapeado, será usado `custom_<id>`.

---

## 3. Observações sobre rate limit e retries

- A API do Trello impõe um **rate limit de ~100 requisições por 10 segundos** para usuários autenticados.
- Caso haja muitos cartões/listas, é possível atingir o limite, resultando em erro **HTTP 429**.
- **Melhores práticas**:
  - Inserir `time.sleep()` entre requisições ao iterar muitas listas/cartões.
  - Implementar lógica de **retry com backoff exponencial** para requisições que retornarem 429 ou erros de rede.
  - Evitar chamadas desnecessárias (reaproveitar dados já obtidos quando possível).

---

## 4. Dependências

Instalar dependências:
```bash
pip install python-dotenv requests pandas
```

---

## 5. Arquivos gerados
- `listas_boards.csv` → Listas do board.
- `cartoes_por_lista.csv` → Cartões de cada lista, com campos customizados e comentários.
