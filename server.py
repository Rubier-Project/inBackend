from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room, leave_room, rooms
from handler.Handler import Handler
import logging


app = Flask(__name__)
socketio = SocketIO(app)
handler = Handler()


logging.basicConfig(level=logging.INFO)

user_sessions = {}

# @socketio.on('authenticate')
# def handle_authenticate(data):
#     try:
#         username = data.get('username')
#         token = data.get('token')
#         user_manager = UserManager()
        
#         if user_manager.authenticate_user(username=username, auth_token=token).get('status') == 'OK':
#             user_sessions[username] = request.sid
#             join_room(username)
#             user_manager.online(username=username, auth_token=token, status='online')
#             emit('authenticated', {'message': 'User authenticated', 'username': username}, to=request.sid)
#         else:
#             emit('authentication_failed', {'message': 'Authentication failed'}, to=request.sid)
#             user_manager.online(username=username, auth_token=token, status='offline')
#             logging.warning(f"Authentication failed for user {username}")
#     except Exception as e:
#         logging.error(f"An error occurred during authentication: {str(e)}")
#         emit('error', {'message': 'Internal server error'}, to=request.sid)

# @socketio.on('getChats')
# def handle_get_chats(data):
#     try:
#         user_manager = UserManager()
#         username = data.get('username')
#         token = data.get('token')
#         handler = Handler(chatManager=ChatManager(UserManager()), userManager=user_manager)
        
#         result = handler.getChats(username=username, token=token)
#         user_manager.online(username=username, auth_token=token, status='online')
#         emit('chats_list', result, to=request.sid)
#     except Exception as e:
#         logging.error(f"Error in handle_get_chats: {str(e)}")
#         emit('error', {'message': str(e)}, to=request.sid)

# @socketio.on('getChatsGroup')
# def handle_get_chats_group(data):
#     try:
#         user_manager = UserManager()
#         username = data.get('username')
#         token = data.get('token')
        
#         handler = Handler(chatManager=ChatManager(UserManager()), userManager=user_manager)
#         result = handler.getChatsGroup(username=username, token=token)
        
#         if result['status'] == 'OK':
#             emit('group_list', result['data'], to=request.sid)
#         else:
#             emit('error', {'message': result['status']}, to=request.sid)
    
#     except Exception as e:
#         logging.error(f"Error in handle_get_chats_group: {str(e)}")
#         emit('error', {'message': str(e)})

# @socketio.on('getMessage')
# def handle_get_messages(data):
#     try:
#         user_manager = UserManager()
#         username = data.get('username')
#         token = data.get('token')
#         user = data.get('user')
#         handler = Handler(chatManager=ChatManager(UserManager()), userManager=user_manager)
        
#         result = handler.getMessages(username=username, token=token, user=user)
#         user_manager.online(username=username, auth_token=token, status='online')
#         emit('messages', result, to=request.sid)
        
#     except Exception as e:
#         logging.error(f"Error in handle_get_messages: {str(e)}")
#         emit('error', {'message': str(e)})

# @socketio.on('markAsRead')
# def handle_mark_as_read(data):
#     try:
#         user_manager = UserManager()
#         username = data.get('username')
#         token = data.get('token')
#         target_user = data.get('target_user')
#         handler = Handler(chatManager=ChatManager(UserManager()), userManager=user_manager)
        
#         result = handler.mark_messages_as_read(username=username, token=token, target_user=target_user)
#         user_manager.online(username=username, auth_token=token, status='online')
#         emit('messages_marked_as_read', result, to=request.sid)
#     except Exception as e:
#         logging.error(f"Error in handle_mark_as_read: {str(e)}")
#         emit('error', {'message': str(e)})

# @socketio.on('sendMessage')
# def handle_send_private_message(data):
#     user_manager = UserManager()
#     chat_manager = ChatManager(user_manager=user_manager)
#     handler = Handler(chatManager=chat_manager, userManager=user_manager)

#     try:
#         from_user = data.get('from')
#         to_user = data.get('to')


#         if from_user in user_sessions and to_user in user_sessions:
#             result = handler.handle_send_message(data)
            
#             if result['status'] == 'success':
#                 print(f'\033[31m|| SID :: {request.sid} || DATA ::: {data} || TO ::: {to_user} || FROM_USER ::: {from_user} || {user_sessions}')
#                 socketio.emit(f'receive_private_message', result['data'], room=to_user)
#                 socketio.emit(f'receive_private_message', result['data'], room=from_user)
#             else:
#                 logging.error(f"Message handling error: {result['message']}")
#         else:
#             print(f'Offline Users {user_sessions}')
#             result = handler.handle_send_message(data)
#             socketio.emit(f'offline', result['data'], room=from_user, to=request.sid)

#     except Exception as e:
#         logging.error(f"An unexpected error occurred: {str(e)}")

# @socketio.on('sendGroupMessage')
# def handle_send_group_message(data):
#     print(f"SendMessage To group {data}")
#     user_manager = UserManager()
#     chat_manager = ChatManager(user_manager=user_manager)

#     handler = Handler(chatManager=chat_manager, userManager=user_manager)

#     try:
#         from_user = data.get('from')
#         group_name = data.get('group')

#         if from_user in user_sessions and group_name in user_sessions:
#             result = handler.handle_send_group_message(data)
            
#             if result['status'] == 'success':
#                 for member in user_sessions:
#                     socketio.emit('receive_group_message', result['data'], room=member)
#             else:
#                 logging.error(f"Message handling error: {result['message']}")
#         else:
#             result = handler.handle_send_group_message(data)
#             socketio.emit(f'offline', result['data'], room=from_user)

#     except Exception as e:
#         logging.error(f"An unexpected error occurred: {str(e)}")

# @socketio.on('getGroupMessages')
# def handle_get_group_messages(data):
#     try:
#         user_manager = UserManager()
#         username = data.get('username')
#         token = data.get('token')
#         group_name = data.get('group')
#         handler = Handler(chatManager=ChatManager(UserManager()), userManager=user_manager)
        
#         result = handler.getGroupMessages(username=username, token=token, group_name=group_name)
#         if result['status'] == 'OK':
#             emit('group_messages', result['data'], to=request.sid)
#         else:
#             emit('error', {'message': result['status']}, to=request.sid)
    
#     except Exception as e:
#         logging.error(f"Error in handle_get_group_messages: {str(e)}")
#         emit('error', {'message': str(e)})

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
            
@socketio.on("signup")
def signup_handler(data: dict):
    keys: list = list(data.keys())

    if not "phone_number" in keys:
        emit("signup", {"status": "INVALID_INPUT", "method": "signup"}, to=request.sid)

    else:
        if not "code" in keys:
            emit("signup", handler.sendCode(data.get("phone_number")), to=request.sid)
        else:
            agreed = handler.agreeCode(data.get("phone_number"), data.get("code"))
            if agreed['ok'] == True:
                emit("signup", handler.createAccount(
                    data.get("username"),
                    data.get("phone_number"),
                    data.get("fullname"),
                    data.get("bio", ""),
                    data.get("profile", handler.user_profile)
                ), to=request.sid)
            else:emit("signup", {"status": "INVALID_CODE", "method": "signup"}, to=request.sid)

@socketio.on("login")
def login_handler(data: dict):
    keys: list = list(data.keys())

    if not "phone_number" in keys:
        emit("login", {"status": "INVALID_INPUT", "method": "login"}, to=request.sid)

    else:
        if not "code" in keys:
            emit("login", handler.sendCode(data.get("phone_number")), to=request.sid)
        else:
            agreed = handler.agreeCode(data.get("phone_number"), data.get("code"))
            if agreed['ok'] == True:
                emit("login", handler.loginAccount(data.get("phone_number")), to=request.sid)
            else:emit("login", {"status": "INVALID_CODE", "method": "login"}, to=request.sid)

@socketio.on("getMe")
def get_me(data: dict):
    keys: list = list(data.keys())

    if not "auth_token" in keys:
        emit("getMe", {"status": "INVALID_INPUT", "method": "getMe"}, to=request.sid)
    else:
        emit("getMe", handler.getMe(data.get("auth_token")), to=request.sid)

@socketio.on("getUserInfo")
def get_user_info(data: dict):
    keys: list = list(data.keys())

    if not "auth_token" in keys or not "target_username" in keys:
        emit("getUserInfo", {"status": "INVALID_INPUT", "method": "getUserInfo"}, to=request.sid)
    else:
        emit("getUserInfo", handler.getUserInfo(data.get("auth_token"), data.get("target_username", "")), to=request.sid)

@socketio.on("getAdmins")
def get_admins(data: dict):
    keys: list = list(data.keys())

    if not "auth_token" in keys:
        emit("getAdmins", {"status": "INVALID_INPUT", "method": "getAdmins"}, to=request.sid)
    else:
        emit("getAdmins", handler.getAdmins(data.get("auth_token")), to=request.sid)

@socketio.on("getDevs")
def get_devs(data: dict):
    keys: list = list(data.keys())

    if not "auth_token" in keys:
        emit("getDevs", {"status": "INVALID_INPUT", "method": "getDevs"}, to=request.sid)
    else:
        emit("getDevs", handler.getDevs(data.get("auth_token")), to=request.sid)

@socketio.on("editAccount")
def edit_account(data: dict):
    keys: list = list(data.keys())

    if not "auth_token" in keys:
        emit("editAccount", {"status": "INVALID_INPUT", "method": "editAccount"}, to=request.sid)
    else:
        emit(
            "editAccount",
            handler.editAccount(
                data.get("auth_token"),
                data.get("fullname", None),
                data.get("username", None),
                data.get("bio", None),
                data.get("profile", None),
                data.get("inner_gif", None),
                data.get("hide_phone_number", None),
                data.get("can_join_groups", None)
            ),
            to=request.sid
        )

@socketio.on("searchUser")
def search_user(data: dict):
    keys: list = list(data.keys())

    if not "auth_token" in keys or not "username" in keys:
        emit("searchUser", {"status": "INVALID_INPUT", "method": "searchUser"}, to=request.sid)
    else:
        emit("searchUser", handler.searchUser(data.get("auth_token"), data.get("username", "")), to=request.sid)

@socketio.on("isExistsUser")
def is_exists_user(data: dict):
    keys: list = list(data.keys())

    if not "username" in keys:
        emit("isExistsUser", {"status": "INVALID_INPUT", "method": "isExistsUser"}, to=request.sid)
    else:
        emit("isExistsUser", handler.isExistsUser(data.get("username", "")), to=request.sid)

@socketio.on("createGroup")
def create_group(data: dict):
    keys: list = list(data.keys())

    if not "auth_token" in keys or not "group_title" in keys or not "group_id" in keys:
        emit("createGroup", {"status": "INVALID_INPUT", "method": "createGroup"}, to=request.sid)
    else:
        emit(
            "createGroup",
            handler.createGroup(
                data.get("auth_token"),
                data.get("group_title"),
                data.get("group_profile", ""),
                data.get("group_caption", ""),
                data.get("group_id"),
                data.get("members", [])
            ),
            to=request.sid
        )

@socketio.on("getGroupByID")
def get_group_by_id(data: dict):
    keys: list = list(data.keys())

    if not "group_id" in keys:
        emit("getGroupByID", {"status": "INVALID_INPUT", "method": "getGroupByID"}, to=request.sid)
    else:
        emit("getGroupByID", handler.getGroupByID(data.get("group_id")), to=request.sid)

@socketio.on("getGroupByGID")
def get_group_by_gid(data: dict):
    keys: list = list(data.keys())

    if not "gid" in keys:
        emit("getGroupByGID", {"status": "INVALID_INPUT", "method": "getGroupByGID"}, to=request.sid)
    else:
        emit("getGroupByGID", handler.getGroupByGID(data.get("gid")), to=request.sid)

@socketio.on("sendGroupMessage")
def send_group_message(data: dict):
    keys: list = list(data.keys())

    if not "from_auth" in keys or not "gid" in keys or not "message" in keys:
        emit("sendGroupMessage", {"status": "INVALID_INPUT", "method": "sendGroupMessage"}, to=request.sid)
    else:
        emit(
            "sendGroupMessage",
            handler.sendGroupMessage(
                data.get("from_auth"),
                data.get("gid"),
                data.get("message"),
                data.get("timestamp", None),
                data.get("reply_data", {})
            ),
            to=request.sid
        )

@socketio.on("searchGroup")
def search_group(data: dict):
    keys: list = list(data.keys())

    if not "auth_token" in keys or not "group_id" in keys:
        emit("searchGroup", {"status": "INVALID_INPUT", "method": "searchGroup"}, to=request.sid)
    else:
        emit("searchGroup", handler.searchGroup(data.get("auth_token"), data.get("group_id", "")), to=request.sid)

@socketio.on("addAdmin")
def add_admin(data: dict):
    keys: list = list(data.keys())

    if not "auth_token" in keys or not "member_user_id" in keys or not "group_id" in keys:
        emit("addAdmin", {"status": "INVALID_INPUT", "method": "addAdmin"}, to=request.sid)
    else:
        emit(
            "addAdmin",
            handler.addAdmin(
                data.get("auth_token"),
                data.get("member_user_id"),
                data.get("group_id")
            ),
            to=request.sid
        )

@socketio.on("removeAdmin")
def remove_admin(data: dict):
    keys: list = list(data.keys())

    if not "auth_token" in keys or not "member_user_id" in keys or not "group_id" in keys:
        emit("removeAdmin", {"status": "INVALID_INPUT", "method": "removeAdmin"}, to=request.sid)
    else:
        emit(
            "removeAdmin",
            handler.removeAdmin(
                data.get("auth_token"),
                data.get("member_user_id"),
                data.get("group_id")
            ),
            to=request.sid
        )

@socketio.on("addMemberToGroup")
def add_member_to_group(data: dict):
    keys: list = list(data.keys())

    if not "auth_token" in keys or not "user_id" in keys or not "group_id" in keys:
        emit("addMemberToGroup", {"status": "INVALID_INPUT", "method": "addMemberToGroup"}, to=request.sid)
    else:
        emit(
            "addMemberToGroup",
            handler.addMemberToGroup(
                data.get("auth_token"),
                data.get("group_id"),
                data.get("user_id")
            ),
            to=request.sid
        )

@socketio.on("getGroupMembersByID")
def get_group_members_by_id(data: dict):
    keys: list = list(data.keys())

    if not "auth_token" in keys or not "group_id" in keys:
        emit("getGroupMembersByID", {"status": "INVALID_INPUT", "method": "getGroupMembersByID"}, to=request.sid)
    else:
        emit("getGroupMembersByID", handler.getGroupMembersByID(data.get("auth_token"), data.get("group_id")), to=request.sid)

@socketio.on("getGroupMembersByGID")
def get_group_members_by_gid(data: dict):
    keys: list = list(data.keys())

    if not "auth_token" in keys or not "gid" in keys:
        emit("getGroupMembersByGID", {"status": "INVALID_INPUT", "method": "getGroupMembersByGID"}, to=request.sid)
    else:
        emit("getGroupMembersByGID", handler.getGroupMembersByGID(data.get("auth_token"), data.get("gid")), to=request.sid)

@socketio.on("removeMemberFromGroup")
def get_group_members_by_id(data: dict):
    keys: list = list(data.keys())

    if not "auth_token" in keys or not "group_id" in keys or not "member_user_id" in keys:
        emit("removeMemberFromGroup", {"status": "INVALID_INPUT", "method": "removeMemberFromGroup"}, to=request.sid)
    else:
        emit("removeMemberFromGroup", handler.removeMemberFromGroup(data.get("auth_token"), data.get("member_user_id"), data.get("group_id")), to=request.sid)


@socketio.on("pinMessage")
def pin_message(data: dict):
    keys: list = list(data.keys())

    if not "auth_token" in keys or not "message_id" in keys or not "group_id" in keys:
        emit("pinMessage", {"status": "INVALID_INPUT", "method": "pinMessage"}, to=request.sid)
    else:
        emit(
            "pinMessage",
            handler.pinMessage(
                data.get("auth_token"),
                data.get("message_id"),
                data.get("group_id")
            ),
            to=request.sid
        )

@socketio.on("clearPin")
def clear_pin(data: dict):
    keys: list = list(data.keys())

    if not "auth_token" in keys or not "group_id" in keys:
        emit("clearPin", {"status": "INVALID_INPUT", "method": "clearPin"}, to=request.sid)
    else:
        emit(
            "clearPin",
            handler.clearPin(
                data.get("auth_token"),
                data.get("group_id")
            ),
            to=request.sid
        )

@socketio.on("lockGroup")
def lock_group(data: dict):
    keys: list = list(data.keys())

    if not "auth_token" in keys or not "group_id" in keys:
        emit("lockGroup", {"status": "INVALID_INPUT", "method": "lockGroup"}, to=request.sid)
    else:
        emit(
            "lockGroup",
            handler.lockGroup(
                data.get("auth_token"),
                data.get("group_id")
            ),
            to=request.sid
        )

@socketio.on("unlockGroup")
def unlock_group(data: dict):
    keys: list = list(data.keys())

    if not "auth_token" in keys or not "group_id" in keys:
        emit("unlockGroup", {"status": "INVALID_INPUT", "method": "unlockGroup"}, to=request.sid)
    else:
        emit(
            "unlockGroup",
            handler.unlockGroup(
                data.get("auth_token"),
                data.get("group_id")
            ),
            to=request.sid
        )

@socketio.on("getGroupMessages")
def get_group_messages(data: dict):
    keys: list = list(data.keys())

    if not "auth_token" in keys or not "group_id" in keys:
        emit("getGroupMessages", {"status": "INVALID_INPUT", "method": "getGroupMessages"}, to=request.sid)
    else:
        emit(
            "getGroupMessages",
            handler.getGroupMessages(
                data.get("auth_token"),
                data.get("group_id")
            ),
            to=request.sid
        )

@socketio.on("getGroupAdmins")
def get_group_admins(data: dict):
    keys: list = list(data.keys())

    if not "group_id" in keys:
        emit("getGroupAdmins", {"status": "INVALID_INPUT", "method": "getGroupAdmins"}, to=request.sid)
    else:
        emit(
            "getGroupAdmins",
            handler.getGroupAdmins(
                data.get("group_id")
            ),
            to=request.sid
        )

@socketio.on("editGroupMessage")
def edit_group_message(data: dict):
    keys: list = list(data.keys())

    if not "from_auth" in keys or not "group_id" in keys or not "new_message" \
    in keys or not "message_id" in keys:
        emit("editGroupMessage", {"status": "INVALID_INPUT", "method": "editGroupMessage"}, to=request.sid)
    else:
        emit(
            "editGroupMessage",
            handler.editGroupMessage(
                data.get("from_auth"),
                data.get("group_id"),
                data.get("message_id"),
                data.get("new_message")
            ),
            to=request.sid
        )

@socketio.on("getGroupsOfUser")
def get_groups_of_user(data: dict):
    keys: list = list(data.keys())

    if not "auth_token" in keys:
        emit("getGroupsOfUser", {"status": "INVALID_INPUT", "method": "getGroupsOfUser"}, to=request.sid)
    else:
        emit("getGroupsOfUser", handler.getUserGroups(data.get("auth_token")), to=request.sid)

@socketio.on("leaveGroup")
def leave_group(data: dict):
    keys: list = list(data.keys())

    if not "auth_token" in keys or not "group_id" in keys:
        emit("leaveGroup", {"status": "INVALID_INPUT", "method": "leaveGroup"}, to=request.sid)
    else:
        emit(
            "leaveGroup",
            handler.leaveGroup(
                data.get("auth_token"),
                data.get("group_id")
            ),
            to=request.sid
        )

@socketio.on("joinGroup")
def join_group(data: dict):
    keys: list = list(data.keys())

    if not "auth_token" in keys or not "group_id" in keys:
        emit("joinGroup", {"status": "INVALID_INPUT", "method": "joinGroup"}, to=request.sid)
    else:
        emit(
            "joinGroup",
            handler.joinGroup(
                data.get("auth_token"),
                data.get("group_id")
            ),
            to=request.sid
        )

@socketio.on("addIndex")
def add_index(data: dict):
    keys: list = list(data.keys())

    if not "user_id" in keys:
        emit("addIndex", {"status": "INVALID_INPUT", "method": "addIndex"}, to=request.sid)
    else:
        emit(
            "addIndex",
            handler.addIndex(data.get("user_id")),
            to=request.sid
        )

@socketio.on("sendPrivateMessage")
def send_private_message(data: dict):
    keys: list = list(data.keys())

    if not "from_auth" in keys or not "to_user_id" in keys or not "message" in \
    keys:
        emit("sendPrivateMessage", {"status": "INVALID_INPUT", "method": "sendPrivateMessage"}, to=request.sid)
    else:
        emit(
            "sendPrivateMessage",
            handler.sendPrivateMessage(
                data.get("from_auth"),
                data.get("to_user_id"),
                data.get("message"),
                data.get("timestamp", None),
                data.get("reply_data", {})
            ),
            to=request.sid
        )

@socketio.on("getPrivateMessageByID")
def get_private_message_by_id(data: dict):
    keys: list = list(data.keys())

    if not "user_id" in keys or not "message_id" in keys:
        emit("getPrivateMessageByID", {"status": "INVALID_INPUT", "method": "getPrivateMessageByID"}, to=request.sid)
    else:
        emit(
            "getPrivateMessageByID",
            handler.getPrivateMessageByID(
                data.get("user_id"),
                data.get("message_id")
            ),
            to=request.sid
        )

@socketio.on("getPrivateMessageByUserID")
def get_private_message_by_user_id(data: dict):
    keys: list = list(data.keys())

    if not "user_id" in keys or not "message_id" in keys:
        emit("getPrivateMessageByUserID", {"status": "INVALID_INPUT", "method": "getPrivateMessageByUserID"}, to=request.sid)
    else:
        emit(
            "getPrivateMessageByUserID",
            handler.getPrivateMessageByUserID(
                data.get("user_id"),
                data.get("message_id")
            ),
            to=request.sid
        )

@socketio.on("editPrivateMessage")
def edit_private_message(data: dict):
    keys: list = list(data.keys())

    if not "from_auth_token" in keys or not "message_id" in keys or not "new_message" in keys:
        emit("editPrivateMessage", {"status": "INVALID_INPUT", "method": "editPrivateMessage"}, to=request.sid)
    else:
        emit(
            "editPrivateMessage",
            handler.editPrivateMessage(
                data.get("from_auth_token"),
                data.get("message_id"),
                data.get("new_message")
            ),
            to=request.sid
        )

@socketio.on("markMessageAsRead")
def edit_private_message(data: dict):
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
