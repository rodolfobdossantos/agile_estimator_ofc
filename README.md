# Configuração de Credenciais

## 1. Obter chave e token do Trello
Para autenticar na API do Trello, você precisará de uma **API Key** e um **Token de Acesso**.

- **API Key**:  
  Acesse [https://trello.com/app-key](https://trello.com/app-key) e copie o valor exibido em **Key**.
- **Token**:  
  Na mesma página, clique no link **"Token"** para gerar um token de acesso.  
  Certifique-se de conceder permissões de leitura (`Allow read`).

> ⚠️ **Importante:** guarde esses dados em local seguro e nunca compartilhe publicamente.

---

## 2. Criar o arquivo `.env`
O projeto já contém um modelo `.env.example` sem valores.  
Siga os passos abaixo:

```bash
cp .env.example .env
```

Edite o arquivo `.env` preenchendo com suas credenciais:

```dotenv
TRELLO_API_KEY=sua_api_key_aqui
TRELLO_TOKEN=seu_token_aqui
BOARD_ID=seu_board_id_aqui
```

---

## 3. Testar se as variáveis foram carregadas
Execute o script de teste para validar o carregamento das credenciais:

```bash
python scripts/test_env.py
```

Se tudo estiver correto, a saída será semelhante a:

```
OK: Variáveis de ambiente carregadas (TRELLO_API_KEY, TRELLO_TOKEN, BOARD_ID).
```

---

## 4. Avisos de Segurança
- **NUNCA** faça commit do arquivo `.env` no repositório.
- O `.env` já está listado no `.gitignore`, mas revise antes de versionar.
- Caso uma chave/token seja exposta, **revogue e gere uma nova** imediatamente em [https://trello.com/app-key](https://trello.com/app-key).
- Não compartilhe credenciais em screenshots, commits ou mensagens.
