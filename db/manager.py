import json
import secrets
import random
import requests
import sqlite3
import time

class UserManager(object):
    def __init__(self):
        self.users_dbs = 'data/users.db'
        self.user_conn = sqlite3.connect(self.users_dbs, check_same_thread=False)
        self.create_table()
        self.lisence = "e765defd954e1e682c81ab4956f5df00"
        self.reflex_api = f"http://api-free.ir/api2/very?token={self.lisence}&phone="
        self.points = ["user", "admin", "dev"]
        self.private_manager = PrivateManager(self)

    def sendCode(self, phone: str):
        try:
            data = requests.post(self.reflex_api + phone)
            data = data.json()
            data['error'] = False
            return data
        except Exception as ERROR_CONNECTION:
            return {
                "error": True,
                "message": str(ERROR_CONNECTION)
            }

    def agreeCode(self, phone: str, code: str):
        try:
            data = requests.post(self.reflex_api + phone + "&code=" + code).json()
            data['error'] = False
            return data
        except Exception as ERROR_CONNECTION:
            return {
                "error": True,
                "message": str(ERROR_CONNECTION)
            }

    def create_user_id(self) -> str:
        return str(random.randint(10000, 9999999999))

    def create_table(self):
        self.user_conn.execute("CREATE TABLE IF NOT EXISTS users ( user_id TEXT PRIMARY KEY, user_data TEXT )")

    def trim_phone_number(self, phone_number: str) -> str:
        num = str(phone_number).strip()

        if num.startswith("0"): num = num[1:]
        elif num.startswith("98"): num = num[2:]
        elif num.startswith("+98"): num = num[3:]
        else: num = num

        return "0" + num

    def getUsers(self) -> list:
        users = self.user_conn.execute("SELECT * FROM users")
        return users.fetchall()

    def getUserByPhone(self, phone_number: str) -> dict:
        phone = self.trim_phone_number(phone_number)
        for user in self.getUsers():
            user = json.loads(user[1])
            if user['phone'] == phone:
                return {"status": "OK", "user": user}
        
        return {"status": "UNREACHABLE_PHONE", "user": {}}

    def getUserByUName(self, uname: str) -> dict:
        for user in self.getUsers():
            user = json.loads(user[1])
            if user['username'] == uname:
                return {"status": "OK", "user": user}
        
        return {"status": "UNREACHABLE_UNAME", "user": {}}
    
    def getUserByAuth(self, token: str) -> dict:
        for user in self.getUsers():
            user = json.loads(user[1])
            if user['token'] == token:
                return {"status": "OK", "user": user}
        
        return {"status": "UNREACHABLE_TOKEN", "user": {}}
    
    def getUserByUserID(self, user_id: str) -> dict:
        for user in self.getUsers():
            user = json.loads(user[1])
            if user['user_id'] == user_id:
                return {"status": "OK", "user": user}
        
        return {"status": "UNREACHABLE_USER_ID", "user": {}}
    
    def getAdmins(self) -> dict:
        admins = []
        for user in self.getUsers():
            user = json.loads(user[1])
            if user['point'] == "admin":
                admins.append(user)
        
        return {"status": "OK", "users": admins}

    def getDevs(self) -> dict:
        devs = []
        for user in self.getUsers():
            user = json.loads(user[1])
            if user['point'] == "dev":
                devs.append(user)
        
        return {"status": "OK", "users": devs}

    def addUser(self, username: str, phone: str, fullname: str, bio: str = "", profile: str = None):
        default_profile = 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRFEZSqk8dJbB0Xc-fr6AWv2aocxDdFpN6maQ&'

        if profile is None or profile.strip() == '':
            profile = default_profile

        isexists_phone = self.getUserByPhone(phone)
        isexists_uname = self.getUserByUName(username)
        
        if not isexists_phone['status'] == "OK":
            if not isexists_uname['status'] == "OK":

                auth_token = self.generate_auth_token()
                user_id = self.create_user_id()
                user_data  = {
                    "phone": self.trim_phone_number(phone),
                    "username": username,
                    "fullname": fullname.strip(),
                    "bio": bio,
                    "profile": profile,
                    "token": auth_token,
                    "user_id": user_id,
                    "status": "online",
                    "point": "user",
                    "is_suspension": False,
                    "settings": {
                        "hide_phone_number": True,
                        "can_join_groups": True,
                        "inner_gif": None
                    }
                }

                self.user_conn.execute("INSERT INTO users (user_id, user_data) VALUES (?, ?)", (user_id, json.dumps(user_data)))
                self.user_conn.commit()

                self.private_manager.addIndex(user_id)

                return {
                    'status': 'OK',
                    'user': user_data
                }

            else: return {
                'status': 'EXISTS_USERNAME'
            }

        else: return {
            "status": "EXISTS_PHONE"
        }

    def suspensionUser(self, auth_token: str):
        verify_user = self.getUserByAuth(auth_token)
        ghostly = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQT6T83Gykijshi_fAb3q1piW3LJ5i0eXkK4w&s"

        if verify_user['status'] == "OK":
            verify_user['user']['is_suspension'] = True
            verify_user['user']['fullname'] = "suspension account".title()
            verify_user['user']['profile'] = ghostly

            self.user_conn.execute("UPDATE users SET user_data WHERE user_id = ?", (json.dumps(verify_user['user']), verify_user['user']['user_id']))
            self.user_conn.commit()

            return {"status": "OK", "user": verify_user['user']}
        else:return {"status": "INVALID_TOKEN", "user": {}}


    def update_user_profile(
            self,
            auth_token: str,

            fullname: str = None,
            username: str = None,
            bio: str = None, 
            profile: str = None,

            inner_gif: str = None,
            hide_phone_number: bool = None,
            can_join_groups: bool = None,
            can_see_profiles: bool = None,
        ):

        verify = self.getUserByAuth(auth_token)
        verify_username = self.getUserByUName(username)
        
        if verify['status'] == "OK":
            if verify_username['status'] == "OK":
                return {"status": "EXISTS_USERNAME", "user": {}}
            else:
                
                user_data = {
                    "phone": verify['user']['phone'],
                    "username": username if not username is None else verify['user']['username'],
                    "fullname": fullname if not fullname is None else verify['user']['fullname'],
                    "bio": bio if not bio is None else verify['user']['bio'],
                    "profile": profile if not profile is None else verify['user']['phone'],
                    "token": auth_token,
                    "user_id": verify['user']['user_id'],
                    "status": "online",
                    "point": "user",
                    "settings": {
                        "hide_phone_number": hide_phone_number if not hide_phone_number is None else verify['user']['settings']['hide_phone_number'],
                        "can_join_groups": can_join_groups if not can_join_groups is None else verify['user']['settings']['can_join_groups'],
                        "can_see_profiles": can_see_profiles if not can_see_profiles is None else verify['user']['settings']['can_see_profiles'],
                        "inner_gif": inner_gif if not inner_gif is None else verify['user']['settings']['inner_gif']
                    }
                }

                self.user_conn.execute("UPDATE users SET user_data = ? WHERE user_id = ?", (json.dumps(user_data), verify['user']['user_id']))
                self.user_conn.commit()

                return {"status": "OK", "user": user_data}
            
        else:return {'status': 'TOKEN_INVALID | NOT_FOUND', 'user': {}}

    def change_point(self, auth: str, mode: str):
        verify = self.getUserByAuth(auth)
        mode = mode if mode in self.points else "user"

        if verify['status'] == "OK":

            verify['user']['point'] = mode

            self.user_conn.execute("UPDATE users SET user_data = ? WHERE user_id = ?", (json.dumps(verify['user']), verify['user']['user_id']))
            self.user_conn.commit()

            return {"status": "OK", "current_point": mode, "user": verify['user']}
        
        else:return {'status': 'TOKEN_INVALID | NOT_FOUND', 'user': {}}
    
            
    def online(self, username, auth_token, status = 'offline'):
            user = self.getUserByAuth(auth_token)
            if user['status'] == "OK":
                user['user']['status'] = status
                self.user_conn.execute("UPDATE users SET user_data = ? WHERE user_id = ?", (json.dumps(user['user']), user['user']['user_id']))
                self.user_conn.commit()

                return {"status": "OK", "user": user}
            else:return {"status": "NOT_FOUND", "user": {}}

    def authenticate_user(self, username, auth_token):
        user = self.getUserByUName(username)
        if user['status'] == "OK":
            if user['user']['token'] == auth_token:
                return {'status': 'OK', 'user': user['user']}
            else:
                return {'status': 'TOKEN_INVALID', 'user': {}}
        else:
            return {'status': 'NOT_FOUND', 'user': {}}

    def login(self, phone_number: str):
        user = self.getUserByPhone(phone_number)
        if user['status'] == "OK":
            return user
        else:
            return {'status': 'NOT_FOUND', 'user': {}}
    
    def getUsernameByID(self, auth_token, getUser):
        user = self.getUserByAuth(auth_token=auth_token)
        if user['status'] == 'OK':
            guser = self.getUserByUName(getUser)
            if guser['status']:
                user = guser['user']
                return {'status': 'OK', 'user': {'fullname': user['fullname'], 'bio': user['bio'], 'username': getUser, 'profile': user['profile'], 'status': user['status'], 'point': user['point'], 'settings': user['settings']}}
            else:
                return {'status': 'USER_NOT_FOUND', 'user': {}}
        else:
            return {'status': 'TOKEN_INVALID | NOT_FOUND', 'user': {}}

    def generate_auth_token(self):
        return secrets.token_urlsafe()

    def user_exists(self, username) -> bool:
        verify = self.getUserByUName(username)
        if verify['status'] == "OK":return True
        else:return False

    def searchUser(self, username: str) -> dict:
        users = self.getUsers()
        finded_users = []

        for user in users:
            user = json.loads(user[1])
            if user['username'] == username or user['username'].startswith(username):
                if user['settings']['hide_phone_number']:del user['phone']

                finded_users.append(user)

        return {"status": "OK", "users": finded_users}


class GroupManager(object):
    def __init__(self, user_manager: UserManager):
        self.user_manager = user_manager
        self.group_conn = sqlite3.connect("data/groups.db", check_same_thread=False)
        self.default_group_profile = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRGqisajcuqgEBg05gUKz5MX3k6CFQoXThhde0LECDOocysVuSAFFh5hECH4cLVyCpM7pM&usqp=CAU"
        self.create_table()

    def create_group_id(self) -> str:
        return f"-{str(random.randint(1000000000, 9999999999999))}"

    def create_table(self):
        self.group_conn.execute("CREATE TABLE IF NOT EXISTS groups ( group_id TEXT PRIMARY KEY, group_data )")

    def create_message_id(self) -> str:
        return str(random.randint(100000000, 9999999999999))

    def addGroup(
            self,
            auth_token: str,
            group_title: str,
            group_profile: str = "",
            group_caption: str = "",
            group_id: str = None,
            members: str = []
    ):
        
        verify = self.user_manager.getUserByAuth(auth_token)
        verify_group = self.getGroupByID(group_id)

        if verify['status'] == "OK":
            if verify_group['status'] == "OK":
                return {"status": "EXISTS_ID", "group": {}}
            else:

                finally_users = []

                for member in members:
                    ver_user = self.user_manager.getUserByUserID(member)
                    if ver_user['status'] == "OK":
                        if ver_user['user']['settings']['can_join_groups']:finally_users.append(member)

                finally_users.append(verify['user']['user_id'])

                gid = self.create_group_id()
                group_data = {
                    "group_title": group_title.strip(),
                    "group_caption": group_caption.strip(),
                    "group_id": group_id.strip(),
                    "gid": gid,
                    "group_profile": group_profile if not group_profile is None else self.default_group_profile,
                    "created_at": time.ctime(time.time()),
                    "owner": verify['user']['user_id'],
                    "admins": [verify['user']['user_id']],
                    "members": finally_users,
                    "messages": [],
                    "last_message": {},
                    "pinned_message": {},
                    "allow_to_send_messages": True
                }

                self.group_conn.execute("INSERT INTO groups (group_id, group_data) VALUES (?, ?)", (gid, json.dumps(group_data)))
                self.group_conn.commit()

                return {"status": "OK", "group": group_data}
            
        else:return {"status": "INVALID_TOKEN", "group": {}}

    def getGroups(self) -> list:
        grps = self.group_conn.execute("SELECT * FROM groups")
        return grps.fetchall()

    def getGroupByID(self, group_id: str):
        groups = self.getGroups()

        for group in groups:
            group = json.loads(group[1])
            if group['group_id'] == group_id:
                return {"status": "OK", "group": group}
            
        return {"status": "INVALID_ID", "group": {}}

    def getGroupByGID(self, gid: str):
        groups = self.getGroups()

        for group in groups:
            group = json.loads(group[1])
            if group['gid'] == gid:
                return {"status": "OK", "group": group}
            
        return {"status": "INVALID_ID", "group": {}}

    def getAnyMessages(self) -> list:
        groups = self.getGroups()
        messages = []

        for group in groups:
            group = json.loads(group[1])

            for message in group['messages']:
                messages.append({message['message_id']: message})
        
        return messages
    
    def getMessageByID(self, message_id: str) -> dict:
        messages = self.getAnyMessages()

        for message in messages:
            if message_id in list(message.keys()):
                return {"status": "OK", "message": message}
        
        return {"status": "UNREACHABLE_MESSAGE_ID", "message": {}}

    def addGroupMessage(
            self,
            from_auth: str,
            gid: str,
            message: str,
            timestamp: str = None,
            reply_data: dict = None
    ):
        verify_user = self.user_manager.getUserByAuth(from_auth)
        verify_group = self.getGroupByGID(gid)

        timestamp = timestamp if not timestamp is None else time.strftime("%H:%M")
        message = message.strip()

        if verify_user['status'] == "OK":
            if verify_group['status'] == "OK":
                if not verify_user['user']['username'] in verify_group['group']['admins']:
                    if verify_group['group']['allow_to_send_messages']:
                        message_data = {
                            "from_user": verify_user['user']['username'],
                            "gid": gid,
                            "group_title": verify_group['group']['group_title'],
                            "group_id": verify_group['group']['group_id'],
                            "message": message,
                            "timestamp": timestamp,
                            "message_id": self.create_message_id(),
                            "is_edit": False
                        }

                        if not reply_data is None:
                            message_data['reply_to_message'] = {}
                            message_data['reply_to_message']['from_user'] = reply_data.get("from_user", "").strip()
                            message_data['reply_to_message']['message_id'] = reply_data.get("message_id", "").strip()
                            message_data['reply_to_message']['message'] = reply_data.get("message", "").strip()
                            message_data['reply_to_message']['timestamp'] = reply_data.get("timestamp", "").strip()
                        else:message_data['reply_to_message'] = {}

                        verify_group['group']['messages'].append(message_data)
                        verify_group['group']['last_message'] = message_data

                        self.group_conn.execute("UPDATE groups SET group_data = ? WHERE group_id = ?", (json.dumps(verify_group['group']), gid))
                        self.group_conn.commit()

                        return {"status": "OK", "message": message_data}
                    
                    else:return {"status": "JUST_ADMINS_ACCESSED", "message": {}}

                else:
                    message_data = {
                        "from_user": verify_user['user']['username'],
                        "gid": gid,
                        "group_title": verify_group['group']['group_title'],
                        "group_id": verify_group['group']['group_id'],
                        "message": message,
                        "timestamp": timestamp,
                        "message_id": self.create_message_id(),
                        "is_edit": False
                    }

                    if not reply_data is None:
                        message_data['reply_to_message'] = {}
                        message_data['reply_to_message']['from_user'] = reply_data.get("from_user", "").strip()
                        message_data['reply_to_message']['message_id'] = reply_data.get("message_id", "").strip()
                        message_data['reply_to_message']['message'] = reply_data.get("message", "").strip()
                        message_data['reply_to_message']['timestamp'] = reply_data.get("timestamp", "").strip()
                    else:message_data['reply_to_message'] = {}

                    verify_group['group']['messages'].append(message_data)
                    verify_group['group']['last_message'] = message_data

                    self.group_conn.execute("UPDATE groups SET group_data = ? WHERE group_id = ?", (json.dumps(verify_group['group']), gid))
                    self.group_conn.commit()

                    return {"status": "OK", "message": message_data}
                
            else:return {"status": "INVALID_GID", "message": {}}
        else:return {"status": "NOT_FOUND", "message": {}} 

    def searchGroup(self, group_id: str):
        groups = self.getGroups()
        finded_groups = []

        for group in groups:
            group = json.loads(group[1])['group']
            if group['group_id'] == group_id or group['group_id'].startswith(group_id):
                finded_groups.append(group)
            
        return {"status": "OK", "groups": finded_groups}
    
    def addAdmin(self, auth_token: str, member_user_id: str, group_id: str):
        owner_veri = self.user_manager.getUserByAuth(auth_token)
        membr_veri = self.user_manager.getUserByUserID(member_user_id)
        group_veri = self.getGroupByID(group_id)

        if owner_veri['status'] == "OK":
            if membr_veri['status'] == "OK":
                if group_veri['status'] == "OK":
                    if owner_veri['user']['username'] == group_veri['group']['owner']:
                        if member_user_id in group_veri['group']['members']:
                            if not member_user_id in group_veri['group']['admins']:
                                group_veri['group']['admins'].append(member_user_id)
                                self.group_conn.execute("UPDATE groups SET group_data = ? WHERE group_id = ?", (json.dumps(group_veri['group']), group_veri['group']['gid']))
                                self.group_conn.commit()
                                return {"status": "OK", "admins": group_veri['group']['admins']}
                            else:return {"status": "ADMINS_EXISTS"}
                        else:return {"status": "MEMBER_NOT_FOUND"}
                    else:return {"status": "OWNER_NOT_FOUND"}
                else:return {"status": "INVALID_GROUP_ID"}
            else:return {"status": "USER_NOT_FOUND"}
        else:return {"status": "USER_NOT_FOUND"}

    def removeAdmin(self, auth_token: str, admin_user_id: str, group_id: str):
        owner_veri = self.user_manager.getUserByAuth(auth_token)
        membr_veri = self.user_manager.getUserByUserID(admin_user_id)
        group_veri = self.getGroupByID(group_id)

        if owner_veri['status'] == "OK":
            if membr_veri['status'] == "OK":
                if group_veri['status'] == "OK":
                    if owner_veri['user']['username'] == group_veri['group']['owner']:
                        if admin_user_id in group_veri['group']['members']:
                            if admin_user_id in group_veri['group']['admins']:
                                group_veri['group']['admins'].remove(admin_user_id)
                                self.group_conn.execute("UPDATE groups SET group_data = ? WHERE group_id = ?", (json.dumps(group_veri['group']), group_veri['group']['gid']))
                                self.group_conn.commit()
                                return {"status": "OK", "admins": group_veri['group']['admins']}
                            else:return {"status": "MEMBER_IS_NOT_ADMIN"}
                        else:return {"status": "MEMBER_NOT_FOUND"}
                    else:return {"status": "OWNER_NOT_FOUND"}
                else:return {"status": "INVALID_GROUP_ID"}
            else:return {"status": "USER_NOT_FOUND"}
        else:return {"status": "USER_NOT_FOUND"}

    def addMemberToGroup(self, auth_token: str, group_id: str, user_id: str):
        v = self.user_manager.getUserByAuth(auth_token)
        verify_user = self.user_manager.getUserByUserID(user_id)
        verify_group = self.getGroupByID(group_id)

        if v['status'] == "OK":
            if verify_user['status'] == "OK":
                if verify_group['status'] == "OK":
                    if verify_user['user']['settings']['can_join_groups']:
                        if not verify_user['user']['username'] in verify_group['group']['members']:
                            verify_group['group']['members'].append(user_id)
                            self.group_conn.execute("UPDATE groups SET group_data = ? WHERE group_id = ?", (json.dumps(verify_group['group']), verify_group['group']['gid']))
                            self.group_conn.commit()
                            return {"status": "OK", "members": verify_group['group']['members']}
                        else:return {"status": "EXISTS_MEMBER"}
                    else:return {"statis": "UNAVAILABLE_ACTION", "members": verify_group['group']['members']}
                else:return {"status": "INVALID_GROUP_ID"}
            else:return {"status": "INVALID_USERNAME"}
        else:return {"status": "INVALID_TOKEN"}

    def getGroupMembersByID(self, auth_token: str, group_id: str) -> dict:
        verify_group = self.getGroupByID(group_id)
        v = self.user_manager.getUserByAuth(auth_token)

        if v['status'] == "OK":

            if verify_group['status'] == "OK":
                if v['user']['user_id'] in verify_group['group']['members']:
                    return {"status": "OK", "members": verify_group['group']['members']}
                else:return {"status": "AUTH_DOESNT_IN_GROUP"}
            else:return {"status": "INVALID_GROUP_ID", "members": []}
        else:return {'status': "INVALID_TOKEN"}

    def getGroupMembersByGID(self, auth_token: str, gid: str) -> dict:
        v = self.user_manager.getUserByAuth(auth_token)
        verify_group = self.getGroupByGID(gid)

        if v['status'] == "OK":

            if verify_group['status'] == "OK":
                if v['user']['user_id'] in verify_group['group']['members']:
                    return {"status": "OK", "members": verify_group['group']['members']}
                else:return {"status": "AUTH_DOESNT_IN_GROUP"}
            else:return {"status": "INVALID_GID", "members": []}
        
        else:return {"status": "INVALID_TOKEN"}

    def removeMemberFromGroup(self, auth_token: str, member_user_id: str, group_id: str):
        v = self.user_manager.getUserByAuth(auth_token)
        vm = self.user_manager.getUserByUserID(member_user_id)
        vg = self.getGroupByID(group_id)

        if v['status'] == "OK":
            if vm['status'] == "OK":
                if vg['status'] == "OK":
                    if member_user_id in vg['group']['members']:
                        if not member_user_id == v['user']['user_id']:
                            if v["user"]['user_id'] in vg['group']['admins']:
                                vg['group']['members'].remove(member_user_id)
                                self.group_conn.execute("UPDATE groups SET group_data = ? WHERE group_id = ?", (json.dumps(vg['group']), vg['group']['gid']))
                                self.group_conn.commit()
                                return {"status": "OK", "members": vg['group']['members']}
                            else:return {"status": "TOKEN_IS_NOT_ADMIN"}
                        else:return {"status": "CANNOT_REMOVE_OWNER"}
                    else:return {"status": "MEMBER_NOT_FOUND"}
                else:return {"status": "INVALID_GROUP_ID"}
            else:return {"status": "INVALID_USER"}
        else:return {"status": "INVALID_TOKEN"}

    def pinMessage(self, auth_token: str, message_id: str, group_id: str):
        verify_user = self.user_manager.getUserByAuth(auth_token)
        verify_group = self.getGroupByID(group_id)
        verify_message = self.getMessageByID(message_id)

        if verify_user['status'] == "OK":
            if verify_group['status'] == "OK":
                if verify_message['status'] == "OK":
                    if verify_user['user']['user_id'] in verify_group['group']['admins']:
                        verify_group['group']['pinned_message'] = verify_message['message'][message_id]
                        self.group_conn.execute("UPDATE groups SET group_data = ? WHERE group_id = ?", (json.dumps(verify_group['group']), verify_group['group']['gid']))
                        self.group_conn.commit()
                        return {"status": "OK", "message": verify_message["message"][message_id]}
                    else:return {"status": "ACCESS_DENIED"}
                else:return {"status": "UNREACHABLE_MESSAGE_ID"}
            else:return {"status": "INVALID_GROUP_ID"}
        else:return {"status": "INVALID_TOKEN"}

    def clearPin(self, auth_token: str, group_id: str):
        verify_user = self.user_manager.getUserByAuth(auth_token)
        verify_group = self.getGroupByID(group_id)

        if verify_user['status'] == "OK":
            if verify_group['status'] == "OK":
                if verify_user['user']['user_id'] in verify_group['group']['admins']:
                    verify_group['group']['pinned_message'] = {}
                    self.group_conn.execute("UPDATE groups SET group_data = ? WHERE group_id = ?", (json.dumps(verify_group['group']), verify_group['group']['gid']))
                    self.group_conn.commit()
                    return {"status": "OK"}
                else:return {"status": "ACCESS_DENIED"}
            else:return {"status": "INVALID_GROUP_ID"}
        else:return {"status": "INVALID_TOKEN"}

    def lockGroup(self, auth_token: str, group_id: str):
        verify_user = self.user_manager.getUserByAuth(auth_token)
        verify_group = self.getGroupByID(group_id)

        if verify_user['status'] == "OK":
            if verify_group['status'] == "OK":
                if verify_user['user']['user_id'] in verify_group['group']['admins']:
                    if not verify_group["group"]['allow_to_send_messages'] == False:
                        verify_group['group']['allow_to_send_messages'] = False
                        self.group_conn.execute("UPDATE groups SET group_data = ? WHERE group_id = ?", (json.dumps(verify_group['group']), verify_group['group']['gid']))
                        self.group_conn.commit()
                        return {"status": "OK"}
                    else:return {"status": "GROUP_ALREADY_LOCK"}
                else:return {"status": "ACCESS_DENIED"}
            else:return {"status": "INVALID_GROUP_ID"}
        else:return {"status": "INVALID_TOKEN"}

    def unlockGroup(self, auth_token: str, group_id: str):
        verify_user = self.user_manager.getUserByAuth(auth_token)
        verify_group = self.getGroupByID(group_id)

        if verify_user['status'] == "OK":
            if verify_group['status'] == "OK":
                if verify_user['user']['user_id'] in verify_group['group']['admins']:
                    if not verify_group["group"]['allow_to_send_messages'] == True:
                        verify_group['group']['allow_to_send_messages'] = True
                        self.group_conn.execute("UPDATE groups SET group_data = ? WHERE group_id = ?", (json.dumps(verify_group['group']), verify_group['group']['gid']))
                        self.group_conn.commit()
                        return {"status": "OK"}
                    else:return {"status": "GROUP_ALREADY_UNLOCK"}
                else:return {"status": "ACCESS_DENIED"}
            else:return {"status": "INVALID_GROUP_ID"}
        else:return {"status": "INVALID_TOKEN"}

    def getGroupMessages(self, group_id: str):
        verify = self.getGroupByID(group_id)

        if verify['status'] == "OK":return {"status": "OK", "messages": verify['group']['messages'], "last_message": verify['group']['last_message']}
        else:return {"status": "INVALID_GROUP_ID", "messages": [], "last_message": {}}

    def getGroupAdmins(self, group_id: str):
        verify = self.getGroupByID(group_id)

        if verify['status'] == "OK":return {"status": "OK", "admins": verify['group']['admins']}
        else:return {"status": "INVALID_GROUP_ID", "admins": []}

    def getMessageIDByGroupID(self, group_id: str, message_id: str):
        verify_group = self.getGroupByID(group_id)
        verify_message = self.getMessageByID(message_id)

        if verify_group['status'] == "OK":
            if verify_message['status'] == "OK":
                messages = self.getGroupMessages(group_id)

                for message in messages['messages']:
                    if message['message_id'] == message_id:
                        return {"status": "OK", "message": message, "group": verify_group['group']}
                    
                return {"status": "UNREACHABLE_MESSAGE_ID"}
            else:return {"status": "INVALID_MESSAGE_ID"}
        else:return {"status": "INVALID_GROUP_ID"}

    def editMessage(
            self,
            from_auth: str,
            group_id: str,
            message_id: str,
            new_message: str
    ):
        new_message = new_message.strip()

        verify_user: dict = self.user_manager.getUserByAuth(from_auth)
        verify_group_msg: dict = self.getMessageIDByGroupID(group_id, message_id)

        if verify_user['status'] == "OK":
            if verify_group_msg['status'] == "OK":
                if verify_group_msg['message']['from_user'] == verify_user['user']['username']:
                    messages = list(verify_group_msg['group']['messages'])
                    msg_index = messages.index(verify_group_msg['message'])
                    messages.remove(verify_group_msg['message'])
                    verify_group_msg['message']['message'] = new_message
                    verify_group_msg['message']['is_edit'] = True
                    messages.insert(msg_index, verify_group_msg['message'])
                    self.group_conn.execute("UPDATE groups SET group_data = ? WHERE group_id = ?", (json.dumps(verify_group_msg['group']), verify_group_msg['group']['gid']))
                    self.group_conn.commit()
                    return {"status": "OK", "group_messages": messages}
                else:return {"status": "NOT_OWNED_MESSAGE"}
            else:return {"status": verify_group_msg['status']}
        else:return {"status": verify_user['status']}

    def getGroupUserExists(self, auth_token: str) -> dict:
        verify_user = self.user_manager.getUserByAuth(auth_token)
        injoined_groups = []

        if verify_user['status'] == "OK":
            groups = self.getGroups()

            for group in groups:
                if verify_user['user']['user_id'] in group['members']:
                    injoined_groups.append(group)

            return {"status": "OK", "groups": injoined_groups}
        else:return {"status": verify_user['status']}

    def leaveGroup(
            self,
            auth_token: str,
            group_id: str
    ):
        verify_user = self.user_manager.getUserByAuth(auth_token)
        verify_group = self.getGroupByID(group_id)

        if verify_user['status'] == "OK":
            if verify_group['status'] == "OK":
                if verify_user['user']['user_id'] in verify_group['group']['members']:

                    verify_group['group']['members'].remove(verify_user['user']['user_id'])

                    if verify_user['user']['user_id'] in verify_group['group']['admins']:
                        verify_group['group']['admins'].remove(verify_user['user']['user_id'])
                    
                    self.group_conn.execute("UPDATE groups SET group_data = ? WHERE group_id = ?", (json.dumps(verify_group['group']), verify_group['group']['gid']))
                    self.group_conn.commit()

                    return {"status": "OK", "group": verify_group['group']}
                else:return {"status": "AUTH_DOESNT_IN_GROUP", "group": {}}
            else:return {"status": "INVALID_GROUP_ID"}
        else:return {"status": "INVALID_AUTH"}

    def joinGroup(
            self,
            auth_token: str,
            group_id: str
    ):
        verify_user = self.user_manager.getUserByAuth(auth_token)
        verify_group = self.getGroupByID(group_id)

        if verify_user['status'] == "OK":
            if verify_group['status'] == "OK":
                if not verify_user['user']['user_id'] in verify_group['group']['members']:

                    verify_group['group']['members'].append(verify_user['user']['user_id'])

                    if not verify_user['user']['user_id'] in verify_group['group']['admins'] and verify_user['user']['user_id'] == verify_group['group']['owner']:
                        verify_group['group']['admins'].append(verify_user['user']['user_id'])
                    
                    self.group_conn.execute("UPDATE groups SET group_data = ? WHERE group_id = ?", (json.dumps(verify_group['group']), verify_group['group']['gid']))
                    self.group_conn.commit()

                    return {"status": "OK", "group": verify_group['group']}
                else:return {"status": "AUTH_IN_GROUP", "group": {}}
            else:return {"status": "INVALID_GROUP_ID"}
        else:return {"status": "INVALID_AUTH"}


class PrivateManager(object):
    def __init__(self, user_manager: UserManager):
        self.clients_conn = sqlite3.connect("data/prv_messages.db", check_same_thread=False)
        self.user_manager = user_manager
        self.create_table()

    def create_table(self):
        self.clients_conn.execute("CREATE TABLE IF NOT EXISTS messages ( user_id, involved_data )")

    def create_message_id(self) -> str:
        return str(random.randint(100000, 999999999999))

    def getChats(self) -> list:
        return self.clients_conn.execute("SELECT * FROM messages").fetchall()
    
    def getChatByUID(self, user_id: str):
        chats = self.getChats()

        for chat in chats:
            if chat[0] == user_id:
                return {"status": "OK", "chat": json.loads(chat[1])}
            
        return {"status": "INVALID_USER_ID", "chat": {}}

    def addIndex(
            self,
            user_id: str
    ):
        verify_user = self.user_manager.getUserByUserID(user_id)
        verify_chat = self.getChatByUID(user_id)

        if verify_user['status'] == "OK":
            if not verify_chat['status'] == "OK":
                involved_data = {
                    "user_id": user_id,
                    "messages": [],
                    "last_message": {}
                }

                self.clients_conn.execute("INSERT INTO messages (user_id, involved_data) VALUES (?, ?)", (user_id, json.dumps(involved_data)))
                self.clients_conn.commit()

                return {"status": "OK", "involved_data": involved_data}
            else:return {"status": "EXISTS_CHAT"}
        else:return {"status": "INVALID_USER_ID"}

    def addPrivateMessage(
            self,
            from_auth: str,
            to_user_id: str,
            message: str,
            timestamp: str = None,
            reply_data: dict = {}
    ):
        verify_auth = self.user_manager.getUserByAuth(from_auth)
        verify_user = self.user_manager.getUserByUserID(to_user_id)

        message = message.strip()
        timestamp = time.strftime("%H:%M") if timestamp is None else timestamp

        if verify_auth['status'] == "OK":
            if verify_user['status'] == "OK":
                auth_chat = self.getChatByUID(verify_auth['user']['user_id'])
                user_chat = self.getChatByUID(verify_user['user']['user_id'])

                message_data = {
                    "from": verify_auth['user']['fullname'],
                    "to": verify_user['user']['fullname'],
                    "sender_user_id": verify_auth['user']['user_id'],
                    "reciver_user_id": verify_user['user']['user_id'],
                    "message": message,
                    "message_id": self.create_message_id(),
                    "timestamp": timestamp,
                    "is_seen": False,
                    "is_edit": False,
                    "reply_data": reply_data
                }

                auth_chat['chat']['messages'].append({verify_user['user']['username']: message_data})
                user_chat['chat']['messages'].append({verify_auth['user']['username']: message_data})

                auth_chat['chat']['last_message'] = message_data
                user_chat['chat']['last_message'] = message_data

                self.clients_conn.execute("UPDATE messages SET involved_data = ? WHERE user_id = ?", (json.dumps(auth_chat['chat']), verify_auth['user']['user_id']))
                self.clients_conn.execute("UPDATE messages SET involved_data = ? WHERE user_id = ?", (json.dumps(user_chat['chat']), verify_user['user']['user_id']))

                self.clients_conn.commit()

                return {"status": "OK", "message": message_data}

            else:return {"status": "INVALID_USER_ID"}
        else:return {"status": verify_user['status']}

    def getMessageByID(self, user_id: str, message_id):
        chat = self.getChatByUID(user_id)

        if chat['status'] == "OK":
            for message in chat['chat']['messages']:
                for user in list(message.keys()):
                    if message[user]['message_id'] == message_id:
                        return {"status": "OK", "message": message[user]}
            
            return {"status": "UNREACHABLE_MESSAGE_ID"}
        else:return {"status": chat['status']}

    def editMessage(self, from_user_id: str, message_id: str, new_message: str):
        from_chat = self.getChatByUID(from_user_id)
        from_msg = self.getMessageByID(from_user_id, message_id)

        
        if from_chat['status'] == "OK":
            if from_msg['status'] == "OK":
                d = {"msg": ""}
                for message in from_chat['chat']['messages']:
                    for user in list(message.keys()):
                        if message[user]['message_id'] == message_id:
                            # Update the message content for both sender and receiver
                            message[user]['message'] = new_message.strip()
                            message[user]['is_edit'] = True
                            

                            if not from_chat['chat']['last_message'] == message[user]:
                                from_chat['chat']['last_message'] = message[user]
                            

                            self.clients_conn.execute("UPDATE messages SET involved_data = ? WHERE user_id = ?", (json.dumps(from_chat['chat']), from_user_id))
                            self.clients_conn.commit()

                            other_user_id = message[user]['reciver_user_id'] if from_user_id == message[user]['sender_user_id'] else message[user]['sender_user_id']
                            other_chat = self.getChatByUID(other_user_id)
                            for message in other_chat['chat']['messages']:
                                for user in list(message.keys()):
                                    if message[user]['message_id'] == message_id:
                                        message[user]['message'] = new_message.strip()
                                        message[user]['is_edit'] = True
                                        
                                        # Update last message if necessary
                                        if not other_chat['chat']['last_message'] == message[user]:
                                            other_chat['chat']['last_message'] = message[user]

                                        self.clients_conn.execute("UPDATE messages SET involved_data = ? WHERE user_id = ?", (json.dumps(other_chat['chat']), other_user_id))
                                        self.clients_conn.commit()

                            d['msg'] = {"status": "OK", "updated_message": message[user]}


                return d["msg"]
            else:
                return {"status": "UNREACHABLE_MESSAGE_ID"}
        else:
            return {"status": "INVALID_USER_ID"}
        
    def markMessageAsRead(self, from_user_id: str, message_id: str):
        from_chat = self.getChatByUID(from_user_id)
        from_msg = self.getMessageByID(from_user_id, message_id)

        
        if from_chat['status'] == "OK":
            if from_msg['status'] == "OK":
                d = {"msg": ""}
                for message in from_chat['chat']['messages']:
                    for user in list(message.keys()):
                        if message[user]['message_id'] == message_id:
                            message[user]['is_seen'] = True
                            
                            if not from_chat['chat']['last_message'] == message[user]:
                                from_chat['chat']['last_message'] = message[user]
                            
                            self.clients_conn.execute("UPDATE messages SET involved_data = ? WHERE user_id = ?", (json.dumps(from_chat['chat']), from_user_id))
                            self.clients_conn.commit()
                            other_user_id = message[user]['reciver_user_id'] if from_user_id == message[user]['sender_user_id'] else message[user]['sender_user_id']
                            other_chat = self.getChatByUID(other_user_id)
                            for message in other_chat['chat']['messages']:
                                for user in list(message.keys()):
                                    if message[user]['message_id'] == message_id:
                                        message[user]['is_seen'] = True
                                        
                                        if not other_chat['chat']['last_message'] == message[user]:
                                            other_chat['chat']['last_message'] = message[user]

                                        self.clients_conn.execute("UPDATE messages SET involved_data = ? WHERE user_id = ?", (json.dumps(other_chat['chat']), other_user_id))
                                        self.clients_conn.commit()

                            d['msg'] = {"status": "OK", "updated_message": message[user]}


                return d["msg"]
            else:
                return {"status": "UNREACHABLE_MESSAGE_ID"}
        else:
            return {"status": "INVALID_USER_ID"}


# print(UserManager().add_user("ali", "+9843278432", "Someone"))
# print(UserManager().getUsers())

# data = GroupManager(UserManager()).addGroup(
#     "QC2wLIDwv_PKUqGzIr0meMgZTCttozz502WM2f5O6-Q",
#     "دلقک بازی",
#     None,
#     "Someone is Dalghak",
#     "ReDalz",
#     [])

#data = GroupManager(UserManager()).getGroups()[0][1]
#data = GroupManager(UserManager()).add_group_message("ali", "-151118535365", "Hello World 2", reply_data={"from_user": "ali", "timestamp": "324", "message_id": "4325", "message": "XASF"})
#data = GroupManager(UserManager()).searchGroup("z")
#data = UserManager().searchUser("a")
#data = GroupManager(UserManager()).getGroupByGID("-269181497584")
#data = GroupManager(UserManager()).addMemberToGroup("QC2wLIDwv_PKUqGzIr0meMgZTCttozz502WM2f5O6-Q", "ReDalz", "jafar")
#data = GroupManager(UserManager()).removeMemberFromGroup("QC2wLIDwv_PKUqGzIr0meMgZTCttozz502WM2f5O6-Q", "jafar", "ReDalz")
# print(data)
# data = GroupManager(UserManager()).getGroupAdmins("ReDalz")
#data = GroupManager(UserManager()).addGroupMessage("D7ejdNC0IjTSFvtdLZsgObi_nCSIqwwIl4GYg8Jh21U", "-321822164767", "Hello WOrld From JAfar")
#print(data, "\n")
#data = GroupManager(UserManager()).getAnyMessages()#("QC2wLIDwv_PKUqGzIr0meMgZTCttozz502WM2f5O6-Q", "jafar", "ReDalz")
#data = GroupManager(UserManager()).editMessage("QC2wLIDwv_PKUqGzIr0meMgZTCttozz502WM2f5O6-Q",#  "ReDalz", "1719710220991", "Hix")#.getMessageByID("3162977272920")#("QC2wLIDwv_PKUqGzIr0meMgZTCttozz502WM2f5O6-Q", "-321822164767", "something message")

#data = ChatManager(UserManager()).addPrivateMessage("D7ejdNC0IjTSFvtdLZsgObi_nCSIqwwIl4GYg8Jh21U", "jafar", "Hello Jafar")
#data = ChatManager(UserManager()).addPrivateMessage("QC2wLIDwv_PKUqGzIr0meMgZTCttozz502WM2f5O6-Q", "jafar", "Pedaret Bemire Jafar")
#data = ChatManager(UserManager()).getChats()
#data = ChatManager(UserManager()).getAnyMessages()
# import rich
#data = ChatManager(UserManager()).getChatByUName("ali")
#data = ChatManager(UserManager()).markMessagesByMessageId("2851711857015")
#data = ChatManager(UserManager()).addPrivateMessage("QC2wLIDwv_PKUqGzIr0meMgZTCttozz502WM2f5O6-Q", "jafar", "Hello Jafar")
#data = GroupManager(UserManager()).joinGroup("D7ejdNC0IjTSFvtdLZsgObi_nCSIqwwIl4GYg8Jh21U", group_id="zrex")
#data = ChatManager(UserManager()).getChatByUName("ali")
#data = GroupManager(UserManager()).getGroups()
# data = PrivateManager(UserManager()).editMessage("2968877301", "2615108647", "156622353641", "JAFARRRRR")
# data = PrivateManager(UserManager()).getChats()#.getChatByUID("2615108647")

# data = PrivateManager(UserManager()).addIndex("2968877301")
# data = PrivateManager(UserManager()).addIndex("2615108647")
# data = PrivateManager(UserManager()).addPrivateMessage("8hHaNxL5i5OLwT1nvhj5URoFDxsratbC7cscxGmdZHA", "2615108647", "Jafar is Dalghak")

# data = PrivateManager(UserManager()).markMessageAsRead("2968877301", "2615108647", "156622353641")

# rich.print(data)

"""

{
    'status': 'OK',
    'message': {
        'from': 'Ali is Godratmand',
        'to': 'Allah is God',
        'sender_user_id': '2968877301',
        'reciver_user_id': '2615108647',
        'message': 'Jafar is Dalghak',
        'message_id': '405005955940',
        'timestamp': '13:28',
        'is_seen': False,
        'is_edit': False,
        'reply_data': {}
    }
}

{
    'status': 'OK',
    'user': {
        'phone': '04367242342',
        'username': 'ali',
        'fullname': 'Ali is Godratmand',
        'bio': '',
        'profile': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRFEZSqk8dJbB0Xc-fr6AWv2aocxDdFpN6maQ&',
        'token': '8hHaNxL5i5OLwT1nvhj5URoFDxsratbC7cscxGmdZHA',
        'user_id': '2968877301',
        'status': 'online',
        'point': 'user',
        'is_suspension': False,
        'settings': {'hide_phone_number': True, 'can_join_groups': True, 'inner_gif': None}
    }
}

{
    'status': 'OK',
    'user': {
        'phone': '07657756756',
        'username': 'jafar',
        'fullname': 'Allah is God',
        'bio': '',
        'profile': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRFEZSqk8dJbB0Xc-fr6AWv2aocxDdFpN6maQ&',
        'token': 'YxJdmo8UkqLngRhwGva2PSDH_u_gttKRYwYVQtH4_cY',
        'user_id': '2615108647',
        'status': 'online',
        'point': 'user',
        'is_suspension': False,
        'settings': {'hide_phone_number': True, 'can_join_groups': True, 'inner_gif': None}
    }
}

"""