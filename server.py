from flask import Flask, request
from flask_socketio import SocketIO, emit
from handler.Handler import Handler
from utlis.encrypt import inCrypto
import json
import logging


app = Flask(__name__)
socketio = SocketIO(app)
handler = Handler()
crypto = inCrypto()
default_key = "TMP_OBJECT_CODE_!@#$%^&*()-_+'PQ"


logging.basicConfig(level=logging.INFO)

user_sessions = {}

# auth_token

@socketio.on('online')
def handle_connect(data: dict):
    if "auth_token" in data:
        logging.info(f"Client connected with SID: {request.sid}")
        verify = handler.user_manager.getUserByAuth(data.get("auth_token"))
        if verify['status'] == "OK":

            handler.online(data.get("auth_token"))

            emit('handshake', {"status": "OK", "connected_user": dict.get("auth_token")}, to=request.sid)
        else:emit("handshake", {"status": "INVALID_AUTH_TOKEN", "method": "online"}, to=request.sid)
    else:emit("handshake", {"status": "INVALID_INPUT", "method": "online"}, to=request.sid)

# auth_token

@socketio.on('offline')
def handle_disconnect(data: dict):
    if "auth_token" in data:
        logging.info(f"Client disconnected with SID: {request.sid}")
        verify = handler.user_manager.getUserByAuth(data.get("auth_token"))
        if verify['status'] == "OK":

            handler.offline(data.get("auth_token"))

            emit('handshake', {"status": "OK", "disconnected_user": dict.get("auth_token")}, to=request.sid)
        else:emit("handshake", {"status": "INVALID_AUTH_TOKEN", "method": "offline"}, to=request.sid)
    else:emit("handshake", {"status": "INVALID_INPUT", "method": "offline"}, to=request.sid)

# fullname, username, phone_number, bio ( optional ) , profile ( optional ), code ( optional )

@socketio.on("signup")
def signup_handler(data: dict):
    data: dict = crypto.decrypt(data.get("data_enc"), default_key)
    if data['error'] != True:
        data = json.loads(data['dec'])
        keys: list = list(data.keys())

        if not "phone_number" in keys:
            emit("signup", {"data_enc": crypto.encrypt({"status": "INVALID_INPUT", "method": "signup"}, default_key)}, to=request.sid)

        else:
            if not "code" in keys:
                emit("signup", {"data_enc": crypto.encrypt(json.dumps(handler.sendCode(data.get("phone_number"))), default_key)}, to=request.sid)
            else:
                agreed = handler.agreeCode(data.get("phone_number"), data.get("code"))
                if agreed['ok'] == True:
                    emit("signup", {"data_enc": crypto.encrypt(
                        json.dumps(
                            handler.createAccount(
                                data.get("username"),
                                data.get("phone_number"),
                                data.get("fullname"),
                                data.get("bio", ""),
                                data.get("profile", handler.user_profile)
                            ),
                        default_key
                        )
                    )
                }, to=request.sid)
                else:emit("signup", {"data_enc": crypto.encrypt(json.dumps({"status": "INVALID_CODE", "method": "signup"}), default_key)}, to=request.sid)
    else:emit("signup", {"data_enc": crypto.encrypt(json.dumps({"status": "INVALID_ENC", "method": "signup", "message": data['dec']}), default_key)})

# phone_number, code ( optional )

@socketio.on("login")
def login_handler(data: dict):
    data: dict = crypto.decrypt(data.get("data_enc"), default_key)
    if data.get("error") != True:
        data = json.loads(data['dec'])
        keys: list = list(data.keys())

        if not "phone_number" in keys:
            emit("login", {"status": "INVALID_INPUT", "method": "login"}, to=request.sid)

        else:
            if not "code" in keys:
                emit("login", {"data_enc": crypto.encrypt(json.dumps(handler.sendCode(data)), default_key)}, to=request.sid)
            else:
                agreed = handler.agreeCode(data.get("phone_number"), data.get("code"))
                if agreed['ok'] == True:
                    emit("login", {"data_enc": crypto.encrypt(json.dumps(handler.loginAccount(data.get("phone_number"))), default_key)}, to=request.sid)
                else:emit("login", {"data_enc": crypto.encrypt(json.dumps({"status": "INVALID_CODE", "method": "login"}), default_key)}, to=request.sid)

    else:
        emit("login", {"data_enc": crypto.encrypt(json.dumps({"status": "INVALID_ENC", "method": "login", "message": data['dec']}), default_key)})

# auth_token

@socketio.on("getMe")
def get_me(data: dict):
    data = crypto.decrypt(data.get('data_enc'), data.get("auth"))
    auth = data.get("auth")

    if data.get("error") != True:
        data = json.loads(data['dec'])
        keys: list = list(data.keys())

        if not "auth_token" in keys:
            emit("getMe", {"data_enc": crypto.encrypt(json.dumps({"status": "INVALID_INPUT", "method": "getMe"}), auth)}, to=request.sid)
        else:
            emit("getMe", handler.getMe(data.get("auth_token")), to=request.sid)
    else:
        emit("getMe", {"data_enc": crypto.encrypt(json.dumps({"status": "INVALID_ENC", "method": "getMe", "message": data['dec']}), auth)}, to=request.sid)

# auth_token, target_username

@socketio.on("getUserInfo")
def get_user_info(data: dict):
    data = crypto.decrypt(data.get('data_enc'), data.get("auth"))
    auth = data.get("auth")

    if data.get("error") != True:
        data = json.loads(data['dec'])
        keys: list = list(data.keys())

        if not "auth_token" in keys or not "target_username" in keys:
            emit("getUserInfo", {"data_enc": crypto.encrypt(json.dumps({"status": "INVALID_INPUT", "method": "getUserInfo"}), auth)}, to=request.sid)
        else:
            emit("getUserInfo", {"data_enc": crypto.encrypt(json.dumps(handler.getUserInfo(data.get("auth_token"), data.get("target_username", ""))), auth)}, to=request.sid)
    else:emit("getUserInfo", {"data_enc": crypto.encrypt(json.dumps({"status": "INVALID_ENC", "method": "getUserInfo", "message": data['dec']}), auth)}, to=request.sid)

# auth_token

@socketio.on("getAdmins")
def get_admins(data: dict):
    data = crypto.decrypt(data.get('data_enc'), data.get("auth"))
    auth = data.get("auth")

    if data.get("error") != True:
        data = json.loads(data['dec'])
        keys: list = list(data.keys())

        if not "auth_token" in keys:
            emit("getAdmins", {"data_enc": crypto.encrypt(json.dumps({"status": "INVALID_INPUT", "method": "getAdmins"}), auth)}, to=request.sid)
        else:
            emit("getAdmins", {"data_enc": crypto.encrypt(json.dumps(handler.getAdmins(data.get("auth_token"))), auth)}, to=request.sid)
    else:emit("getAdmins", {"data_enc": crypto.encrypt(json.dumps({"status": "INVALID_ENC", "method": "getAdmins", "message": data['dec']}), auth)}, to=request.sid)

# auth_token

@socketio.on("getDevs")
def get_devs(data: dict):
    data = crypto.decrypt(data.get('data_enc'), data.get("auth"))
    auth = data.get("auth")

    if data.get("error") != True:
        data = json.loads(data['dec'])
        keys: list = list(data.keys())

        if not "auth_token" in keys:
            emit("getDevs", {"data_enc": crypto.encrypt(json.dumps({"status": "INVALID_INPUT", "method": "getDevs"}), auth)}, to=request.sid)
        else:
            emit("getDevs", {"data_enc": crypto.encrypt(json.dumps(handler.getDevs(data.get("auth_token"))), auth)}, to=request.sid)
    else:emit("getDevs", {"data_enc": crypto.encrypt(json.dumps({"status": "INVALID_ENC", "method": "getDevs", "message": data['enc']}), auth)}, to=request.sid)

# auth_token
# All are Optional: fullname, username, bio, profile, inner_gif, hide_phone_number, can_join_groups

@socketio.on("editAccount")
def edit_account(data: dict):
    data = crypto.decrypt(data.get('data_enc'), data.get("auth"))
    auth = data.get("auth")

    if data.get("error") != True:
        data = json.loads(data['dec'])
        keys: list = list(data.keys())

        if not "auth_token" in keys:
            emit("editAccount", {"data_enc": crypto.encrypt(json.dumps({"status": "INVALID_INPUT", "method": "editAccount"}), auth)}, to=request.sid)
        else:
            emit(
                "editAccount",
                {
                    "data_enc": crypto.encrypt(
                        json.dumps(
                            handler.editAccount(
                                data.get("auth_token"),
                                data.get("fullname", None),
                                data.get("username", None),
                                data.get("bio", None),
                                data.get("profile", None),
                                data.get("inner_gif", None),
                                data.get("hide_phone_number", None),
                                data.get("can_join_groups", None)
                            )
                        ),
                        auth
                    )
                },
                to=request.sid
            )
    else:emit("editAccount", {"data_enc": crypto.encrypt(json.dumps({"status": "INVALID_ENC", "method": "editAccount", "message": data['enc']}), auth)}, to=request.sid)

# auth_token, username

@socketio.on("searchUser")
def search_user(data: dict):
    data = crypto.decrypt(data.get('data_enc'), data.get("auth"))
    auth = data.get("auth")

    if data.get("error") != True:
        data = json.loads(data['dec'])
        keys: list = list(data.keys())

        if not "auth_token" in keys or not "username" in keys:
            emit("searchUser", {"data_enc": crypto.encrypt(json.dumps({"status": "INVALID_INPUT", "method": "searchUser"}), auth)}, to=request.sid)
        else:
            emit("searchUser", {"data_enc": crypto.encrypt(json.dumps(handler.searchUser(data.get("auth_token"), data.get("username", ""))), auth)}, to=request.sid)
    else:emit("searchUser", {"data_enc": crypto.encrypt(json.dumps({"status": "INVALID_ENC", "method": "searchUser", "message": data['dec']}), auth)}, to=request.sid)

# username -> Baray RamzNegari az 'default_key' estefade mishe

@socketio.on("isExistsUser")
def is_exists_user(data: dict):
    data = crypto.decrypt(data.get('data_enc'))

    if data.get("error") != True:
        data = json.loads(data['dec'])
        keys: list = list(data.keys())

        if not "username" in keys:
            emit("isExistsUser", {"data_enc": crypto.encrypt(json.dumps({"status": "INVALID_INPUT", "method": "isExistsUser"}), default_key)}, to=request.sid)
        else:
            emit("isExistsUser", {"data_enc": crypto.encrypt(json.dumps(handler.isExistsUser(data.get("username", ""))), default_key)}, to=request.sid)
    else:emit("isExistsUser", {"data_enc": crypto.encrypt(json.dumps({"status": "INVALID_ENC", "method": "isExistsUser", "message": data['enc']}), default_key)}, to=request.sid)

# auth_token, group_title, group_id, group_caption ( Optional ), group_profile ( Optional ), members [ user_id, user_id ] ( Optional )

@socketio.on("createGroup")
def create_group(data: dict):
    data = crypto.decrypt(data.get('data_enc'), data.get("auth"))
    auth = data.get("auth")

    if data.get("error") != True:
        data = json.loads(data['dec'])
        keys: list = list(data.keys())

        if not "auth_token" in keys or not "group_title" in keys or not "group_id" in keys:
            emit("createGroup", {"data_enc": crypto.encrypt(json.dumps({"status": "INVALID_INPUT", "method": "createGroup"}), auth)}, to=request.sid)
        else:
            emit(
                "createGroup",
                {
                    "data_enc": crypto.encrypt(
                        json.dumps(
                            handler.createGroup(
                                data.get("auth_token"),
                                data.get("group_title"),
                                data.get("group_profile", ""),
                                data.get("group_caption", ""),
                                data.get("group_id"),
                                data.get("members", [])
                            )
                        ),
                        auth
                    )
                },
                to=request.sid
            )
            
    else:emit("createGroup", {"data_enc": crypto.encrypt(json.dumps({"status": "INVALID_ENC", "method": "createGroup", "message": data['dec']}), auth)}, to=request.sid)

# group_id -> Baray RamzNegari az 'default_key' estefade mishe

@socketio.on("getGroupByID")
def get_group_by_id(data: dict):
    data = crypto.decrypt(data.get('data_enc'))

    if data.get("error") != True:
        data = json.loads(data['dec'])
        keys: list = list(data.keys())

        if not "group_id" in keys:
            emit("getGroupByID", {"data_enc": crypto.encrypt(json.dumps({"status": "INVALID_INPUT", "method": "getGroupByID"}), default_key)}, to=request.sid)
        else:
            emit("getGroupByID", {"data_enc": crypto.encrypt(json.dumps(handler.getGroupByID(data.get("group_id"))), default_key)}, to=request.sid)
    else:emit("getGroupByID", {"data_enc": crypto.encrypt(json.dumps({"status": "INVALID_INPUT", "method": "getGroupByID"}), default_key)}, to=request.sid)

# gid -> Baray RamzNegari az 'default_key' estefade mishe

@socketio.on("getGroupByGID")
def get_group_by_gid(data: dict):
    data = crypto.decrypt(data.get('data_enc'))

    if data.get("error") != True:
        data = json.loads(data['dec'])
        keys: list = list(data.keys())

        if not "gid" in keys:
            emit("getGroupByGID", {"data_enc": crypto.encrypt(json.dumps({"status": "INVALID_INPUT", "method": "getGroupByGID"}), default_key)}, to=request.sid)
        else:
            emit("getGroupByGID", {"data_enc": crypto.encrypt(json.dumps(handler.getGroupByGID(data.get("gid"))), default_key)}, to=request.sid)
    else:emit("getGroupByGID", {"data_enc": crypto.encrypt(json.dumps({"status": "INVALID_ENC", "method": "getGroupByGID", "message": data['dec']}), default_key)}, to=request.sid)

# from_auth, gid, message

@socketio.on("sendGroupMessage")
def send_group_message(data: dict):
    data = crypto.decrypt(data.get('data_enc'), data.get("auth"))
    auth = data.get("auth")

    if data.get("error") != True:
        data = json.loads(data['dec'])
        keys: list = list(data.keys())

        if not "from_auth" in keys or not "gid" in keys or not "message" in keys:
            emit("sendGroupMessage", {"data_enc": crypto.encrypt(json.dumps({"status": "INVALID_INPUT", "method": "sendGroupMessage"}), auth)}, to=request.sid)
        else:
            emit(
                "sendGroupMessage",
                {
                    "data_enc": crypto.encrypt(
                        json.dumps(
                            handler.sendGroupMessage(
                                data.get("from_auth"),
                                data.get("gid"),
                                data.get("message"),
                                data.get("timestamp", None),
                                data.get("reply_data", {})
                            )
                        ),
                        auth
                    )
                },
                to=request.sid
            )
    else:emit("sendGroupMessage", {"data_enc": crypto.encrypt(json.dumps({"status": "INVALID_ENC", "method": "sendGroupMessage", "message": data['dec']}), auth)}, to=request.sid)

# auth_token, group_id

@socketio.on("searchGroup")
def search_group(data: dict):
    data = crypto.decrypt(data.get('data_enc'), data.get("auth"))
    auth = data.get("auth")

    if data.get("error") != True:
        data = json.loads(data['dec'])
        keys: list = list(data.keys())

        if not "auth_token" in keys or not "group_id" in keys:
            emit("searchGroup", {"data_enc": crypto.encrypt(json.dumps({"status": "INVALID_INPUT", "method": "searchGroup"}), auth)}, to=request.sid)
        else:
            emit("searchGroup", {"data_enc": crypto.encrypt(json.dumps(handler.searchGroup(data.get("auth_token"), data.get("group_id", ""))), auth)}, to=request.sid)
    else:emit("searchGroup", {"data_enc": crypto.encrypt(json.dumps({"status": "INVALID_ENC", "method": "searchGroup", "message": data['dec']}), auth)}, to=request.sid)

# auth_token, member_user_id, group_id

@socketio.on("addAdmin")
def add_admin(data: dict):
    data = crypto.decrypt(data.get('data_enc'), data.get("auth"))
    auth = data.get("auth")

    if data.get("error") != True:
        data = json.loads(data['dec'])
        keys: list = list(data.keys())

        if not "auth_token" in keys or not "member_user_id" in keys or not "group_id" in keys:
            emit("addAdmin", {"data_enc": crypto.encrypt(json.dumps({"status": "INVALID_INPUT", "method": "addAdmin"}), auth)}, to=request.sid)
        else:
            emit(
                "addAdmin",
                {
                    "data_enc": crypto.encrypt(
                        json.dumps(
                            handler.addAdmin(
                                data.get("auth_token"),
                                data.get("member_user_id"),
                                data.get("group_id")
                            )
                        ),
                        auth
                    )
                },
                to=request.sid
            )
    else:emit("addAdmin", {"data_enc": crypto.encrypt(json.dumps({"status": "INVALID_ENC", "method": "addAdmin", "message": data['dec']}), auth)}, to=request.sid)

# auth_token, member_user_id, group_id

@socketio.on("removeAdmin")
def remove_admin(data: dict):
    data = crypto.decrypt(data.get('data_enc'), data.get("auth"))
    auth = data.get("auth")

    if data.get("error") != True:
        data = json.loads(data['dec'])
        keys: list = list(data.keys())

        if not "auth_token" in keys or not "member_user_id" in keys or not "group_id" in keys:
            emit("removeAdmin", {"data_enc": crypto.encrypt(json.dumps({"status": "INVALID_INPUT", "method": "removeAdmin"}), auth)}, to=request.sid)
        else:
            emit(
                "removeAdmin",
                {
                    "data_enc": crypto.encrypt(
                        json.dumps(
                            handler.removeAdmin(
                                data.get("auth_token"),
                                data.get("member_user_id"),
                                data.get("group_id")
                            )
                        ),
                        auth
                    )
                },
                to=request.sid
            )
    else:emit("removeAdmin", {"data_enc": crypto.encrypt(json.dumps({"status": "INVALID_ENC", "method": "removeAdmin", "message": data['dec']}), auth)}, to=request.sid)

# auth_token, user_id, group_id

@socketio.on("addMemberToGroup")
def add_member_to_group(data: dict):
    data = crypto.decrypt(data.get('data_enc'), data.get("auth"))
    auth = data.get("auth")

    if data.get("error") != True:
        data = json.loads(data['dec'])
        keys: list = list(data.keys())

        if not "auth_token" in keys or not "user_id" in keys or not "group_id" in keys:
            emit("addMemberToGroup", {"data_enc": crypto.encrypt(json.dumps({"status": "INVALID_INPUT", "method": "addMemberToGroup"}), auth)}, to=request.sid)
        else:
            emit(
                "addMemberToGroup",
                {
                    "data_enc": crypto.encrypt(
                        json.dumps(
                            handler.addMemberToGroup(
                                data.get("auth_token"),
                                data.get("group_id"),
                                data.get("user_id")
                            )
                        ),
                        auth
                    )
                },
                to=request.sid
            )
    else:emit("addMemberToGroup", {"data_enc": crypto.encrypt(json.dumps({"status": "INVALID_ENC", "method": "addMemberToGroup", "message": data['dec']}), auth)}, to=request.sid)

# auth_token, group_id

@socketio.on("getGroupMembersByID")
def get_group_members_by_id(data: dict):
    data = crypto.decrypt(data.get('data_enc'), data.get("auth"))
    auth = data.get("auth")

    if data.get("error") != True:
        data = json.loads(data['dec'])
        keys: list = list(data.keys())

        if not "auth_token" in keys or not "group_id" in keys:
            emit("getGroupMembersByID", {"data_enc": crypto.encrypt(json.dumps({"status": "INVALID_INPUT", "method": "getGroupMembersByID"}), auth)}, to=request.sid)
        else:
            emit("getGroupMembersByID", {"data_enc": crypto.encrypt(json.dumps(handler.getGroupMembersByID(data.get("auth_token"), data.get("group_id"))), auth)}, to=request.sid)
    else:emit("getGroupMembersByID", {"data_enc": crypto.encrypt(json.dumps({"status": "INVALID_ENC", "method": "getGroupMembersByID", "message": data['dec']}), auth)}, to=request.sid)

# auth_token, gid

@socketio.on("getGroupMembersByGID")
def get_group_members_by_gid(data: dict):
    data = crypto.decrypt(data.get('data_enc'), data.get("auth"))
    auth = data.get("auth")

    if data.get("error") != True:
        data = json.loads(data['dec'])
        keys: list = list(data.keys())

        if not "auth_token" in keys or not "gid" in keys:
            emit("getGroupMembersByGID", {"data_enc": crypto.encrypt(json.dumps({"status": "INVALID_INPUT", "method": "getGroupMembersByGID"}), auth)}, to=request.sid)
        else:
            emit("getGroupMembersByGID", {"data_enc": crypto.encrypt(json.dumps(handler.getGroupMembersByGID(data.get("auth_token"), data.get("gid"))), auth)}, to=request.sid)
    else:emit("getGroupMembersByGID", {"data_enc": crypto.encrypt(json.dumps({"status": "INVALID_ENC", "method": "getGroupMembersByGID", "message": data['dec']}), auth)}, to=request.sid)

# auth_token, group_id, member_user_id

@socketio.on("removeMemberFromGroup")
def remove_member_from_group(data: dict):
    data = crypto.decrypt(data.get('data_enc'), data.get("auth"))
    auth = data.get("auth")

    if data.get("error") != True:
        data = json.loads(data['dec'])
        keys: list = list(data.keys())

        if not "auth_token" in keys or not "group_id" in keys or not "member_user_id" in keys:
            emit("removeMemberFromGroup", {"data_enc": crypto.encrypt(json.dumps({"status": "INVALID_INPUT", "method": "removeMemberFromGroup"}), auth)}, to=request.sid)
        else:
            emit("removeMemberFromGroup", {"data_enc": crypto.encrypt(json.dumps(handler.removeMemberFromGroup(data.get("auth_token"), data.get("member_user_id"), data.get("group_id"))), auth)}, to=request.sid)
    else:emit("removeMemberFromGroup", {"data_enc": crypto.encrypt(json.dumps({"status": "INVALID_ENC", "method": "removeMemberFromGroup", "message": data['dec']}), auth)}, to=request.sid)

# auth_token, message_id, group_id

@socketio.on("pinMessage")
def pin_message(data: dict):
    data = crypto.decrypt(data.get('data_enc'), data.get("auth"))
    auth = data.get("auth")

    if data.get("error") != True:
        data = json.loads(data['dec'])
        keys: list = list(data.keys())

        if not "auth_token" in keys or not "message_id" in keys or not "group_id" in keys:
            emit("pinMessage", {"data_enc": crypto.encrypt(json.dumps({"status": "INVALID_INPUT", "method": "pinMessage"}), auth)}, to=request.sid)
        else:
            emit(
                "pinMessage",
                {
                    "data_enc": crypto.encrypt(
                        json.dumps(
                            handler.pinMessage(
                                data.get("auth_token"),
                                data.get("message_id"),
                                data.get("group_id")
                            )
                        ),
                        auth
                    )
                },
                to=request.sid
            )
    else:emit("pinMessage", {"data_enc": crypto.encrypt(json.dumps({"status": "INVALID_ENC", "method": "pinMessage", "message": data['dec']}), auth)}, to=request.sid)

# auth_token, group_id

@socketio.on("clearPin")
def clear_pin(data: dict):
    data = crypto.decrypt(data.get('data_enc'), data.get("auth"))
    auth = data.get("auth")

    if data.get("error") != True:
        data = json.loads(data['dec'])
        keys: list = list(data.keys())

        if not "auth_token" in keys or not "group_id" in keys:
            emit("clearPin", {"data_enc": crypto.encrypt(json.dumps({"status": "INVALID_INPUT", "method": "clearPin"}), auth)}, to=request.sid)
        else:
            emit(
                "clearPin",
                {
                    "data_enc": crypto.encrypt(
                        json.dumps(
                            handler.clearPin(
                                data.get("auth_token"),
                                data.get("group_id")
                            )
                        ),
                        auth
                    )
                },
                to=request.sid
            )
    else:emit("clearPin", {"data_enc": crypto.encrypt(json.dumps({"status": "INVALID_ENC", "method": "clearPin", "message": data['dec']}), auth)}, to=request.sid)

# auth_token, group_id

@socketio.on("lockGroup")
def lock_group(data: dict):
    data = crypto.decrypt(data.get('data_enc'), data.get("auth"))
    auth = data.get("auth")

    if data.get("error") != True:
        data = json.loads(data['dec'])
        keys: list = list(data.keys())

        if not "auth_token" in keys or not "group_id" in keys:
            emit("lockGroup", {"data_enc": crypto.encrypt(json.dumps({"status": "INVALID_INPUT", "method": "lockGroup"}), auth)}, to=request.sid)
        else:
            emit(
                "lockGroup",
                {
                    "data_enc": crypto.encrypt(
                        json.dumps(
                            handler.lockGroup(
                                data.get("auth_token"),
                                data.get("group_id")
                            )
                        ),
                        auth
                    )
                },
                to=request.sid
            )
    else:emit("lockGroup", {"data_enc": crypto.encrypt(json.dumps({"status": "INVALID_ENC", "method": "lockGroup", "message": data['dec']}), auth)}, to=request.sid)

# auth_token, group_id

@socketio.on("unlockGroup")
def unlock_group(data: dict):
    data = crypto.decrypt(data.get('data_enc'), data.get("auth"))
    auth = data.get("auth")

    if data.get("error") != True:
        data = json.loads(data['dec'])
        keys: list = list(data.keys())

        if not "auth_token" in keys or not "group_id" in keys:
            emit("unlockGroup", {"data_enc": crypto.encrypt(json.dumps({"status": "INVALID_INPUT", "method": "unlockGroup"}), auth)}, to=request.sid)
        else:
            emit(
                "unlockGroup",
                {
                    "data_enc": crypto.encrypt(
                        json.dumps(
                            handler.unlockGroup(
                                data.get("auth_token"),
                                data.get("group_id")
                            )
                        ),
                        auth
                    )
                },
                to=request.sid
            )

    else:emit("unlockGroup", {"data_enc": crypto.encrypt(json.dumps({"status": "INVALID_ENC", "method": "unlockGroup", "message": data['dec']}), auth)}, to=request.sid)

# auth_token, group_id

@socketio.on("getGroupMessages")
def get_group_messages(data: dict):
    data = crypto.decrypt(data.get('data_enc'), data.get("auth"))
    auth = data.get("auth")

    if data.get("error") != True:
        data = json.loads(data['dec'])
        keys: list = list(data.keys())

        if not "auth_token" in keys or not "group_id" in keys:
            emit("getGroupMessages", {"data_enc": crypto.encrypt(json.dumps({"status": "INVALID_INPUT", "method": "getGroupMessages"}), auth)}, to=request.sid)
        else:
            emit(
                "getGroupMessages",
                {
                    "data_enc": crypto.encrypt(
                        json.dumps(
                            handler.getGroupMessages(
                                data.get("auth_token"),
                                data.get("group_id")
                            )
                        ),
                        auth
                    )
                },
                to=request.sid
            )
    else:emit("getGroupMessages", {"data_enc": crypto.encrypt(json.dumps({"status": "INVALID_ENC", "method": "getGroupMessages", "message": data['dec']}), auth)}, to=request.sid)

# group_id -> Baray RamzNegari az 'default_key' estefade mishe

@socketio.on("getGroupAdmins")
def get_group_admins(data: dict):
    data = crypto.decrypt(data.get('data_enc'), data.get("auth"))

    if data.get("error") != True:
        data = json.loads(data['dec'])
        keys: list = list(data.keys())

        if not "group_id" in keys:
            emit("getGroupAdmins", {"data_enc": crypto.encrypt(json.dumps({"status": "INVALID_INPUT", "method": "getGroupAdmins"}), default_key)}, to=request.sid)
        else:
            emit(
                "getGroupAdmins",
                {
                    "data_enc": crypto.encrypt(
                        json.dumps(
                            handler.getGroupAdmins(
                                data.get("group_id")
                            )
                        ),
                        default_key
                    )
                },
                to=request.sid
            )
    else:emit("getGroupAdmins", {"data_enc": crypto.encrypt(json.dumps({"status": "INVALID_ENC", "method": "getGroupAdmins", "message": data['dec']}), default_key)}, to=request.sid)

# from_auth, group_id, new_message, message_id

@socketio.on("editGroupMessage")
def edit_group_message(data: dict):
    data = crypto.decrypt(data.get('data_enc'), data.get("auth"))
    auth = data.get("auth")

    if data.get("error") != True:
        data = json.loads(data['dec'])
        keys: list = list(data.keys())

        if not "from_auth" in keys or not "group_id" in keys or not "new_message" \
        in keys or not "message_id" in keys:
            emit("editGroupMessage", {"data_enc": crypto.encrypt(json.dumps({"status": "INVALID_INPUT", "method": "editGroupMessage"}), auth)}, to=request.sid)
        else:
            emit(
                "editGroupMessage",
                {
                    "data_enc": crypto.encrypt(
                        json.dumps(
                            handler.editGroupMessage(
                                data.get("from_auth"),
                                data.get("group_id"),
                                data.get("message_id"),
                                data.get("new_message")
                            )
                        ),
                        auth
                    )
                },
                to=request.sid
            )
    else:emit("editGroupMessage", {"data_enc": crypto.encrypt(json.dumps({"status": "INVALID_ENC", "method": "editGroupMessage", "message": data['dec']}), auth)}, to=request.sid)

# auth_token

@socketio.on("getGroupsOfUser")
def get_groups_of_user(data: dict):
    data = crypto.decrypt(data.get('data_enc'), data.get("auth"))
    auth = data.get("auth")

    if data.get("error") != True:
        data = json.loads(data['dec'])
        keys: list = list(data.keys())

        if not "auth_token" in keys:
            emit("getGroupsOfUser", {"data_enc": crypto.encrypt(json.dumps({"status": "INVALID_INPUT", "method": "getGroupsOfUser"}), auth)}, to=request.sid)
        else:
            emit("getGroupsOfUser", {"data_enc": crypto.encrypt(json.dumps(handler.getUserGroups(data.get("auth_token"))), auth)}, to=request.sid)
    else:emit("getGroupsOfUser", {"data_enc": crypto.encrypt(json.dumps({"status": "INVALID_ENC", "method": "getGroupsOfUser", "message": data['dec']}), auth)}, to=request.sid)

# auth_token, group_id

@socketio.on("leaveGroup")
def leave_group(data: dict):
    data = crypto.decrypt(data.get('data_enc'), data.get("auth"))
    auth = data.get("auth")

    if data.get("error") != True:
        data = json.loads(data['dec'])
        keys: list = list(data.keys())

        if not "auth_token" in keys or not "group_id" in keys:
            emit("leaveGroup", {"data_enc": crypto.encrypt(json.dumps({"status": "INVALID_INPUT", "method": "leaveGroup"}), auth)}, to=request.sid)
        else:
            emit(
                "leaveGroup",
                {
                    "data_enc": crypto.encrypt(
                        json.dumps(
                            handler.leaveGroup(
                                data.get("auth_token"),
                                data.get("group_id")
                            )
                        ),
                        auth
                    )
                },
                to=request.sid
            )
    else:emit("leaveGroup", {"data_enc": crypto.encrypt(json.dumps({"status": "INVALID_ENC", "method": "leaveGroup", "message": data["dec"]}), auth)}, to=request.sid)

# auth_token, group_id

@socketio.on("joinGroup")
def join_group(data: dict):
    data = crypto.decrypt(data.get('data_enc'), data.get("auth"))
    auth = data.get("auth")

    if data.get("error") != True:
        data = json.loads(data['dec'])
        keys: list = list(data.keys())

        if not "auth_token" in keys or not "group_id" in keys:
            emit("joinGroup", {"data_enc": crypto.encrypt(json.dumps({"status": "INVALID_INPUT", "method": "joinGroup"}), auth)}, to=request.sid)
        else:
            emit(
                "joinGroup",
                {
                    "data_enc": crypto.encrypt(
                        json.dumps(
                            handler.joinGroup(
                                data.get("auth_token"),
                                data.get("group_id")
                            )
                        ),
                        auth
                    )
                },
                to=request.sid
            )
    else:emit("joinGroup", {"data_enc": crypto.encrypt(json.dumps({"status": "INVALID_ENC", "method": "joinGroup", "message": data['dec']}), auth)}, to=request.sid)

# from_auth, to_user_id, message, timestamp ( optional ), reply_data {} ( optional )

@socketio.on("sendPrivateMessage")
def send_private_message(data: dict):
    data = crypto.decrypt(data.get('data_enc'), data.get("auth"))
    auth = data.get("auth")

    if data.get("error") != True:
        data = json.loads(data['dec'])
        keys: list = list(data.keys())

        if not "from_auth" in keys or not "to_user_id" in keys or not "message" in \
        keys:
            emit("sendPrivateMessage", {"data_enc": crypto.encrypt(json.dumps({"status": "INVALID_INPUT", "method": "sendPrivateMessage"}), auth)}, to=request.sid)
        else:
            emit(
                "sendPrivateMessage",
                {
                    "data_enc": crypto.encrypt(
                        json.dumps(
                            handler.sendPrivateMessage(
                                data.get("from_auth"),
                                data.get("to_user_id"),
                                data.get("message"),
                                data.get("timestamp", None),
                                data.get("reply_data", {})
                            )
                        ),
                        auth
                    )
                },
                to=request.sid
            )
    else:emit("sendPrivateMessage", {"data_enc": crypto.encrypt(json.dumps({"status": "INVALID_ENC", "method": "sendPrivateMessage", "message": data["dec"]}), auth)}, to=request.sid)

# user_id, message_id -> Baray RamzNegari az 'default_key' estefade mishe

@socketio.on("getPrivateMessageByID")
def get_private_message_by_id(data: dict):
    data = crypto.decrypt(data.get('data_enc'), data.get("auth"))

    if data.get("error") != True:
        data = json.loads(data['dec'])
        keys: list = list(data.keys())

        if not "user_id" in keys or not "message_id" in keys:
            emit("getPrivateMessageByID", {"data_enc": crypto.encrypt(json.dumps({"status": "INVALID_INPUT", "method": "getPrivateMessageByID"}), default_key)}, to=request.sid)
        else:
            emit(
                "getPrivateMessageByID",
                {
                    "data_enc": crypto.encrypt(
                        json.dumps(
                            handler.getPrivateMessageByID(
                                data.get("user_id"),
                                data.get("message_id")
                            )
                        ),
                        default_key
                    )
                },
                to=request.sid
            )
    else:emit("getPrivateMessageByID", {"data_enc": crypto.encrypt(json.dumps({"status": "INVALID_ENC", "method": "getPrivateMessageByID", "message": data['dec']}), default_key)}, to=request.sid)

# user_id -> Baray RamzNegari az 'default_key' estefade mishe

@socketio.on("getPrivateMessagesByUserID")
def get_private_message_by_user_id(data: dict):
    data = crypto.decrypt(data.get('data_enc'), data.get("auth"))

    if data.get("error") != True:
        data = json.loads(data['dec'])
        keys: list = list(data.keys())

        if not "user_id" in keys:
            emit("getPrivateMessagesByUserID", {"data_enc": crypto.encrypt(json.dumps({"status": "INVALID_INPUT", "method": "getPrivateMessagesByUserID"}), default_key)}, to=request.sid)
        else:
            emit(
                "getPrivateMessagesByUserID",
                {
                    "data_enc": crypto.encrypt(
                        json.dumps(
                            handler.getPrivateMessagesByUserID(
                                data.get("user_id"),
                            )
                        ),
                        default_key
                    )
                },
                to=request.sid
            )
    else:emit("getPrivateMessagesByUserID", {"data_enc": crypto.encrypt(json.dumps({"status": "INVALID_ENC", "method": "getPrivateMessagesByUserID", "message": data["dec"]}), default_key)}, to=request.sid)

# from_auth_token, message_id, new_message

@socketio.on("editPrivateMessage")
def edit_private_message(data: dict):
    data = crypto.decrypt(data.get('data_enc'), data.get("auth"))
    auth = data.get("auth")

    if data.get("error") != True:
        data = json.loads(data['dec'])
        keys: list = list(data.keys())

        if not "from_auth_token" in keys or not "message_id" in keys or not "new_message" in keys:
            emit("editPrivateMessage", {"data_enc": crypto.encrypt(json.dumps({"status": "INVALID_INPUT", "method": "editPrivateMessage"}), auth)}, to=request.sid)
        else:
            emit(
                "editPrivateMessage",
                {
                    "data_enc": crypto.encrypt(
                        json.dumps(
                            handler.editPrivateMessage(
                                data.get("from_auth_token"),
                                data.get("message_id"),
                                data.get("new_message")
                            )
                        ),
                        auth
                    )
                },
                to=request.sid
            )
    else:emit("editPrivateMessage", {"data_enc": crypto.encrypt(json.dumps({"status": "INVALID_ENC", "method": "editPrivateMessage", "message": data["dec"]}), auth)}, to=request.sid)

# from_auth_token, message_id

@socketio.on("markMessageAsRead")
def edit_private_message(data: dict):
    data = crypto.decrypt(data.get('data_enc'), data.get("auth"))
    auth = data.get("auth")

    if data.get("error") != True:
        data = json.loads(data['dec'])
        keys: list = list(data.keys())

        if not "from_auth_token" in keys or not "message_id" in keys:
            emit("markMessageAsRead", {"status": "INVALID_INPUT", "method": "markMessageAsRead"}, to=request.sid)
        else:
            emit(
                "markMessageAsRead",
                handler.markMessageAsRead(
                    data.get("from_auth_token"),
                    data.get("message_id")
                ),
                to=request.sid
            )
    else:emit("markMessageAsRead", {"status": "INVALID_ENC", "method": "markMessageAsRead", "message": data['dec']}, to=request.sid)

@socketio.on("getChats")
def get_chats(data: dict):
    data = crypto.decrypt(data.get('data_enc'), data.get("auth"))
    auth = data.get("auth")

    if data.get("error") != True:
        data = json.loads(data['dec'])
        keys: list = list(data.keys())

        if not "auth_token" in keys:
            emit("getChats", {"data_enc": crypto.encrypt(json.dumps({"status": "INVALID_INPUT", "method": "getChats"}), auth)}, to=request.sid)
        else:
            emit("getChats", {"data_enc": crypto.encrypt(json.dumps(handler.getChats(data.get("auth_token"))), auth)}, to=request.sid)
    else:emit("getChats", {"data_enc": crypto.encrypt(json.dumps({"status": "INVALID_ENC", "method": "getChats", "message": data['dec']}), auth)}, to=request.sid)

@socketio.on("getMessages")
def get_messages(data: dict):
    data = crypto.decrypt(data.get('data_enc'), data.get("auth"))
    auth = data.get("auth")

    if data.get("error") != True:
        data = json.loads(data['dec'])
        keys: list = list(data.keys())

        if not "auth_token" in keys:
            emit("getMessages", {"data_enc": crypto.encrypt(json.dumps({"status": "INVALID_INPUT", "method": "getMessages"}), auth)}, to=request.sid)
        else:
            emit("getMessages", {"data_enc": crypto.encrypt(json.dumps(handler.getMessages(data.get("auth_token"))), auth)}, to=request.sid)
    else:emit("getMessages", {"data_enc": crypto.encrypt(json.dumps({"status": "INVALID_ENC", "method": "getMessages", "message": data['dec']}), auth)}, to=request.sid)


# Suspension User
@socketio.on("776c1a1d52944bfedb2b59462cec69a3a2756021258da461b540e935257481260a3abc1b0d33a1c60822924db3ef14f43eb71ba9b92d6c81eb95ae9ad83b9f40")
def suspension_user(data: dict):
    keys: list = list(data.keys())

    if not "auth_token" in keys:
        emit("776c1a1d52944bfedb2b59462cec69a3a2756021258da461b540e935257481260a3abc1b0d33a1c60822924db3ef14f43eb71ba9b92d6c81eb95ae9ad83b9f40",
             {"status": "INVALID_INPUT"}, to=request.sid)
    else:
        emit("776c1a1d52944bfedb2b59462cec69a3a2756021258da461b540e935257481260a3abc1b0d33a1c60822924db3ef14f43eb71ba9b92d6c81eb95ae9ad83b9f40",
             handler.suspensionAccount(data.get("auth_token")))
        
# Change Point
@socketio.on("dea20382d8f8c25d552df06edf78fcfb9517cd45c06e4fe0a716822890e576993bac52a165848bc2e557782dfc18a99f826e0d37caab96b9a972ba70e400fc32")
def change_point(data: dict):
    keys: list = list(data.keys())

    if not "auth_token" in keys or not "mode" in keys:
        emit("dea20382d8f8c25d552df06edf78fcfb9517cd45c06e4fe0a716822890e576993bac52a165848bc2e557782dfc18a99f826e0d37caab96b9a972ba70e400fc32",
             {"status": "INVALID_INPUT"}, to=request.sid)
    else:
        emit("dea20382d8f8c25d552df06edf78fcfb9517cd45c06e4fe0a716822890e576993bac52a165848bc2e557782dfc18a99f826e0d37caab96b9a972ba70e400fc32",
             handler.changePoint(data.get("auth_token"), data.get("mode")), to=request.sid)

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=8080)
