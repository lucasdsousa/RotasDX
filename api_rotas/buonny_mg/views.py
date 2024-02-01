from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files import File
import json
from flask import jsonify
import requests
from requests.auth import HTTPBasicAuth
import json
import configparser
from datetime import datetime, timedelta
import MySQLdb
from MySQLdb import IntegrityError, OperationalError
from threading import Thread, Lock, Semaphore
import re


'''endereco_I = []
lat_I = []
long_I = []'''

endereco_F = []
lat_F = []
long_F = []

locais = []

bases = []

config = configparser.ConfigParser()
config.read('config.ini')

user_GR = ''
pass_GR = ''

token_vuupt_MG = ''
token_buonny = ''

headers_VPT = {'Authorization': 'Bearer ' +
               token_vuupt_MG, 'Content-Type': 'application/json'}

headers_Buonny = {'Authorization': 'Bearer ' +
               token_buonny, 'Content-Type': 'application/json; charset=utf-8'}

db_host = ''
db_port = ''
db_user = ''
db_pass = ''



lock = Lock()
sem = Semaphore()

@csrf_exempt
def buonny_mg(request):
    try:
        content_type = request.headers.get('Content-Type')
        if content_type == 'application/json':
            
            response = request.body
            data = json.loads(response)
            #print(json.dumps(data.get('payload'), indent=2))
            #print(json.dumps(data.get('payload'), indent=2))
            
            #print(json.dumps(data, indent=2))
                
            session_GR = requests.Session()
            auth_GR = HTTPBasicAuth(user_GR, pass_GR)

            if data.get('event') == 'Vuupt\Events\Service\ServiceAssignedEvent':
                lock.acquire()
                
                print(data.get('event'))
                
                con = MySQLdb.connect(host=db_host, port=int(db_port), user=db_user, password=db_pass)
                con.select_db("vuupt_buonny_mg")
                cursor = con.cursor()

                cursor.execute('select idRota from rotas_buonny')
                rotas = cursor.fetchall()
                

                try:
                    #print("Endereço: ", data.get('payload')['customer']['address'])
                    descr = data.get('payload')['customer']['name']

                    latitude = data.get('payload')['customer']['latitude']
                    longitude = data.get('payload')['customer']['longitude']

                    cnpj_cliente = data.get('payload')['customer']['code']

                    '''if len(cnpj_cliente) == 15:
                        cnpj_cliente_formated = '{}.{}.{}/{}-{}'.format(cnpj_cliente[:2], cnpj_cliente[2:5], cnpj_cliente[5:8], cnpj_cliente[8:12], cnpj_cliente[12:])
                    else:
                        cnpj_cliente_formated = '{}.{}.{}-{}'.format(cnpj_cliente[:3], cnpj_cliente[3:6], cnpj_cliente[6:9], cnpj_cliente[9:])
                    '''

                    nf_carga = 1
                    nf_serie = "001"
                    tipo_produto = '431'
                    valor_nf = data.get('payload')['dimension_4']
                    volume_carga = data.get('payload')['dimension_3']
                    peso_carga = data.get('payload')['dimension_2']
                    
                    try:                        
                        cursor.execute('insert into services_buonny (descricao, endereco, rua, numero, complemento, cep, bairro, cidade, estado, latitude, longitude, cnpj_cliente, nf_carga, nf_serie, tipo_produto, valor_nf, volume_carga, peso_carga, idRota) values ("%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s")' % (data.get('payload')['customer']['name'], data.get('payload')['customer']['address'], "NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL", latitude, longitude, cnpj_cliente, nf_carga, nf_serie, tipo_produto, valor_nf, volume_carga, peso_carga, data.get('payload')['route_id']))
                        con.commit() 
                    except OperationalError:
                        lock.release()
                        print("Serviço sem rota atribuida no momento.")
                        pass
                    
                except IndexError:
                    lock.release()
                    print("Erro no endereço")
                    pass
                        
                cursor.close() 
                con.close()

                lock.release()

            if data.get('event') == 'Vuupt\Events\Route\RouteAssignedEvent':
                print(data.get('event'))
                
                if data.get('payload')['vehicle']['license_plate'] == 'RCY6I33':
                    lock.acquire()
                    
                    con = MySQLdb.connect(host=db_host, port=int(db_port), user=db_user, password=db_pass)
                    con.select_db("vuupt_buonny_mg")
                    cursor = con.cursor()
                    #print(json.dumps(data.get('payload'), indent=2))
                    #print(json.dumps(data['payload']['agent'], indent=2))
                    #print(data.get('payload')['start_at'])
                    #print(json.dumps(data.get('payload')['activities'][0], indent=2))

                    route_id = data.get('payload')['id']
                    
                    try:  

                        cursor.execute("insert into rotas_buonny (idRota) values (%s)" % route_id)
                        con.commit()

                        cursor.execute('select * from services_buonny where idRota = "%s"' % (route_id))
                        services = cursor.fetchall()

        
                        hora_inicio = (datetime.now() + timedelta(minutes = 30)).strftime("%d/%m/%Y %H:%M:%S")
                        hora_final = (datetime.strptime(data.get('payload')['prevision_finish_at'], "%Y-%m-%d %H:%M:%S") - timedelta(hours = 3)).strftime("%d/%m/%Y %H:%M:%S")

                        previsao = []

                        for n in data.get('payload')['activities']:
                            prevision_arrive = n['prevision_initial_arrive_at'] if n['prevision_initial_arrive_at'] != "null" else n['prevision_initial_end_at']
                            previsao.append(prevision_arrive)

                        sequencia = 0

                        for i in services:
                            sequencia += 1

                            try:
                                locais.append(
                                        {
                                                    "codigo_externo":'{}.{}.{}/{}-{}'.format(i[12][:2], i[12][2:5], i[12][5:8], i[12][8:12], i[12][12:]) if len(i[12]) == 14 else '{}.{}.{}-{}'.format(i[12][:3], i[12][3:6], i[12][6:9], i[12][9:]),
                                                    "descricao":i[1],
                                                    "tipo_parada": "3",
                                                    "previsao_de_chegada":(datetime.strptime(previsao[sequencia], "%Y-%m-%d %H:%M:%S")).strftime("%d/%m/%Y %H:%M:%S"),
                                                    "dados_da_carga":{
                                                        "carga":[
                                                            {
                                                                "NF":i[13],
                                                                "serie_nf":"001",
                                                                "tipo_produto":"431",
                                                                "valor_total_nf":i[16],
                                                                "volume":i[17],
                                                                "peso":i[18]
                                                            }
                                                        ]
                                                    }
                                        }
                                        
                                )
                            except IndexError:
                                pass

                        request_rota_id = 'https://api.vuupt.com/api/v1/routes?filter[0][field]=id&filter[0][operator]=eq&filter[0][value]=%s' % route_id
                        response_rota_id = requests.get(request_rota_id, headers=headers_VPT).json()

                        
                        initial_base_id = response_rota_id['data'][0]['start_location_base_id']

                        rota_inicial = 'https://api.vuupt.com/api/v1/operational-bases?filter[0][field]=id&filter[0][operator]=eq&filter[0][value]=%s' % initial_base_id
                        response_rota_inicial = requests.get(rota_inicial, headers=headers_VPT).json()

                        base_I = response_rota_inicial['data'][0]['address'].replace('- ', ',').replace('-', '').split(",")
                        #print(response_rota_inicial['data'][0]['address'])
                        descr_base_I = response_rota_inicial['data'][0]['name']

                        cnpj_base_I = response_rota_inicial['data'][0]['address_complement']

                        lat_I = response_rota_inicial['data'][0]['latitude']
                        long_I = response_rota_inicial['data'][0]['longitude']
                            #print("Base inicial:", initial_base_id)
                        

                        '''print("Endereco base inicial:", base_I)
                        print("Latitude base inicial:", lat_I)
                        print("Longitude base inicial:", long_I)

                        print("Endereco base final:", endereco_F)
                        print("Latitude base final:", lat_F)
                        print("Longitude base final:", long_F)'''
                        
                        if data.get('payload')['agent'] != None:
                            
                            #for i in range(len(endereco_F)):
                                #for j in range(len(data.get('payload')['activities'])):
                            
                            try:
                                viagem_Buonny = {
                                    "autenticacao":{
                                        "token":token_buonny
                                    },
                                    "cnpj_cliente":'05092901001227',
                                    "cnpj_embarcador":'05092901001227',
                                    "cnpj_transportador":'05092901001227',
                                    "cnpj_gerenciadora_de_risco":"0",
                                    "pedido_cliente":route_id,
                                    "numero_liberacao":route_id,
                                    "tipo_de_transporte":"2",
                                    "controle_temperatura":{
                                        "de":0,
                                        "Ate":0
                                    },
                                    "Observacao":"0",
                                    "motorista":{
                                        "nome":data.get('payload')['agent']['name'],
                                        "cpf":data.get('payload')['agent']['code'],
                                        "telefone":data.get('payload')['agent']['phone_number'],
                                        "radio":"0"
                                    },
                                    "veiculos":{
                                        "placa":data.get('payload')['vehicle']['license_plate']                                    
                                    },
                                    "origem":{
                                        "codigo_externo":cnpj_base_I,
                                        "descricao":descr_base_I,
                                    },
                                    "monitorar_retorno": 0,
                                    "data_previsao_inicio":hora_inicio,
                                    "data_previsao_fim":hora_final,
                                    "itinerario": {
                                        "alvo": locais
                                    },
                                    "iscas":{
                                        "isca":[
                                            
                                        ]
                                    },
                                    "operacao_sm":"",
                                    "codigo_sm":"",
                                    "rota_codigo_externo":""
                                }

                                url_Viagens = "https://api.buonny.com.br/portal/viagens.json"
                                post_Viagens = requests.post(
                                        url=url_Viagens, headers=headers_Buonny, data=json.dumps(viagem_Buonny, ensure_ascii=False))
                                print("Viagem: ", post_Viagens)
                                print("ID Rota: ", route_id)
                                print(json.dumps(viagem_Buonny, indent=2, ensure_ascii=False))
                                print("Response: ", post_Viagens.text)

                                try:
                                    load = open('C:/Users/mra/Documents/Api_rotas/buonny_mg/public/payloads/Payload Vuupt ID %s - %s.txt' % (data.get('payload')['id'], data.get('payload')['name'].replace('/', '-')), 'w')
                                    payload = File(load)
                                    payload.write('Response: "%s"' % post_Viagens)
                                    payload.write(json.dumps(viagem_Buonny, indent=2))
                                    payload.write(post_Viagens.text)
                                    payload.close()
                                    load.close()
                                except FileNotFoundError:
                                    lock.release()
                                    print('Nao foi possivel criar payload.txt da rota.')
                                    pass

                                locais.clear()

                            except UnboundLocalError:
                                lock.release()
                                print("Base inicial não encontrada")
                                pass
                        
                        else:
                            lock.release()
                            print("Motorista ainda não foi atribuído a esta rota. Aguardando... \n")
                            pass
                    
                        
                    
                    except IntegrityError:
                        lock.release()
                        print("Rota já enviada: %s" % data.get('payload')['id'])
                        pass
                    
                    lock.release()
                    
                    cursor.close()
                    con.close()
                else:
                    pass
                    

            return HttpResponse(jsonify(data))
        else:
            pass
            return HttpResponse("Aguardando Webhook da VUUPT...")
    except RuntimeError:
        pass
        return HttpResponse("Aguardando...")

thread = Thread(target=buonny_mg, args=())
thread.start()
thread.join()

