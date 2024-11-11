# Web Scraper para Dados Meteorológicos do INMET

Este projeto é um web scraper desenvolvido em Python para coletar dados meteorológicos históricos do site do Instituto Nacional de Meteorologia do Brasil (INMET). Ele usa a biblioteca Selenium para automação de navegação na web e BeautifulSoup para manipulação de HTML, extraindo e organizando dados de cidades específicas em intervalos de datas definidos.

## Funcionalidades

- **Coleta de dados climáticos**: Extrai dados históricos de temperatura, umidade e chuva para uma lista de cidades e estados brasileiros.
- **Busca de cidades alternativas**: Caso a cidade desejada não esteja disponível, o script encontra a cidade mais próxima para garantir a coleta de dados.
- **Divisão de períodos de coleta**: Para grandes intervalos de tempo, o scraper divide a busca em blocos de 180 dias (limite do site), permitindo a coleta eficiente de grandes quantidades de dados.
- **Processamento e limpeza dos dados**: O script organiza e formata os dados extraídos, normalizando colunas, preenchendo valores e salvando os resultados como arquivos `.csv`.
- **Conversão para JSON (em desenvolvimento)**: O projeto oferece um método (comentado) para converter os dados em JSON, estruturando os dados por data e hora.

## Dependências

Este projeto requer as seguintes bibliotecas:

- `Selenium`: Para automação de navegação e interação com o site.
- `BeautifulSoup` (parte do `bs4`): Para manipulação de HTML.
- `Pandas`: Para organização e limpeza dos dados.
- `Unidecode`: Para remover acentuação de strings.
- `datetime`: Para manipulação de datas.
- `math`: Para cálculos precisos de intervalos de datas.

Para instalar as dependências, execute:

```bash
pip install selenium bs4 pandas unidecode
```

## Estrutura do Código

1. **Configuração e Inicialização**:
   - Definição da URL de busca e parâmetros de cidade e data.
   - Funções auxiliares para normalizar strings (sem acentos) e calcular intervalos de datas.

2. **Automação de Navegação**:
   - `criar_webdriver()`: Inicializa o Chrome WebDriver com configurações específicas para a coleta.
   - `esperar_elemento_visivel()`: Aguarda até que um elemento específico esteja visível antes de interagir com ele.

3. **Interação com o Site e Busca de Cidades Próximas**:
   - `selecionar_opcoes()`: Seleciona a cidade e o estado no site.
   - `buscar_cidade()`: Caso a cidade desejada não esteja disponível, encontra a cidade mais próxima para garantir dados.

4. **Coleta e Processamento dos Dados**:
   - O script coleta dados em blocos de até 180 dias, extrai o HTML e transforma em um DataFrame.
   - Remove colunas desnecessárias e ajusta nomes e formatos das colunas para facilitar a análise dos dados.

5. **Armazenamento dos Dados**:
   - Concatena os dados dos blocos e salva em arquivos `.csv` estruturados por cidade, estado e intervalo de datas.
   
6. **Exportação para JSON (Comentado)**:
   - Proporciona uma estrutura para transformar os dados em JSON para futuras análises.

## Uso

1. **Defina a lista de cidades**: No código, ajuste a lista `cidades_list` para incluir as cidades e datas desejadas.
2. **Execute o script**: Após configurar as cidades, execute o código para iniciar a coleta.
3. **Resultados**: Os arquivos `.csv` gerados serão salvos na pasta `data/temperaturas/`, com o nome no formato `<cidade>_<estado>_<data-inicio>_<data-fim>.csv`.

### Exemplo de Saída CSV

Cada arquivo contém as seguintes colunas:
- **Data**: Data de observação.
- **Hora**: Hora da coleta de dados.
- **Temperatura_Inst**: Temperatura instantânea (°C).
- **Temperatura_Max**: Temperatura máxima do dia (°C).
- **Temperatura_Min**: Temperatura mínima do dia (°C).
- **Umidade_Inst**: Umidade relativa instantânea (%).
- **Umidade_Max**: Umidade relativa máxima do dia (%).
- **Umidade_Min**: Umidade relativa mínima do dia (%).
- **Chuva_mm**: Precipitação acumulada (mm).

## Observações

- **Configuração do WebDriver**: A variável `chrome_driver_path` deve apontar para o executável do ChromeDriver. Certifique-se de que o ChromeDriver está atualizado e compatível com sua versão do navegador.
- **Confiabilidade da conexão**: O scraper faz várias requisições ao site. Uma conexão lenta ou instável pode interromper o processo; ajuste os tempos de espera (`timeout`) conforme necessário.
- **Limitações do site**: Como o site permite apenas consultas de até 180 dias por vez, o script divide períodos mais longos em blocos, para respeitar essa limitação.


