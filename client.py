from typing import List, Callable
class Group:
    def __init__(self, client : Client, nick : str, id : str):
        self.client = client
        self.nick = nick
        self.id = id
        self._message_callbacks : List[Callable[[User, Message], None]] = []
    def on_message(self):
        def do_register(func : Callable[[User, Message], None]) -> None:
            self._message_callbacks.append(func)
        return do_register
    def _do_on_message(self, sender : User, message : Message) -> None:
        for callback in self._message_callbacks:
            callback(sender, message)
    @property
    def alive(self) -> bool:
        return False
class User:
    def __init__(self, client : Client, nick : str, id : str):
        self.client = client
        self.nick = nick
        self.id = id
        self._message_callbacks : List[Callable[[Message], None]] = []
    def on_message(self):
        def do_register(func : Callable[[Message], None]) -> None:
            self._message_callbacks.append(func)
        return do_register
    def _do_on_message(self, message : Message) -> None:
        for callback in self._message_callbacks:
            callback(sender, message)
    @property
    def alive(self) -> bool:
        return False
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
        pass
    def send_private_message(self, user : User, message : Message) -> None:
        pass
    @property
    def alive(self) -> bool:
        return False

import wxpy
class WxpyGroup(Group):
    def __init__(wxbot, wxgroup):
        pass
class WxpyUser(User):
    def __init__(self, wxclient, wxbot, wxuser):
        super(User, self).__init__(wxclient, wxuser.name, wxuser.wxid)
        self._wxbot = wxbot
        @self._wxbot.register(wxuser, wxpy.TEXT)
        def raw_on_message(raw_message):
            pass
    @property
    def alive(self) -> bool:
        return self._wxbot.alive()
   
class WxpyClient(Client):
    def __init__(self):
        super(Client, self).__init__()
        wxbot = wxpy.Bot()
        @wxbot.register(wxbot.groups(), wxpy.TEXT)
        def raw_on_group_message(raw_message):
            message = Message(raw_message.text)
            user = User(raw_message.member.name, raw_message.member.wxid)
            #group#WIP
