import json
import requests
from datetime import datetime

msg = {'detail': {'sucesso': [], 'error': [{'cod_status': '0', 'valor': 9000967, 'campo': 'viag_pgpg_codigo', 'mensagem': 'O PGR selecionado nao permite criar uma SM sem que exista sinal do terminal'}]}}
msg2 = {'detail': [{'loc': ['body', 'viagem', 0, 'motoristas', 0, 'cpf_moto'], 'msg': 'string does not match regex "^\\d{3}\\d{3}\\d{3}\\d{2}$"', 'type': 'value_error.str.regex', 'ctx': {'pattern': '^\\d{3}\\d{3}\\d{3}\\d{2}$'}}]}


token_vuupt_BA = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiI5MzcxZDcyYi0xZTVjLTQ2OGYtOTRmNi02YjM0Yzk2NDg3N2MiLCJqdGkiOiJjNjYzY2ZlZjI0ZTAyZjQ3MzllYTgzMDczMTAyYWNmYzdkODhhNjMwMWJkNWM2OTU0NWViMjg3YTFkYzE4NzkyNjU3YTRmMmM3NGMyNWI5OCIsImlhdCI6MTY3OTkyODEzMC45MjMwOTIsIm5iZiI6MTY3OTkyODEzMC45MjMwOTUsImV4cCI6NDgzNTYwMTczMC45MDQ2ODgsInN1YiI6IjI0MDE5Iiwic2NvcGVzIjpbXX0.puMJYQySuHDRdA9PB2GRU-EGVXmhWUAgBQ9hD5jrXzNFiGuF8Vdmwoi4sP_y_SE8QzgHpJrjWZ8b7JAuFbMux_hxq6S7J17AYmfhVnB3MhQWnhrn0bmC8OQzL-CWXSHvv00qP_Yv7nPWPz-ULJH38JPY23U_RTg1g_3NNCse6Lzss7qDYB4bJVJ6Tzgtq821M3HKH0I2KsQ__s1-6zVcXuIrtehdCQAQMzdXzPp7jP5VPFqrDAdxTQJ3pGHx-5PfAKV81blrvg92CapJF9umLJpxVIXFCFBkJoAU6WCzNkueLNhBbXQw2oEuBS5C39PJ1cjchY6SKYmDJlj-nRixkpFZDwmZh4EczA6buZGIfZDXp5SqWFKHR-Os8PJcEUr1Ofv9t9mPhDa_ABkYephT3y4fjHD5eiVGwJpfhmXEj6kgpIn8uxhIATKJWz8OttfiRg2wHplGZAdKcTz_CsdIGZXwMdRZ0waZDjYHqlYKFQDSr0NZThT9gaFuTuC2PLHHrFXF9xCHvlmamGOEr2tD4Ln_yB5a9Xa2MGtiMTdLV4aUbIUyIWFSUqqOPaGMYjaDIBpakDOex2NPkThtXP5zKE76_VhwGmhM1D4wxKHMOsB33IFpvK1_BGKSl08uPcKtZPv2B0lWsz1TuCDJntz78v71GW3smaERRpupTCKY3Ao'

headers_VPT = {'Authorization': 'Bearer ' +
               token_vuupt_BA, 'Content-Type': 'application/json'}

#motoristas = 'https://api.vuupt.com/api/v1/users'
#response_driver = requests.get(motoristas, headers=headers_VPT).json()

'''veiculos = 'https://api.vuupt.com/api/v1/vehicles'
response_placa = requests.get(veiculos, headers=headers_VPT).json()

base_inicial = 'https://api.vuupt.com/api/v1/operational-bases'
response_base = requests.get(base_inicial, headers=headers_VPT).json()'''

print(datetime.now().utcnow())