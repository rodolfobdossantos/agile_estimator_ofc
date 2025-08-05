- Foi criado um script python para geração de um .csv com dados fictícios de 10 sprints, seguindo as colunas e campos descritos na task AE6
- A princípio seria somente a geração de um .csv, porém tomei a liberdade de incluir uma função que cria também um .xlsxs formatado para melhor visualização dos dados. Para isso usei o pacote "openpyxl", o mesmo já foi incluído em "requirements.txt"


--RESUMO DO SCRIPT--
Este script gera um conjunto de dados sintéticos (fictícios, porém realistas) sobre sprints ágeis, com o objetivo de alimentar e testar modelos de estimativa de produtividade como o Agile Estimator.

Ele cria automaticamente dois arquivos:

*sprints_simuladas.csv → dados brutos em formato CSV
*sprints_formatadas.xlsx → mesma base de dados com formatação legível no Excel

Cada linha representa uma sprint com campos como: período da sprint, número de membros da equipe, cartões previstos e entregues, story points, produtividade estimada, percentual de bugs e retrabalho, entre outros.

O script utiliza as bibliotecas:
*pandas (manipulação de dados)
*random (valores simulados)
*datetime (controle de datas)
*openpyxl (formatação no Excel)
