from db.manager import UserManager, PrivateManager, GroupManager, getChats, getMessages


class Handler:
    def __init__(self) -> None:
        self.user_manager = UserManager()
        self.private_manager = PrivateManager(self.user_manager)
        self.group_manager = GroupManager(self.user_manager)

        self.point_modes = self.user_manager.points
        self.user_profile = self.user_manager.default_profile
        self.ghostly_profile = self.user_manager.ghostly
        self.default_group_profile = self.group_manager.default_group_profile

    # ---- Users Functions ----

    def getMe(self, auth_token: str):
        return self.user_manager.getUserByAuth(auth_token)
    
    def getUserInfo(self, auth_token: str, target_username: str):
        verify_auth = self.user_manager.getUserByAuth(auth_token)
        verify_target = self.user_manager.getUserByUName(target_username)

        if verify_auth['status'] == "OK":
            if verify_target['status'] == "OK":
                del verify_target['user']['token']
                if verify_target['user']['settings']['hide_phone_number']:
                    del verify_target['user']['phone']

                return verify_target
            else:return verify_target
        else:return verify_auth

    def getAdmins(self, auth_token: str):
        verify_auth = self.user_manager.getUserByAuth(auth_token)

        if verify_auth['status'] == "OK":
            return self.user_manager.getAdmins()
        else:return verify_auth

    def getDevs(self, auth_token: str):
        verify_auth = self.user_manager.getUserByAuth(auth_token)

        if verify_auth['status'] == "OK":
            return self.user_manager.getDevs()
        else:return verify_auth

    def sendCode(self, phone_number: str):
        return self.user_manager.sendCode(phone_number)
    
    def agreeCode(self, phone_number: str, code: str):
        return self.user_manager.agreeCode(phone_number, code)
    
    def createAccount(
            self,
            username: str,
            phone: str,
            fullname: str,
            bio: str = "",
            profile: str = None
    ):
        return self.user_manager.addUser(
            username,
            phone,
            fullname,
            bio,
            profile
        )
    
    def suspensionAccount(self, auth_token: str):
        return self.user_manager.suspensionUser(auth_token)
    
    def editAccount(
            self,
            auth_token: str,

            fullname: str = None,
            username: str = None,
            bio: str = None, 
            profile: str = None,

            inner_gif: str = None,
            hide_phone_number: bool = None,
            can_join_groups: bool = None
    ):
        return self.user_manager.update_user_profile(
            auth_token,
            fullname,
            username,
            bio,
            profile,
            inner_gif,
            hide_phone_number,
            can_join_groups
        )
    
    def loginAccount(self, phone_number: str):
        return self.user_manager.login(phone_number)
    
    def changePoint(self, auth_token: str, mode: str):
        return self.user_manager.change_point(auth_token, mode)
    
    def offline(self, auth_token: str):
        return self.user_manager.online(auth_token)
    
    def online(self, auth_token: str):
        return self.user_manager.online(auth_token, "online")
    
    def searchUser(self, auth_token: str, username: str):
        verify_auth = self.user_manager.getUserByAuth(auth_token)

        if verify_auth['status'] == "OK":
            return self.user_manager.searchUser(username)
        else:return verify_auth

    def isExistsUser(self, username: str):
        return {"status": "OK", "user_status": self.user_manager.user_exists(username)}
    
    # ---- Groups Functions ----

    def createGroup(
            self,
            auth_token: str,
            group_title: str,
            group_profile: str = "",
            group_caption: str = "",
            group_id: str = None,
            members: str = []
    ):
        return self.group_manager.addGroup(
            auth_token,
            group_title,
            group_profile,
            group_caption,
            group_id,
            members
        )
    
    def getGroupByID(self, group_id: str):
        return self.group_manager.getGroupByID(group_id)
    
    def getGroupByGID(self, gid: str):
        return self.group_manager.getGroupByGID(gid)
    
    def getGroupMessageByID(self, message_id: str):
        return self.group_manager.getMessageByID(message_id)
    
    def sendGroupMessage(
            self,
            from_auth: str,
            gid: str,
            message: str,
            timestamp: str = None,
            reply_data: dict = {}
    ):
        return self.group_manager.addGroupMessage(
            from_auth,
            gid,
            message,
            timestamp,
            reply_data
        )
    
    def searchGroup(self, auth_token: str, group_id: str):
        verify_auth = self.user_manager.getUserByAuth(auth_token)

        if verify_auth['status'] == "OK":
            return self.group_manager.searchGroup(group_id)
        else:return verify_auth

    def addAdmin(
            self,
            auth_token: str,
            member_user_id: str,
            group_id: str
        ):
        return self.group_manager.addAdmin(
            auth_token,
            member_user_id,
            group_id
        )
    
    def removeAdmin(
            self,
            auth_token: str,
            member_user_id: str,
            group_id: str
        ):
        return self.group_manager.removeAdmin(
            auth_token,
            member_user_id,
            group_id
        )
    
    def addMemberToGroup(
            self,
            auth_token: str,
            group_id: str,
            user_id: str
        ):
        return self.group_manager.addMemberToGroup(auth_token, group_id, user_id)
    
    def getGroupMembersByID(self, auth_token: str, group_id: str):
        return self.group_manager.getGroupMembersByID(auth_token, group_id)
    
    def getGroupMembersByGID(self, auth_token: str, gid: str):
        return self.group_manager.getGroupMembersByGID(auth_token, gid)
    
    def removeMemberFromGroup(self, auth_token: str, member_user_id: str, group_id: str):
        return self.group_manager.removeMemberFromGroup(auth_token, member_user_id, group_id)
    
    def pinMessage(self, auth_token: str, message_id: str, group_id: str):
        return self.group_manager.pinMessage(auth_token, message_id, group_id)
    
    def clearPin(self, auth_token: str, group_id: str):
        return self.group_manager.clearPin(auth_token, group_id)
    
    def lockGroup(self, auth_token: str, group_id: str):
        return self.group_manager.lockGroup(auth_token, group_id)
    
    def unlockGroup(self, auth_token: str, group_id: str):
        return self.group_manager.unlockGroup(auth_token, group_id)
    
    def getGroupMessages(self, auth_token: str, group_id: str):
        return self.group_manager.getGroupMessages(auth_token, group_id)
    
    def getGroupAdmins(self, group_id: str):
        return self.group_manager.getGroupAdmins(group_id)
    
    def editGroupMessage(
            self,
            from_auth: str,
            group_id: str,
            message_id: str,
            new_message: str
    ):
        return self.group_manager.editMessage(
            from_auth,
            group_id,
            message_id,
            new_message
        )
    
    def getUserGroups(self, auth_token: str):
        return self.group_manager.getGroupUserExists(auth_token)
    
    def leaveGroup(self, auth_token: str, group_id: str):
        return self.group_manager.leaveGroup(auth_token, group_id)
    
    def joinGroup(self, auth_token: str, group_id: str):
        return self.group_manager.joinGroup(auth_token, group_id)
    
    # ---- Private Functions ----

    def addIndex(self, user_id: str):
        return self.private_manager.addIndex(user_id)
    
    def sendPrivateMessage(
            self,
            from_auth: str,
            to_user_id: str,
            message: str,
            timestamp: str = None,
            reply_data: dict = {}
    ):
        return self.private_manager.addPrivateMessage(
            from_auth,
            to_user_id,
            message,
            timestamp,
            reply_data
        )
    
    def getPrivateMessageByID(self, user_id: str, message_id: str):
        return self.private_manager.getMessageByID(user_id, message_id)
    
    def getPrivateMessagesByUserID(self, user_id: str):
        return self.private_manager.getMessagesByUserID(user_id)
    
    def editPrivateMessage(
            self,
            from_auth_token: str,
            message_id: str,
            new_message: str
    ):
        return self.private_manager.editMessage(from_auth_token, message_id, new_message)
    
    def markMessageAsRead(self, from_auth_token: str, message_id: str):
        return self.private_manager.markMessageAsRead(from_auth_token, message_id)

    # ---- Last Functions ----

    def getChats(self, auth_token: str):
        return getChats(
            auth_token,
            self.user_manager,
            self.private_manager,
            self.group_manager
        )
    
    def getMessages(self, auth_token: str):
        return getMessages(
            auth_token,
            self.user_manager,
            self.private_manager,
            self.group_manager
        )