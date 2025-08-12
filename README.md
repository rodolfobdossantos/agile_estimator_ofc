# Extração de Cartões por Lista - Trello

Este script permite extrair todos os cartões de um board do Trello, incluindo campos customizados e comentários, salvando o resultado em um arquivo CSV.

---

## 1. Comando para executar

```bash
python extrair_cartoes_por_lista.py --board-id <ID_DO_BOARD>
```

> **Obs.:** O script atual lê o `BOARD_ID` do arquivo `.env`. Se preferir passar via parâmetro, adapte o código para receber `sys.argv`.

Certifique-se de que o `.env` contém:

```dotenv
TRELLO_KEY=sua_chave_aqui
TRELLO_TOKEN=seu_token_aqui
BOARD_ID=seu_board_id_aqui
```

---

## 2. Dicionário de colunas

O arquivo `cartoes_por_lista.csv` conterá as seguintes colunas (mais colunas extras para campos customizados):

| Coluna             | Descrição |
|--------------------|-----------|
| list_id            | ID da lista onde o cartão está |
| list_name          | Nome da lista |
| card_id            | ID do cartão |
| card_name          | Nome/título do cartão |
| card_url           | URL pública do cartão |
| card_due           | Data de entrega do cartão (se houver) |
| card_labels        | Labels associadas ao cartão (separadas por vírgula) |
| card_members       | Membros atribuídos ao cartão (nomes completos, separados por vírgula) |
| custom_*           | Campos customizados do board (prefixo `custom_` seguido do nome ou ID do campo) |
| card_comments      | Comentários do cartão (separados por ` | `) |

---

## 3. Como configurar listas, labels e aliases

O script **não filtra** listas ou labels por padrão — ele busca todos os cartões de todas as listas do board informado.

Para configurar:
- **Filtrar listas específicas:** adicione lógica antes do loop principal para verificar `list_name` ou `list_id`.
- **Filtrar por labels:** adicione filtro dentro do loop de cartões verificando `card_labels`.
- **Aliases de listas/labels:** crie um dicionário no código mapeando nomes reais para apelidos, por exemplo:

```python
aliases_listas = {
    "To Do": "A Fazer",
    "Doing": "Em Progresso"
}
list_name = aliases_listas.get(list_name, list_name)
```

---

## 4. Limitações conhecidas

- **Rate Limit**: a API do Trello limita requisições (aprox. 100 por 10 segundos). Em boards grandes, pode ocorrer erro HTTP 429.
- **Paginação**: o script não implementa paginação para comentários ou campos customizados muito extensos.
- **Campos customizados**: apenas o primeiro valor (texto/número/opção) é capturado.
- **Dependência do `.env`**: atualmente, o script depende de variáveis definidas no `.env`. Não há suporte direto para parâmetros via CLI.
- **Ausência de retries**: em caso de erro temporário de rede ou limite excedido, o script falha sem tentar novamente.
