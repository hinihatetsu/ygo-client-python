import enum

class CtosMessage(enum.IntEnum):
    RESPONSE         = 0x1
    UPDATE_DECK      = 0x2
    HAND_RESULT      = 0x3
    TP_RESULT        = 0x4
    PLAYER_INFO      = 0x10
    CREATE_GAME      = 0x11
    JOIN_GAME        = 0x12
    LEAVE_GAME       = 0x13
    SURRENDER        = 0x14
    TIME_CONFIRM     = 0x15
    CHAT             = 0x16
    TO_DUELIST       = 0x20 
    TO_SPECTATOR     = 0x21
    READY            = 0x22
    NOTREADY         = 0x23
    KICK             = 0x24
    START            = 0x25
    REMATCH_RESPONSE = 0xf0