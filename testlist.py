import socketio
import rich

sio = socketio.Client()

@sio.event
def connect():
    print("connected socket io")
    sio.emit("getMe", {"auth_token": "Vv9pGB_TtSMydHikcv2eLsHgxIzmkL9dQcu-PtpV5cA"})

@sio.on("getMe")
def sign(d):
    rich.print(d)

sio.connect("http://127.0.0.1:8080")
sio.wait()

"""

{'status': 'OK', 'user': {'phone': '09904541580', 'username': 'MamadAli', 'fullname': 'mmd', 'bio': '', 'profile': '
https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRFEZSqk8dJbB0Xc-fr6AWv2aocxDdFpN6maQ&', 'token': 'Vv9pGB_TtSMydHikcv2e
LsHgxIzmkL9dQcu-PtpV5cA', 'user_id': '1276065966', 'status': 'online', 'point': 'user', 'is_suspension': False, 'settings':
{'hide_phone_number': True, 'can_join_groups': True, 'inner_gif': None}}}

"""