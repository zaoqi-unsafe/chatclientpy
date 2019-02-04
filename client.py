from typing import List, Callable, Mapping
class Group:
    def __init__(self, client : Client, nick : str, id : str):
        self.client = client
        self.nick = nick
        self.id = id
        self._message_callbacks : List[Callable[[User, Message], None]] = []
        @client.on_group_message
        def _handle_client_grpmsg(group : Group, sender : User, message : Message) -> None:
            if group == self:
                self._do_on_message(sender, message)
    def on_message(self):
        def do_register(func : Callable[[User, Message], None]) -> None:
            self._message_callbacks.append(func)
        return do_register
    def _do_on_message(self, sender : User, message : Message) -> None:
        for callback in self._message_callbacks:
            callback(sender, message)
    @property
    def alive(self) -> bool:
        return self.client.alive
    def send(self, message : Message) -> None:
        self.client.send_group_message(self, message)
class User:
    def __init__(self, client : Client, nick : str, id : str):
        self.client = client
        self.nick = nick
        self.id = id
        self._message_callbacks : List[Callable[[Message], None]] = []
        @client.on_private_message
        def _handle_client_privmsg(sender : User, message : Message) -> None:
            if sender ==  self:
                self._do_on_message(message)
    def on_message(self):
        def do_register(func : Callable[[Message], None]) -> None:
            self._message_callbacks.append(func)
        return do_register
    def _do_on_message(self, message : Message) -> None:
        for callback in self._message_callbacks:
            callback(sender, message)
    @property
    def alive(self) -> bool:
        return self.client.alive
    def send(self, message : Message) -> None:
        self.client.send_private_message(self, message)
class Message:
    def __init__(self, message : str):
        self.message : str = message
class Client:
    def __init__(self):
        self._group_message_callbacks : List[Callable[[Group, User, Message], None]] = []
        self._private_message_callbacks : List[Callable[[User, Message], None]] = []
    def on_group_message(self):
        def do_register(func : Callable[[Group, User, Message], None]) -> None:
            self._group_message_callbacks.append(func)
        return do_register
    def _do_on_group_message(self, group : Group, sender : User, message : Message) -> None:
        for callback in self._group_message_callbacks:
            callback(group, sender, message)
    def on_private_message(self):
        def do_register(func : Callable[[User, Message], None]):
            self._private_message_callbacks.append(func)
        return do_register
    def _do_on_private_message(self, sender : User, message : Message) -> None:
        for callback in self._private_message_callbacks:
            callback(sender, message)
    def send_group_message(self, group : Group, message : Message) -> None:
        return self._send_group_message(group, message)
    def send_private_message(self, user : User, message : Message) -> None:
        return self._send_private_message(user, message)
    @property
    def alive(self) -> bool:
        return self._alive()
    @property
    def groups(self) -> List[Group]:
        return self._groups()
    @property
    def friends(self) -> List[User]:
        return self._friends()

import wxpy
class WxpyClient(Client):
    def __init__(self):
        super(Client, self).__init__()
        wxbot = wxpy.Bot()
        wxbot.enable_puid()
        wx2usermap : Mapping[str, User] = {}
        user2wxmap : Mapping[User, str] = {}
        def wx2user(wxuser : wxpy.User) -> User:
            puid = wxuser.puid
            if puid in wx2usermap:
                return wx2usermap[puid]
            else:
                user = User(self, wxuser.name, puid)
                wx2usermap[puid] = user
                user2wxmap[user] = puid
                return user
        def user2wx(user : User) -> wxpy.User:
            puid = user2wxmap[user]
            for friend in wxbot.friends():
                if friend.puid == puid:
                    return friend
            for group in wxbot.groups():
                for member in group.members:
                    if member.puid == puid:
                        return member
            for mp in wxbot.mps():
                if mp.puid == puid:
                    return mp
            raise ValueError('not found')
        wx2groupmap : Mapping[str, Group] = {}
        group2wxmap : Mapping[Group, str] = {}
        def wx2group(wxgroup : wxpy.Group) -> Group:
            puid = wxgroup.puid
            if puid in wx2groupmap:
                return wx2groupmap[puid]
            else:
                group = Group(self, wxgroup.name, wxgroup.puid)
                wx2groupmap[puid] = group
                group2wxmap[group] = puid
        def group2wx(group : Group) -> wxpy.Group:
            puid = group2wxmap[group]
            for wxg in wxbot.groups():
                if wxg.puid == puid:
                    return wxg
            raise ValueError('not found')
        @wxbot.register(msg_types=wxpy.TEXT)
        def raw_on_message(raw_message):
            message = Message(raw_message.text)
            if message.chat == wxpy.Group:
                #user = User(self, raw_message.member.name, raw_message.member.wxid)
                user = wx2user(raw_message.member)
                group = wx2group(raw_message.sender)
