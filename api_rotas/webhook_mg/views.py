from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files import File
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

bases = []

config = configparser.ConfigParser()
config.read('config.ini')

user_GR = 'dulub'
pass_GR = 'dulub2023'


token_vuupt_MG = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiI5MzcxZDcyYi0xZTVjLTQ2OGYtOTRmNi02YjM0Yzk2NDg3N2MiLCJqdGkiOiI1MGM2OThjOTEzYzUwYWMyNmUyZmI4YzhkNzc2OGIyMWQ2MjQ3MWEyMTc0YTgzYjMyNzcwYmU4MTkyYTFmZDBkYTFlZWY0ZWU0NmEyMzdiMSIsImlhdCI6MTY4MTM5NTA4Ny44MDIxMDQsIm5iZiI6MTY4MTM5NTA4Ny44MDIxMDcsImV4cCI6NDgzNzA2ODY4Ny43OTIyMTgsInN1YiI6Ijk0ODEiLCJzY29wZXMiOltdfQ.q1pV2OTC7eDt_lYHstJeFnpsTUQkkwYZ9xBtZShBqcFwvMAQoVaazEbnOsqv-6DAr0yu6YRVnPaevdzVbToc73UtgbZJZrGwOPwOVkyOgtIXqY3__dM_heZNvhdZ6OFzJGVGY4JG1b662j1TWbrdBRthKqAqhlVL_6yrcSGLMCABcL761rhxYoJYUVfk7nTD35yWlH5oaZMfSllHgnUOIEfqRVzN4b0goY-zj7Yfo2MP27RWaTeKAaJ3jciR4F0AJ-kJPfc11GuPlEyq-CzQLs2NmXNAbBfWqBBu2snY6Jo6dtcDw_dAheO3m92cOkrGvKy1DQFDeFze2RlybdOhZDvcbDPgmH_bDU4nmxGLhsLWtlt2R7X8hler2n7TL8PE4w8SZ55BhrtWpKzIZJM1xQO9RCMGdKeFhC8cz0f3JhuNH9ejd0G6xYjEtnRYkklzYiYy9_-Mhgl35SsPJ4JRVlJRKGTMhmmULhbuLXoLfFe8HNVHwM9YXQcK7gAQQiI0WESjmqH3O0ll9XwtY6QyJ7dHolQz1gP-ZdcbU54yNw49Kw3Gv4tvKoj1m7kjh8-sJN8XyLeAestmVp95aVaG9jFSNfRT28X-R8q-PqLdKupLElpYs4QxaJQtndiggzT-nvXslz0B2Jq1VHTjUAhOxWLM7jxl5Erdor_oxAC-d8s'

headers_VPT = {'Authorization': 'Bearer ' +
               token_vuupt_MG, 'Content-Type': 'application/json'}

db_host = 'localhost'
db_port = '3306'
db_user = 'dev'
db_pass = '*dUNAX()1452@'



lock = Lock()
sem = Semaphore()

@csrf_exempt
def webhook_mg(request):
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

                    rota_por_ID = 'https://api.vuupt.com/api/v1/routes?filter[0][field]=id&filter[0][operator]=eq&filter[0][value]=%s' % data.get('payload')['id']
                    response_rota = requests.get(rota_por_ID, headers=headers_VPT).json()

                    servicos_por_ID = 'https://api.vuupt.com/api/v1/services?filter[0][field]=route_id&filter[0][operator]=eq&filter[0][value]=%s' % data.get('payload')['id']
                    response_servicos = requests.get(servicos_por_ID, headers=headers_VPT).json()


                    
                    try:
                        cursor.execute('insert into rotas (idRota, data) values ("%s", "%s")' % (data.get('payload')['id'], data.get('payload')['start_at']))
                        con.commit()

                        try:
                            for j in response_servicos['data']:
                                cursor.execute('insert into services (endereco, latitude, longitude, idRota) values ("%s", "%s", "%s", "%s")' % (j['address'], j['latitude'], j['longitude'], j['route_id']))
                                con.commit()
                        except OperationalError:
                            lock.release()
                            pass
                            print("Serviço sem rota atribuida no momento.")

                        hora_inicio = (datetime.strptime(response_rota['data'][0]['start_at'], "%Y-%m-%d %H:%M:%S") - timedelta(hours = 3)).strftime("%d/%m/%Y %H:%M:%S")
                        hora_final = (datetime.strptime(response_rota['data'][0]['prevision_finish_at'], "%Y-%m-%d %H:%M:%S") - timedelta(hours = 3)).strftime("%d/%m/%Y %H:%M:%S")

                        motoristas = 'https://api.vuupt.com/api/v1/users?filter[0][field]=id&filter[0][operator]=eq&filter[0][value]=%s' % response_rota['data'][0]['agent_id']
                        response_driver = requests.get(motoristas, headers=headers_VPT).json()

                        veiculos = 'https://api.vuupt.com/api/v1/vehicles?filter[0][field]=id&filter[0][operator]=eq&filter[0][value]=%s' % response_rota['data'][0]['vehicle_id']
                        response_placa = requests.get(veiculos, headers=headers_VPT).json()

                        base_inicial = 'https://api.vuupt.com/api/v1/operational-bases?filter[0][field]=id&filter[0][operator]=eq&filter[0][value]=%s' % response_rota['data'][0]['start_location_base_id']
                        response_base = requests.get(base_inicial, headers=headers_VPT).json()

                        cursor.execute('select * from services where idRota = "%s"' % (response_rota['data'][0]['id']))
                        services = cursor.fetchall()

                        cursor.execute('update rotas set driver="%s" where idRota=%s' % (response_driver['data'][0]['name'], data.get('payload')['id']))
                        con.commit()

                        cursor.execute('update rotas set placa="%s" where idRota=%s' % (response_placa['data'][0]['license_plate'], data.get('payload')['id']))
                        con.commit()

                        cursor.execute('update rotas set base="%s" where idRota=%s' % (response_base['data'][0]['name'], data.get('payload')['id']))
                        con.commit()

                        sequencia = 0

                        locais = []

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


                        try:
                            motorista_GR = {
                                "motorista": [
                                    {
                                        "cpf_motorista": response_driver['data'][0]['code'],
                                        "nome": response_driver['data'][0]['name']
                                    }
                                ]
                            }
                        except TypeError or IndexError:
                            lock.release()
                            print("Motorista sem CPF: %s" % response_driver['data'][0]['name'])
                            pass

                        url_Motorista = "http://grclient.grparceria.com.br/enviar_motorista"
                        post_Motorista = requests.post(
                            url=url_Motorista, auth=auth_GR, json=motorista_GR)
                        print("Motorista GR: ", post_Motorista)
                        print(json.dumps(motorista_GR, indent=2))

                        veiculo_GR = {
                            "veiculo": [
                                {
                                    "placa": response_placa['data'][0]['license_plate'],
                                    "tipo_veiculo": 3
                                }
                            ]
                        }

                        url_Veiculo = "http://grclient.grparceria.com.br/enviar_veiculo"
                        post_Veiculo = requests.post(
                            url=url_Veiculo, auth=auth_GR, json=veiculo_GR)
                        print("Veiculo GR: ", post_Veiculo)
                        print(json.dumps(veiculo_GR, indent=2))
                                    
                        try:
                            viagens_GR = {
                                "viagem": [
                                    {
                                        "viag_ttra_codigo": 2,
                                        "viag_pgpg_codigo": 9000967 if data.get('payload')['vehicle']['license_plate'] not in ["PLM1D98", "RCQ3J66", "PKT3918"] else 9000958, #9000922, #9000918, #9000902, #9000881, #9000860, #9000859, #9000845, #9000799,
                                        "viag_valor_carga": 100000,
                                        "veiculos": [{
                                            "placa": response_placa['data'][0]['license_plate']
                                        }],
                                        "motoristas": [{
                                            "cpf_moto": response_driver['data'][0]['code']
                                        }],
                                        "rota_descricao": response_rota['data'][0]['name'],
                                        "origem": {
                                            "vloc_descricao": response_base['data'][0]['name'],
                                            "refe_latitude": response_base['data'][0]['latitude'],
                                            "refe_longitude": response_base['data'][0]['longitude']
                                        },
                                        "locais": locais,
                                        "destino": {
                                            "vloc_descricao": response_base['data'][0]['name'],
                                            "refe_latitude": response_base['data'][0]['latitude'],
                                            "refe_longitude": response_base['data'][0]['longitude']
                                        },
                                        "viag_previsao_inicio": hora_inicio,
                                        "viag_previsao_fim": hora_final
                                    }
                                ]
                            }

                            print("ID Rota: ", response_rota['data'][0]['id'])

                        except UnboundLocalError:
                            print("Base inicial não encontrada")
                            lock.release()
                            pass

                        url_Viagens = "http://grclient.grparceria.com.br/enviar_viagem"
                        post_Viagens = requests.post(
                            url=url_Viagens, auth=auth_GR, json=viagens_GR)
                        print("Viagens GR: ", post_Viagens)
                        print(json.dumps(viagens_GR, indent=2))
                        print(json.loads(post_Viagens.text))


                        if post_Viagens.status_code == 200:
                            try:
                                sm = json.loads(post_Viagens.text)['sucesso'][0]['cod_sm']
                                msg = json.loads(post_Viagens.text)['sucesso'][0]['mensagem']                              

                                cursor.execute('update rotas set msg = "%s - %s" where idRota = %s' % (sm, msg, data.get('payload')['id']))
                                con.commit()
                            except Exception as e:
                                print(e)
                                lock.release()
                        else:
                            try:
                                # Erro sinal de veiculo
                                msg = json.loads(post_Viagens.text)['detail']['error'][0]['mensagem']
                                
                                cursor.execute('update rotas set msg = "%s" where idRota = %s' % (msg, data.get('payload')['id']))
                                con.commit()
                            except TypeError:
                                try:
                                    # Erro cpf motorista
                                    msg = "Erro no CPF do motorista. Confira as informações e tente novamente."

                                    cursor.execute('update rotas set msg = "%s" where idRota = %s' % (msg, data.get('payload')['id']))
                                    con.commit()
                                except Exception as i:
                                    print(i)
                                    lock.release()

                        '''if post_Motorista.status_code == 200:
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
                            print(status_v) '''
                                    
                        try:
                            load = open('/home/ubuntu/Documents/Projects/Django/api_rotas/webhook_mg/public/payloads/Payload Vuupt ID %s - %s.txt' % (data.get('payload')['id'], data.get('payload')['name'].replace('/', '-')), 'w')
                            payload = File(load)
                            payload.write('Response: "%s"' % (post_Viagens))
                            payload.write('Payload: "%s"' % json.dumps(viagens_GR, indent=2))
                            payload.write(post_Viagens.text)
                            payload.close()
                            load.close()
                        except FileNotFoundError:
                            lock.release()
                            print('Nao foi possivel criar payload.txt da rota.')
                            pass    
                        

                        locais.clear() 

                        cursor.close()
                        con.close()
                        
                        lock.release()
                        
                    except IntegrityError:
                        cursor.close()
                        con.close()

                        lock.release()
                        print("Rota já enviada: %s" % data.get('payload')['id'])
                        pass


            return HttpResponse(jsonify(data))
        else:
            lock.release()
            pass
            return HttpResponse("Aguardando Webhook da VUUPT...")
    except RuntimeError:
        pass
        return HttpResponse("Aguardando...")

thread = Thread(target=webhook_mg, args=())
thread.start()
thread.join()
