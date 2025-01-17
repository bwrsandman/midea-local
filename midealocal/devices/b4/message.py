from ...message import MessageType, MessageRequest, MessageResponse, MessageBody


class MessageB4Base(MessageRequest):
    def __init__(self, protocol_version, message_type, body_type):
        super().__init__(
            device_type=0xB4,
            protocol_version=protocol_version,
            message_type=message_type,
            body_type=body_type,
        )

    @property
    def _body(self):
        raise NotImplementedError


class MessageQuery(MessageB4Base):
    def __init__(self, protocol_version):
        super().__init__(
            protocol_version=protocol_version,
            message_type=MessageType.query,
            body_type=0x01,
        )

    @property
    def _body(self):
        return bytearray([])


class B4MessageBody(MessageBody):
    def __init__(self, body):
        super().__init__(body)
        self.time_remaining = (
            (0 if body[22] == 0xFF else body[22]) * 3600
            + (0 if body[23] == 0xFF else body[23]) * 60
            + (0 if body[24] == 0xFF else body[24])
        )
        self.current_temperature = (body[25] << 8) + body[26]
        if self.current_temperature == 0:
            self.current_temperature = (body[27] << 8) + body[28]
        self.status = body[31]
        self.door = (body[32] & 0x02) > 0
        self.tank_ejected = (body[16] & 0x04) > 0
        self.water_shortage = (body[16] & 0x08) > 0
        self.water_change_reminder = (body[16] & 0x10) > 0


class MessageB4Response(MessageResponse):
    def __init__(self, message):
        super().__init__(message)
        if self.message_type in [
            MessageType.notify1,
            MessageType.query,
            MessageType.set,
        ]:
            if self.body_type == 0x01:
                self.set_body(B4MessageBody(super().body))
        self.set_attr()
