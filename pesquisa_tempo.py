import time
import json
import math
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from unidecode import unidecode
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException


#       SITE DE BUSCA
url = "https://tempo.inmet.gov.br/"

cidades_list = [    #   CIDADE     ESTADO   , DATA-INICIO ,  DATA-FIM
                    # ['Senador Canedo', 'Goiás', '01/01/2022', '31/12/2023'],
                    #  ['Sorocaba', 'São Paulo', '01/01/2022', '31/12/2023'],
                    # ['Itu', 'São Paulo', '01/01/2022', '31/12/2023'],
                    ['Goiânia', 'Goiás', '01/01/2022', '31/12/2023'],  
                    # ['Lins', 'São Paulo', '01/01/2022', '31/12/2023']                                                                                                                                        
                ]
# ACENTUACAO
def remover_acentos(texto): 
    minusculo = unidecode(texto)
    return minusculo.lower()

def calcula_data(data_de_inicio, dias):
    return data_de_inicio + timedelta(days=dias)

def calcula_dif_datas(obj_data2,obj_data1):
    return (obj_data2 - obj_data1).days

def criar_webdriver():
    chrome_options = Options()
    chrome_options.headless = False
    chrome_options.add_argument("--start-maximized")

    chrome_driver_path = "C:/Users/morai/OneDrive/Documentos/Web_drive/chromedriver.exe"
    timeout = 30 

    driver = webdriver.Chrome(executable_path=chrome_driver_path, options=chrome_options)
    driver.set_page_load_timeout(timeout)
    driver.get(url)
    driver.implicitly_wait(10)

    driver.minimize_window()

    return driver

def esperar_elemento_visivel(driver, xpath, timeout=10):
    xpath_locator = (By.XPATH, xpath)
    return WebDriverWait(driver, timeout).until(EC.visibility_of_element_located(xpath_locator))

def buscar_cidade(g_driver, cidade_desejada, estado, esperar_elemento_visivel):    
    distancias = []
    g_driver.execute_script("window.open('', '_blank');")
    janelas = g_driver.window_handles
    g_driver.switch_to.window(janelas[1])
    g_driver.minimize_window()
    g_driver.get("https://www.distanciaentreascidades.com.br/")
    
    time.sleep(1)
    for destino in cidades_disponiveis:
        try:
            busca_cidade = esperar_elemento_visivel(g_driver, '/html/body/div/form/div[6]/div[1]/div[3]/div[2]/input')
            busca_cidade.send_keys(f'{cidade_desejada} {estado}')
            cidade_destino = esperar_elemento_visivel(g_driver,  '/html/body/div/form/div[6]/div[1]/div[5]/div[2]/input')
            cidade_destino.send_keys(f'{destino} {estado}')

            botao_calcula_distancia = esperar_elemento_visivel(g_driver, '/html/body/div/form/div[6]/div[1]/div[7]/a')
            botao_calcula_distancia.click()

            kms = esperar_elemento_visivel(g_driver, '/html/body/div/form/div[6]/div[3]/div[3]/div[3]/span')

            dist_km = kms.text.split(' ')[0]
            distancias.append((destino, dist_km))

            if dist_km < 10:
                break

        except Exception as e:
            busca_cidade = esperar_elemento_visivel(g_driver, '/html/body/div/form/div[6]/div[1]/div[3]/div[2]/input')
            cidade_destino = esperar_elemento_visivel(g_driver,  '/html/body/div/form/div[6]/div[1]/div[5]/div[2]/input')

            busca_cidade.clear()
            cidade_destino.clear()
            pass

    menor_distancia = min(tupla[1] for tupla in distancias)
    tupla_com_menor_distancia = next(tupla for tupla in distancias if tupla[1] == menor_distancia)

    nova_cidade = tupla_com_menor_distancia[0]
    cidade_inicial = cidade_desejada
    cidade_desejada = nova_cidade

    muda_cidade = True

    g_driver.switch_to.window(janelas[0])
    g_driver.minimize_window()
    time.sleep(1)
    return cidade_desejada, muda_cidade, cidade_inicial

def selecionar_opcoes(g_driver, estado, esperar_elemento_visivel):
    elemento_dropdown = esperar_elemento_visivel(g_driver, "/html/body/div[1]/div[2]/div[1]/div[1]/div/div[1]")
    elemento_dropdown.click()
    
    opcao_tabela_dados_estacoes = esperar_elemento_visivel(g_driver, '/html/body/div[1]/div[2]/div[1]/div[1]/div/div[2]/div[10]/span')
    opcao_tabela_dados_estacoes.click()

    elemento_estado = esperar_elemento_visivel(g_driver, "/html/body/div[1]/div[2]/div[1]/div[2]/div[2]/input")
    elemento_estado.send_keys(estado)
    
    opcoes_de_cidades = esperar_elemento_visivel(g_driver, "/html/body/div[1]/div[2]/div[1]/div[2]/div[3]")
    opcoes_de_cidades.click()
    
    time.sleep(1)

    html_content = opcoes_de_cidades.get_attribute('outerHTML')
    soup = BeautifulSoup(html_content, 'html.parser')

    time.sleep(2)

    lista_cidades_element = soup.find('div', class_='visible menu transition')
    opcoes_cidades = lista_cidades_element.find_all('div', class_='item')
    opcoes_cidades_disponiveis = [opcao.text.split('(')[0].strip() for opcao in opcoes_cidades]

    return opcoes_cidades_disponiveis

# BUSCA OS DADOS
for item  in cidades_list:
    g_driver = criar_webdriver()
    
    muda_cidade = False
    datas = []
    lista_dataframes = []
    
    cidade_desejada = item[0]
    estado          = item[1]
    data1           = item[2]
    data2           = item[3]             

    cidades_disponiveis = selecionar_opcoes(g_driver, estado, esperar_elemento_visivel)
    
    if cidade_desejada.lower() not in [c.lower() for c in cidades_disponiveis]:
        cidade_desejada, muda_cidade, cidade_inicial = buscar_cidade(g_driver, cidade_desejada, estado, esperar_elemento_visivel)

    data1_obj = datetime.strptime(data1, '%d/%m/%Y').date()
    data2_obj = datetime.strptime(data2, '%d/%m/%Y').date()

    dif_datas = calcula_dif_datas(data2_obj,data1_obj)
    blocos = dif_datas / 180
    parte_inteira, parte_decimal = divmod(blocos, 1)
    parte_decimal = round(parte_decimal, len(str(parte_decimal).split('.')[1])) if '.' in str(parte_decimal) else 0
    
    tolerancia = 1e-1000
    
    if parte_decimal > tolerancia:
        parte_inteira += 1
        parte_decimal = math.ceil(parte_decimal *180)        
        maior = True
    else:
        maior = False

    data_de_inicio = data1_obj       
    for i in range(int(parte_inteira)):  
        if i +1 == parte_inteira and maior:        
            data_de_fim = calcula_data(data_de_inicio,parte_decimal) 
        else:
            data_de_fim = calcula_data(data_de_inicio,180)

        elemento_cidade = esperar_elemento_visivel(g_driver, "/html/body/div[1]/div[2]/div[1]/div[2]/div[3]")
        actions = ActionChains(g_driver)
        actions.move_to_element(elemento_cidade).click().send_keys(cidade_desejada).send_keys(Keys.ENTER).perform()

        data_inicio = esperar_elemento_visivel(g_driver, "/html/body/div[1]/div[2]/div[1]/div[2]/div[4]/input")
        data_inicio.send_keys(data_de_inicio.strftime('%d/%m/%Y'))


        data_fim = esperar_elemento_visivel(g_driver, "/html/body/div[1]/div[2]/div[1]/div[2]/div[5]/input")
        data_fim.send_keys(data_de_fim.strftime('%d/%m/%Y'))

        botao_gera_tabela = esperar_elemento_visivel(g_driver, '/html/body/div[1]/div[2]/div[1]/div[2]/button')
        botao_gera_tabela.click()

        tabela = esperar_elemento_visivel(g_driver, '/html/body/div[1]/div[2]/div[2]/div/div/table')
        html_content = tabela.get_attribute('outerHTML')

        time.sleep(1)

        soup = BeautifulSoup(html_content, 'html.parser')
        table = soup.find(name='table')

        df_full = pd.read_html(str(table))[0]
        df_full.columns = df_full.columns.droplevel(1)

        columns_to_remove = ['Pto. Orvalho (°C)', 'Pressão (hPa)', 'Vento', 'Radiação']
        df = df_full.drop(columns=columns_to_remove, errors='ignore')

        df.columns = [f"{col}_{i}" if df.columns.duplicated().any() else col for i, col in enumerate(df.columns)]

        df = df.rename(columns={
            'Data_0': 'Data',
            'Hora_1': 'Hora',
            'Temperatura (°C)_2': 'Temperatura_Inst',
            'Temperatura (°C)_3': 'Temperatura_Max',
            'Temperatura (°C)_4': 'Temperatura_Min',
            'Umidade (%)_5': 'Umidade_Inst',
            'Umidade (%)_6': 'Umidade_Max',
            'Umidade (%)_7': 'Umidade_Min',
            'Chuva_8': 'Chuva_mm'
        })
        df['Hora'] = df['Hora'].astype(str).str.zfill(4)
        df['Hora'] = pd.to_datetime(df['Hora'], format='%H%M', errors='coerce')
        df['Hora'] = df['Hora'].dt.strftime('%H:%M')

        colunas_numericas = ['Temperatura_Inst', 'Temperatura_Max', 'Temperatura_Min', 'Umidade_Inst', 'Umidade_Max', 'Umidade_Min', 'Chuva_mm']
        for coluna in colunas_numericas:
            df[coluna] = df[coluna] / 10.0

        lista_dataframes.append(df)    

        datas.extend([data_de_inicio, data_de_fim])

        data_de_inicio = calcula_data(data_de_fim,1)

        g_driver.refresh()
        selecionar_opcoes(g_driver, estado, esperar_elemento_visivel)

    if muda_cidade:
        cidade_desejada = cidade_inicial

    cidade_desejada = remover_acentos(cidade_desejada)
    estado = remover_acentos(estado)
    
    df_final = pd.concat(lista_dataframes, ignore_index=True)

    data_de_inicio  = min(datas)
    data_de_fim     = max(datas)
    output_file     = f'data/temperaturas/{cidade_desejada.replace(" ", "_")}_{estado.replace(" ", "_")}_{data_de_inicio.strftime("%Y-%m-%d")}_{data_de_fim.strftime("%Y-%m-%d")}.csv'       

    df_final.to_csv(output_file, index=False)   

    g_driver.quit()


print('Trabalho concluído!')












# GERA JSON
# resultado_global = []
# def dataframe_to_json(df, cidade, estado):
#     if muda_cidade:
#         cidade = cidade_inicial

#     cidade = remover_acentos(cidade)
#     estado = remover_acentos(estado)

#     grouped_data = df.groupby(['Data'])
#     resultado_cidade_list = []  

#     for data, group in grouped_data:
#         horas_list = []

#         for _, row in group.iterrows():            
#             hora_formatada = datetime.strptime(row['Hora'], '%H:%M').time()

#             temp_max = float(row['Temperatura_Max'])
#             temp_min = float(row['Temperatura_Min'])
#             umi_max = float(row['Umidade_Max'])
#             umi_min = float(row['Umidade_Min'])

#             hora_entry = {
#                 'hora': row['Hora'],
#                 'temperatura_maxima': f"{temp_max:.1f} C",
#                 'temperatura_minima': f"{temp_min:.1f} C",
#                 'umidade_maxima': f"{umi_max:.1f} %",
#                 'umidade_minima': f"{umi_min:.1f} %"
#             }

#             horas_list.append(hora_entry)

#         resultado_cidade = {            
#             'data': list(data)[0],
#             'dados_por_hora': horas_list,
#         }
#         resultado_cidade_list.append(resultado_cidade)  

#         result_final = {
#             'cidade': f'{cidade}, {estado}',
#             'dados_por_dia' :resultado_cidade_list
#         }

#     return result_final 

 # resultado_json = dataframe_to_json(df, cidade_desejada, estado)
    
        # with open(output_file, 'w') as json_file:
        #     json.dump(resultado_json, json_file, indent=4)