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
from time import sleep


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

user_GR = 'dulub'
pass_GR = 'dulub2023'

token_vuupt_BA = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiI5MzcxZDcyYi0xZTVjLTQ2OGYtOTRmNi02YjM0Yzk2NDg3N2MiLCJqdGkiOiJjNjYzY2ZlZjI0ZTAyZjQ3MzllYTgzMDczMTAyYWNmYzdkODhhNjMwMWJkNWM2OTU0NWViMjg3YTFkYzE4NzkyNjU3YTRmMmM3NGMyNWI5OCIsImlhdCI6MTY3OTkyODEzMC45MjMwOTIsIm5iZiI6MTY3OTkyODEzMC45MjMwOTUsImV4cCI6NDgzNTYwMTczMC45MDQ2ODgsInN1YiI6IjI0MDE5Iiwic2NvcGVzIjpbXX0.puMJYQySuHDRdA9PB2GRU-EGVXmhWUAgBQ9hD5jrXzNFiGuF8Vdmwoi4sP_y_SE8QzgHpJrjWZ8b7JAuFbMux_hxq6S7J17AYmfhVnB3MhQWnhrn0bmC8OQzL-CWXSHvv00qP_Yv7nPWPz-ULJH38JPY23U_RTg1g_3NNCse6Lzss7qDYB4bJVJ6Tzgtq821M3HKH0I2KsQ__s1-6zVcXuIrtehdCQAQMzdXzPp7jP5VPFqrDAdxTQJ3pGHx-5PfAKV81blrvg92CapJF9umLJpxVIXFCFBkJoAU6WCzNkueLNhBbXQw2oEuBS5C39PJ1cjchY6SKYmDJlj-nRixkpFZDwmZh4EczA6buZGIfZDXp5SqWFKHR-Os8PJcEUr1Ofv9t9mPhDa_ABkYephT3y4fjHD5eiVGwJpfhmXEj6kgpIn8uxhIATKJWz8OttfiRg2wHplGZAdKcTz_CsdIGZXwMdRZ0waZDjYHqlYKFQDSr0NZThT9gaFuTuC2PLHHrFXF9xCHvlmamGOEr2tD4Ln_yB5a9Xa2MGtiMTdLV4aUbIUyIWFSUqqOPaGMYjaDIBpakDOex2NPkThtXP5zKE76_VhwGmhM1D4wxKHMOsB33IFpvK1_BGKSl08uPcKtZPv2B0lWsz1TuCDJntz78v71GW3smaERRpupTCKY3Ao'

headers_VPT = {'Authorization': 'Bearer ' +
               token_vuupt_BA, 'Content-Type': 'application/json'}

db_host = 'localhost'
db_port = '3306'
db_user = 'dev'
db_pass = '*dUNAX()1452@'



lock = Lock()
sem = Semaphore()

@csrf_exempt
def webhook_ba(request):
    try:
        content_type = request.headers.get('Content-Type')
        if content_type == 'application/json':            
            response = request.body.decode('utf-8')
            data = json.loads(response)

            #print(json.dumps(data.get('payload'), indent=2))
            #print(json.dumps(data.get('payload'), indent=2))
            
            #print(json.dumps(data, indent=2))
                
            session_GR = requests.Session()
            auth_GR = HTTPBasicAuth(user_GR, pass_GR)

            if data.get('event') == 'Vuupt\Events\Service\ServiceAssignedEvent':
                print(data.get('event'))

                lock.acquire()
                

                con = MySQLdb.connect(host=db_host, port=int(db_port), user=db_user, password=db_pass)
                con.select_db("vuupt_gr")
                cursor = con.cursor()

                cursor.execute('select idRota from rotas')
                rotas = cursor.fetchall()

                #print(json.dumps(data.get('payload'), indent=2))            
                #print(data.get('payload')['address'])

                
                try:                    
                    cursor.execute('insert into services (endereco, latitude, longitude, idRota) values ("%s", "%s", "%s", "%s")' % (data.get('payload')['customer']['address'], data.get('payload')['customer']['latitude'], data.get('payload')['customer']['longitude'], data.get('payload')['route_id']))
                    con.commit()  
                except OperationalError:
                    lock.release()
                    print("Serviço sem rota atribuida no momento.")
                    pass
                

                route_id = data.get('payload')['route_id']
                rotas_all_id = 'https://api.vuupt.com/api/v1/routes?filter[0][field]=id&filter[0][operator]=eq&filter[0][value]=%s' % route_id
                response_rotas_all_id = requests.get(rotas_all_id, headers=headers_VPT).json()
                #print("Rotas ALL ID:", json.dumps(response_rotas_all_id, indent=2))

                try:
                    try:
                        initial_base_id = response_rotas_all_id['data'][0]['start_location_base_id']

                        rota_inicial = 'https://api.vuupt.com/api/v1/operational-bases?filter[0][field]=id&filter[0][operator]=eq&filter[0][value]=%s' % initial_base_id
                        response_rota_incial = requests.get(rota_inicial, headers=headers_VPT).json()

                        base_I = response_rota_incial['data'][0]['address']
                        lat_I = response_rota_incial['data'][0]['latitude']
                        long_I = response_rota_incial['data'][0]['longitude']
                        #print("Base inicial:", initial_base_id)
                    except KeyError:
                        lock.release()
                        print("Serviço sem rota atribuida no momento.")
                        pass
                except IndexError:
                    lock.release()
                    print("Serviço sem rota atribuida no momento.")
                    pass

                cursor.close()
                con.close()

                    
                lock.release()

            if data.get('event') == 'Vuupt\Events\Route\RouteAssignedEvent':
                print(data.get('event'))

                if False: #data.get('payload')['vehicle']['license_plate'] == 'RCY6I33':
                    pass
                else:
                    lock.acquire()
                    
                    con = MySQLdb.connect(host=db_host, port=int(db_port), user=db_user, password=db_pass)
                    con.select_db("vuupt_gr_mg")
                    cursor = con.cursor()

                    cursor.execute('select idRota from rotas')
                    rotas = cursor.fetchall()

                    #print(json.dumps(data.get('payload'), indent=2))
                    #print(json.dumps(data['payload']['agent'], indent=2))
                    #print(data.get('payload')['start_at'])
                    #print(json.dumps(data.get('payload')['activities'][0], indent=2))

                    route_id = data.get('payload')['id']
                    
                    try:                    

                        cursor.execute('select * from services where idRota = "%s"' % (route_id))
                        services = cursor.fetchall()            
                                
                        cursor.execute("insert into rotas (idRota) values (%s)" % route_id)
                        con.commit()

                        #print("Serviços:", services)

                        hora_inicio = (datetime.strptime(data.get('payload')['start_at'], "%Y-%m-%d %H:%M:%S") - timedelta(hours = 3)).strftime("%d/%m/%Y %H:%M:%S")
                        hora_final = (datetime.strptime(data.get('payload')['prevision_finish_at'], "%Y-%m-%d %H:%M:%S") - timedelta(hours = 3)).strftime("%d/%m/%Y %H:%M:%S")

                        #print(hora_inicio)
                        #print(hora_final)

                        rotas_all_id = 'https://api.vuupt.com/api/v1/routes?filter[0][field]=id&filter[0][operator]=eq&filter[0][value]=%s' % route_id
                        response_rotas_all_id = requests.get(rotas_all_id, headers=headers_VPT).json()

                        sequencia = 0

                        for i in services:
                            sequencia += 1

                            locais.append( 
                                    {
                                        "vloc_sequencia": sequencia,
                                        "vloc_descricao": i[1],
                                        "tipo_parada": 3,
                                        "refe_latitude": i[2],
                                        "refe_longitude": i[3]
                                    }
                                )
                            
                            #print(i[1], i[4])
                                
                        #print(locais)

                        '''endereco_I.clear()
                        lat_I.clear()
                        lat_I.clear()

                        endereco_F.clear()
                        lat_F.clear()
                        lat_F.clear()'''
                        #print("Rotas ALL ID:", json.dumps(response_rotas_all_id, indent=2))

                        try:
                            initial_base_id = response_rotas_all_id['data'][0]['start_location_base_id']

                            rota_inicial = 'https://api.vuupt.com/api/v1/operational-bases?filter[0][field]=id&filter[0][operator]=eq&filter[0][value]=%s' % initial_base_id
                            response_rota_incial = requests.get(rota_inicial, headers=headers_VPT).json()

                            base_I = response_rota_incial['data'][0]['address']
                            lat_I = response_rota_incial['data'][0]['latitude']
                            long_I = response_rota_incial['data'][0]['longitude']
                            #print("Base inicial:", initial_base_id)
                        except IndexError:
                            lock.release()
                            print("Rota sem atribuição no momento.")
                            pass
                        

                        '''print("Endereco base inicial:", base_I)
                        print("Latitude base inicial:", lat_I)
                        print("Longitude base inicial:", long_I)

                        print("Endereco base final:", endereco_F)
                        print("Latitude base final:", lat_F)
                        print("Longitude base final:", long_F)'''
                        
                        if data.get('payload')['agent'] != None:
                            try:
                                motorista_GR = {
                                    "motorista": [
                                        {
                                            "cpf_motorista": data.get('payload')['agent']['code'],
                                            "nome": data.get('payload')['agent']['name'],
                                            "contatos": [{
                                                "fone1": data.get('payload')['agent']['phone_number']
                                            }]
                                        }
                                    ]
                                }
                            except TypeError:
                                lock.release()
                                print("Motorista sem CPF: %s" % data.get('payload')['agent']['name'])
                                pass

                            url_Motorista = "http://grclient.grparceria.com.br/enviar_motorista"
                            post_Motorista = requests.post(
                                url=url_Motorista, auth=auth_GR, json=motorista_GR)
                            print("Motorista GR: ", post_Motorista)
                            print(json.dumps(motorista_GR, indent=2))

                            try:
                                veiculo_GR = {
                                    "veiculo": [
                                        {
                                            "placa": data.get('payload')['vehicle']['license_plate'],
                                            "tipo_veiculo": 3
                                        }
                                    ]
                                }
                            except TypeError:
                                lock.release()
                                print("Carro no encontrado")
                                pass

                            url_Veiculo = "http://grclient.grparceria.com.br/enviar_veiculo"
                            post_Veiculo = requests.post(
                                url=url_Veiculo, auth=auth_GR, json=veiculo_GR)
                            print("Veiculo GR: ", post_Veiculo)
                            print(json.dumps(veiculo_GR, indent=2))
                            
                            #for i in range(len(endereco_F)):
                                #for j in range(len(data.get('payload')['activities'])):
                            
                            try:
                                viagens_GR = {
                                            "viagem": [
                                                {
                                                    "viag_ttra_codigo": 2,
                                                    "viag_pgpg_codigo": 9000948 if data.get('payload')['vehicle']['license_plate'] != "PLM1D98" or data.get('payload')['vehicle']['license_plate'] != "RCQ3J66" or data.get('payload')['vehicle']['license_plate'] != "PKT3918" else 9000947, #9000922, #9000918, #9000902, #9000881, #9000860, #9000859, #9000845, #9000799,
                                                    "viag_valor_carga": 100000,
                                                    "veiculos": [{
                                                        "placa": data.get('payload')['vehicle']['license_plate']
                                                    }],
                                                    "motoristas": [{
                                                        "cpf_moto": data.get('payload')['agent']['code']
                                                    }],
                                                    "rota_descricao": data.get('payload')['name'],
                                                    "origem": {
                                                        "vloc_descricao": base_I,
                                                        "refe_latitude": lat_I,
                                                        "refe_longitude": long_I
                                                    },
                                                    "locais": locais,
                                                    "destino": {
                                                        "vloc_descricao": base_I,
                                                        "refe_latitude": lat_I,
                                                        "refe_longitude": long_I
                                                    },
                                                    "viag_previsao_inicio": hora_inicio,
                                                    "viag_previsao_fim": hora_final
                                                }
                                            ]
                                        }

                                url_Viagens = "http://grclient.grparceria.com.br/enviar_viagem"
                                post_Viagens = requests.post(
                                        url=url_Viagens, auth=auth_GR, json=viagens_GR)
                                print("Viagens GR: ", post_Viagens)
                                print("ID Rota: ", data.get('payload')['id'])
                                print(json.dumps(viagens_GR, indent=2))

                                if post_Motorista.status_code == 200:
                                    status_m = "Motorista OK"
                                    print(status_m)
                                else:
                                    status_m = "Erro Motorista"
                                    print(status_m)

                                if post_Veiculo.status_code == 200:
                                    status_c = "Carro OK"
                                    print(status_c)
                                else:
                                    status_c = " Erro Carro"
                                    print(status_c)

                                if post_Viagens.status_code == 200:
                                    status_v = "Viagem OK"
                                    print(status_v)
                                else:
                                    status_v = "Erro Viagem"
                                    print(status_v)

                                try:
                                    load = open('C:/Users/mra/Documents/Api_rotas/webhook_mg/public/payloads/Payload Vuupt ID %s - %s.txt' % (data.get('payload')['id'], data.get('payload')['name'].replace('/', '-')), 'w')
                                    payload = File(load)
                                    payload.write('Response: "%s" \nMotorista: "%s" \nCarro: "%s" \nViagem: "%s" \n' % (post_Viagens, status_m, status_c, status_v))
                                    payload.write('Payload: "%s"' % json.dumps(viagens_GR, indent=2))
                                    payload.close()
                                    load.close()
                                except FileNotFoundError:
                                    lock.release()
                                    print('Nao foi possivel criar payload.txt da rota.')
                                    pass

                                locais.clear()

                                cursor.close()
                                con.close()

                            except UnboundLocalError:
                                cursor.close()
                                con.close()
                                lock.release()
                                print("Base inicial não encontrada")
                                pass
                        
                        else:
                            cursor.close()
                            con.close()
                            lock.release()
                            print("Motorista ainda não foi atribuído a esta rota. Aguardando... \n")
                            pass
                    
                        
                    
                    except IntegrityError:
                        cursor.close()
                        con.close()

                        lock.release()
                        print("Rota já enviada: %s" % data.get('payload')['id'])
                        pass
                    
                    lock.release()


            return HttpResponse(jsonify(data))
        else:
            pass
            return HttpResponse("Aguardando Webhook da VUUPT...")
    except RuntimeError:
        pass
        return HttpResponse("Aguardando...")

thread = Thread(target=webhook_ba, args=())
thread.start()
thread.join()
