import socketio
import rich
from utlis.encrypt import inCrypto
import json

sio = socketio.Client()
crypt = inCrypto()
def_key = "TMP_OBJECT_CODE_!@#$%^&*()-_+'PQ"

@sio.event
def connect():
    print("connected socket io")
    data = {"fullname": "YOoooo", "username": "mmd", "phone_number": "+989904541580"}
    enc_data = crypt.encrypt(json.dumps(data), def_key)['enc']
    sio.emit("signup", {"data_enc": enc_data})

@sio.on("signup")
def sign(d):
    print(d)
    rich.print(crypt.decrypt(d['data_enc']['enc'], def_key)['dec'])

sio.connect("http://127.0.0.1:8080")
sio.wait()

"""

{'status': 'OK', 'user': {'phone': '09904541580', 'username': 'MamadAli', 'fullname': 'mmd', 'bio': '', 'profile': '
https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRFEZSqk8dJbB0Xc-fr6AWv2aocxDdFpN6maQ&', 'token': 'Vv9pGB_TtSMydHikcv2e
LsHgxIzmkL9dQcu-PtpV5cA', 'user_id': '1276065966', 'status': 'online', 'point': 'user', 'is_suspension': False, 'settings':
{'hide_phone_number': True, 'can_join_groups': True, 'inner_gif': None}}}

"""