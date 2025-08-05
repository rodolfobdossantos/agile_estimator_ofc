- Foi criado um simples script em python para conexão ao board no trello e coleta dos nomes e ids das listas criadas no board
- Foi criado um notebook jupyter com o mesmo script criado em python para melhor visualização do resultado.

--RESUMO DO SCRIPT--
O script realiza uma consulta simples à API do Trello para verificar a conectividade com um board específico. Ele lê as variáveis de ambiente definidas no .env (TRELLO_KEY, TRELLO_TOKEN e BOARD_ID) e retorna:

* Uma mensagem de sucesso ou erro detalhado da requisição;

* Uma lista com o nome e o ID de cada lista presente no board.
