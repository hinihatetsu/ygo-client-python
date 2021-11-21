import enum

class StocMessage(enum.IntEnum):
    GAME_MSG            = 0x1
    ERROR_MSG           = 0x2
    SELECT_HAND         = 0x3
    SELECT_TP           = 0x4
    HAND_RESULT         = 0x5
    TP_RESULT           = 0x6
    CHANGE_SIDE         = 0x7
    WAITING_SIDE_CHANGE = 0x8
    CREATE_GAME         = 0x11
    JOIN_GAME           = 0x12
    TYPE_CHANGE         = 0x13
    LEAVE_GAME          = 0x14
    DUEL_START          = 0x15
    DUEL_END            = 0x16
    REPLAY              = 0x17
    TIMELIMIT           = 0x18
    CHAT                = 0x19
    PLAYER_ENTER        = 0x20
    PLAYER_CHANGE       = 0x21
    WATCH_CHANGE        = 0x22
    CATCH_UP            = 0xf0
    REMATCH             = 0xf1
    WAITING_REMATCH     = 0xf2

    NEW_REPLAY          = 0x30