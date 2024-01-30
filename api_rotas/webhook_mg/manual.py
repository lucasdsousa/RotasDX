import requests
from requests.auth import HTTPBasicAuth
import json
import time
from datetime import *
import configparser
import MySQLdb
from MySQLdb import IntegrityError, OperationalError
import re

class manual():
    global id_rotas    

    id_rotas = []

    def start(id_rota_webhook):
        # variaveis
        config = configparser.ConfigParser()
        config.read('config.ini')

        #print(config.sections())

        db_host = config["API GR"]["db_host"]
        db_port = config["API GR"]["db_port"]
        db_user = config["API GR"]["db_user"]
        db_pass = config["API GR"]["db_pass"]

        con = MySQLdb.connect(host=db_host, port=int(db_port), user=db_user, password=db_pass)
        con.select_db("vuupt_gr_mg")
        cursor = con.cursor()
            
        user_GR = 'dulub'
        pass_GR = 'dulub2023'

        session_GR = requests.Session()
        auth_GR = HTTPBasicAuth(user_GR, pass_GR)

        token_VPT = config['API GR']['token_vuupt_MG']
        headers_VPT = {'Authorization': 'Bearer ' +
                    token_VPT, 'Content-Type': 'application/json'}


        for i in id_rotas:
            rota_por_ID = 'https://api.vuupt.com/api/v1/routes?filter[0][field]=id&filter[0][operator]=eq&filter[0][value]=%s' % i #1528335'
            response_rota = requests.get(rota_por_ID, headers=headers_VPT).json()

            servicos_por_ID = 'https://api.vuupt.com/api/v1/services?filter[0][field]=route_id&filter[0][operator]=eq&filter[0][value]=%s' % i #1528335'
            response_servicos = requests.get(servicos_por_ID, headers=headers_VPT).json()

        try:
            for j in response_servicos['data']:
                cursor.execute('insert into services (endereco, latitude, longitude, idRota) values ("%s", "%s", "%s", "%s")' % (j['address'], j['latitude'], j['longitude'], j['route_id']))
                con.commit()

        except OperationalError:
            pass
            print("Serviço sem rota atribuida no momento.")

        try:
            cursor.execute("insert into rotas (idRota) values (%s)" % response_rota['data'][0]['id'])
            con.commit()
        except IntegrityError:
            print("Rota já enviada")

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
        except TypeError:
            print("Motorista sem CPF: %s" % response_driver['data'][0]['name'])

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
                                
                                #for i in range(len(endereco_F)):
                                    #for j in range(len(data.get('payload')['activities'])):
                                
        try:
            viagens_GR = {
                "viagem": [
                    {
                        "viag_ttra_codigo": 2,
                        "viag_pgpg_codigo": 9000948, #9000918, #9000902, #9000881, #9000860, #9000859, #9000845, #9000799,
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
            pass

        url_Viagens = "http://grclient.grparceria.com.br/enviar_viagem"
        post_Viagens = requests.post(
            url=url_Viagens, auth=auth_GR, json=viagens_GR)
        print("Viagens GR: ", post_Viagens)
        print(json.dumps(viagens_GR, indent=2))
        #print(post_Viagens.text)
        if post_Motorista.status_code == 200:
            print("Motorista OK")
        else:
            print("Erro Motorista")

        if post_Veiculo.status_code == 200:
            print("Carro OK")
        else:
            print("Erro Carro")

        if post_Viagens.status_code == 200:
            print("Viagem OK")
        else:
            print("Erro Viagem")

        locais.clear() 

        cursor.close()
        con.close()
        #print(json.dumps(response['data'][0]['id'], indent=2))

        #for i in response['data']:
        #    print("ID: %s / Data: %s" % (i['id'], i['created_at']))

