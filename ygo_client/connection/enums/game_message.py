import enum


class GameMessage(enum.IntEnum):
    RETRY             = 1
    HINT              = 2
    WAITING           = 3
    START             = 4
    WIN               = 5
    UPDATE_DATA       = 6
    UPDATE_CARD       = 7
    REQUEST_DECK      = 8
    SELECT_BATTLE_CMD = 10
    SELECT_IDLE_CMD   = 11
    SELECT_EFFECT_YN  = 12
    SELECT_YESNO      = 13
    SELECT_OPTION     = 14
    SELECT_CARD       = 15
    SELECT_CHAIN      = 16
    SELECT_PLACE      = 18
    SELECT_POSITION   = 19
    SELECT_TRIBUTE    = 20
    SORT_CHAIN        = 21
    SELECT_COUNTER    = 22
    SELECT_SUM        = 23
    SELECT_DISFIELD   = 24
    SORT_CARD         = 25
    SELECT_UNSELECT   = 26
    CONFIRM_DECKTOP   = 30
    CONFIRM_CARDS     = 31
    SHUFFLE_DECK      = 32
    SHUFFLE_HAND      = 33
    REFLESH_DECK      = 34
    SWAP_GRAVEDECK    = 35
    SHUFFLE_SETCARD   = 36
    REVERSE_DECK      = 37
    DECKTOP           = 38
    SHUFFLE_EXTRA     = 39
    NEW_TURN          = 40
    NEW_PHASE         = 41
    CONFIRM_EXTRATOP  = 42
    MOVE              = 50
    POSCHANGE         = 53
    SET               = 54
    SWAP              = 55
    FIELD_DISABLED    = 56
    SUMMONING         = 60
    SUMMONED          = 61
    SPSUMMONING       = 62
    SPSUMMONED        = 63
    FLIPSUMMONING     = 64
    FLIPSUMMONED      = 65
    CHAINING          = 70
    CHAINED           = 71
    CHAIN_SOLVING     = 72
    CHAIN_SOLVED      = 73
    CHAIN_END         = 74
    CHAIN_NEGATED     = 75
    CHAIN_DISABLED    = 76
    CARD_SELECT_ED    = 80
    RANDOM_SELECT_ED  = 81
    BECOME_TARGET     = 83
    DRAW              = 90
    DAMAGE            = 91
    RECOVER           = 92
    EQUIP             = 93
    LP_UPDATE         = 94
    UNEQUIP           = 95
    CARD_TARGET       = 96
    CANCEL_TARGET     = 97
    PAY_LPCOST        = 100
    ADD_COUNTER       = 101
    REMOVE_COUNTER    = 102
    ATTACK            = 110
    BATTLE            = 111
    ATTACK_DISABLED   = 112
    DAMAGESTEP_START  = 113
    DAMAGESTEP_End    = 114
    MISSED_EFFECT     = 120
    BE_CHAINTARGET    = 121
    CREATE_RELATION   = 122
    RELEASE_RELATION  = 123
    TOSS_COIN         = 130
    TOSS_DICE         = 131
    ROCK_PAPER_SCISSORS = 132
    HAND_RESULT       = 133
    ANNOUNCE_RACE     = 140
    ANNOUNCE_ATTRIB   = 141
    ANNOUNCE_CARD     = 142
    ANNOUNCE_NUNBER   = 143
    CARD_HINT         = 160
    TAG_SWAP          = 161
    RELOAD_FIELD      = 162
    AI_NAME           = 163
    SHOW_HINT         = 164
    PLAYER_HINT       = 165
    MATCH_KILL        = 170
    CUSTOM_MSG        = 180
    DUEL_WINNER       = 200