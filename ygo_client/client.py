import logging
from typing import Optional

from ygo_core import Duel, Deck
from ygo_client.executor import DuelExecutor
from ygo_client.manager import GameManager
from ygo_client.connection.connect import YGOConnection
from ygo_client.connection.packet import Packet
from ygo_client.connection.enums.stoc_message import StocMessage
from ygo_client.connection.enums.ctos_message import CtosMessage
from ygo_client.connection.enums.game_message import GameMessage



logger = logging.getLogger(__name__)

class GameClient:
    _connection: YGOConnection
    _gamemanager: GameManager
    _name: str
    _version: int

    def __init__(
        self,  
        executor: DuelExecutor,
        deck: Deck
    ) -> None:
        self._connection = YGOConnection()
        self._gamemanager = GameManager(deck, executor)

    
    def get_deck(self) -> Deck:
        return self._gamemanager.deck


    def get_duel(self) -> Duel:
        return self._gamemanager.duel


    async def connect(
        self,
        host: str, 
        port: int,
        name: str,
        version: int
    ) -> None:
        self._name = name
        self._version = version
        await self._connection.connect(host, port)
        if self._connection.is_connected():
            self._on_connected()

        while self._connection.is_connected():
            packet: Packet = await self._connection.receive()
            await self._on_received(packet)

        logger.debug('Connection has been closed.')
    

    def close(self) -> None:
        self._connection.close()


    async def surrender(self) -> None:
        await self._connection.send(Packet(CtosMessage.SURRENDER))


    async def chat(self, content: str) -> None:
        reply: Packet = Packet(CtosMessage.CHAT)
        reply.write_str(content, byte_size=2*len(content))
        reply.write_int(0)
        await self._connection.send(reply)


    async def _on_connected(self) -> None:          
        packet: Packet = Packet(CtosMessage.PLAYER_INFO)
        packet.write_str(self._name, byte_size=40)
        await self._connection.send(packet)

        junc = bytes([0xcc, 0xcc, 0x00, 0x00, 0x00, 0x00])
        packet = Packet(CtosMessage.JOIN_GAME)
        packet.write_int(self._version & 0xffff, byte_size=2)
        packet.write_bytes(junc)
        packet.write_str('', byte_size=40) # host_room_info here
        packet.write_int(self._version)
        await self._connection.send(packet)


    async def _on_received(self, packet: Packet) -> None:
        reply: Optional[Packet] = None
        msg_id: int = packet.msg_id
        if  msg_id == StocMessage.GAME_MSG:
            id: int = packet.read_int(1)
            if id == GameMessage.RETRY:
                reply = self._gamemanager.on_retry(packet)
            elif id == GameMessage.HINT:
                reply = self._gamemanager.on_hint(packet)
            elif id == GameMessage.START:
                reply = self._gamemanager.on_start(packet)
            elif id == GameMessage.WIN:
                reply = self._gamemanager.on_win(packet)
            elif id == GameMessage.NEW_TURN:
                reply = self._gamemanager.on_new_turn(packet)
            elif id == GameMessage.NEW_PHASE:
                reply = self._gamemanager.on_new_phase(packet)
            elif id == GameMessage.SELECT_IDLE_CMD:
                reply = self._gamemanager.on_select_idle_cmd(packet)
            elif id == GameMessage.SELECT_BATTLE_CMD:
                reply = self._gamemanager.on_select_battle_cmd(packet)
            elif id == GameMessage.SELECT_EFFECT_YN:
                reply = self._gamemanager.on_select_effect_yn(packet)
            elif id == GameMessage.SELECT_YESNO:
                reply = self._gamemanager.on_select_yesno(packet)
            elif id == GameMessage.SELECT_OPTION: 
                reply = self._gamemanager.on_select_option(packet)
            elif id == GameMessage.SELECT_CARD:
                reply = self._gamemanager.on_select_card(packet)
            elif id == GameMessage.SELECT_CHAIN:
                reply = self._gamemanager.on_select_chain(packet)
            elif id == GameMessage.SELECT_PLACE:
                reply = self._gamemanager.on_select_place(packet)
            elif id == GameMessage.SELECT_POSITION:
                reply = self._gamemanager.on_select_position(packet)
            elif id == GameMessage.SELECT_TRIBUTE:
                reply = self._gamemanager.on_select_tribute(packet)
            elif id == GameMessage.SELECT_COUNTER:
                reply = self._gamemanager.on_select_counter(packet)
            elif id == GameMessage.SELECT_SUM:
                reply = self._gamemanager.on_select_sum(packet)
            elif id == GameMessage.SELECT_DISFIELD:
                reply = self._gamemanager.on_select_place(packet)
            elif id == GameMessage.SELECT_UNSELECT:
                reply = self._gamemanager.on_select_unselect(packet)
            elif id == GameMessage.ANNOUNCE_RACE:
                reply = self._gamemanager.on_announce_race(packet)
            elif id == GameMessage.ANNOUNCE_ATTRIB:
                reply = self._gamemanager.on_announce_attr(packet)
            elif id == GameMessage.ANNOUNCE_CARD:
                reply = self._gamemanager.on_announce_card(packet)
            elif id == GameMessage.ANNOUNCE_NUNBER:
                reply = self._gamemanager.on_announce_number(packet)
            elif id == GameMessage.UPDATE_DATA:
                reply = self._gamemanager.on_update_data(packet)
            elif id == GameMessage.UPDATE_CARD:
                reply = self._gamemanager.on_update_card(packet)
            elif id == GameMessage.SHUFFLE_DECK:
                reply = self._gamemanager.on_shuffle_deck(packet)
            elif id == GameMessage.SHUFFLE_HAND:
                reply = self._gamemanager.on_shuffle_hand(packet)
            elif id == GameMessage.SHUFFLE_EXTRA:
                reply = self._gamemanager.on_shuffle_extra(packet)
            elif id == GameMessage.SHUFFLE_SETCARD:
                reply = self._gamemanager. on_shuffle_setcard(packet)
            elif id == GameMessage.SORT_CARD:
                reply = self._gamemanager.on_sort_card(packet)
            elif id == GameMessage.SORT_CHAIN:
                reply = self._gamemanager.on_sort_chain(packet)
            elif id == GameMessage.MOVE:
                reply = self._gamemanager.on_move(packet)
            elif id == GameMessage.POSCHANGE:
                reply = self._gamemanager.on_poschange(packet)
            elif id == GameMessage.SET:
                reply = self._gamemanager.on_set(packet)
            elif id == GameMessage.SWAP:
                reply = self._gamemanager.on_swap(packet)
            elif id == GameMessage.SUMMONING:
                reply = self._gamemanager.on_summoning(packet)
            elif id == GameMessage.SUMMONED:
                reply = self._gamemanager.on_summoned(packet)
            elif id == GameMessage.SPSUMMONING:
                reply = self._gamemanager.on_spsummoning(packet)
            elif id == GameMessage.SPSUMMONED:
                reply = self._gamemanager.on_spsummoned(packet)
            elif id == GameMessage.FLIPSUMMONING:
                reply = self._gamemanager.on_summoning(packet)
            elif id == GameMessage.FLIPSUMMONED:
                reply = self._gamemanager.on_summoned(packet)
            elif id == GameMessage.CHAINING:
                reply = self._gamemanager.on_chaining(packet)
            elif id == GameMessage.CHAIN_END:
                reply = self._gamemanager.on_chain_end(packet)
            elif id == GameMessage.BECOME_TARGET:
                reply = self._gamemanager.on_become_target(packet)
            elif id == GameMessage.DRAW:
                reply = self._gamemanager.on_draw(packet)
            elif id == GameMessage.DAMAGE:
                reply = self._gamemanager.on_damage(packet)
            elif id == GameMessage.RECOVER:
                reply = self._gamemanager.on_recover(packet)
            elif id == GameMessage.EQUIP:
                reply = self._gamemanager.on_equip(packet)
            elif id == GameMessage.UNEQUIP:
                reply = self._gamemanager.on_unequip(packet)
            elif id == GameMessage.LP_UPDATE:
                reply = self._gamemanager.on_lp_update(packet)
            elif id == GameMessage.CARD_TARGET:
                reply = self._gamemanager.on_card_target(packet)
            elif id == GameMessage.CANCEL_TARGET:
                reply = self._gamemanager.on_cancel_target(packet)
            elif id == GameMessage.PAY_LPCOST:
                reply = self._gamemanager.on_damage(packet)
            elif id == GameMessage.ATTACK:
                reply = self._gamemanager.on_attack(packet)
            elif id == GameMessage.BATTLE:
                reply = self._gamemanager.on_battle(packet)
            elif id == GameMessage.ATTACK_DISABLED:
                reply = self._gamemanager.on_attack_disabled(packet)
            elif id == GameMessage.ROCK_PAPER_SCISSORS:
                reply = self._gamemanager.on_rock_paper_scissors(packet)
            elif id == GameMessage.TAG_SWAP:
                reply = self._gamemanager.on_tag_swap(packet)

        elif msg_id == StocMessage.ERROR_MSG:
            reply = self._gamemanager.on_error_msg(packet)
            self.close()
        elif msg_id == StocMessage.SELECT_HAND:
            reply = self._gamemanager.on_select_hand(packet)
        elif msg_id == StocMessage.SELECT_TP:
            reply = self._gamemanager.on_select_tp(packet)
        elif msg_id == StocMessage.CHANGE_SIDE:
            reply = self._gamemanager.on_change_side(packet)
        elif msg_id == StocMessage.JOIN_GAME:
            reply = self._gamemanager.on_joined_game(packet)
        elif msg_id == StocMessage.TYPE_CHANGE:
            reply = self._gamemanager.on_type_changed(packet)
        elif msg_id == StocMessage.DUEL_START:
            reply = self._gamemanager.on_duel_start(packet)
        elif msg_id == StocMessage.DUEL_END:
            reply = self._gamemanager.on_duel_end(packet)
            self.close()
        elif msg_id == StocMessage.REPLAY:
            reply = self._gamemanager.on_replay(packet)
        elif msg_id == StocMessage.TIMELIMIT:
            reply = self._gamemanager.on_timelimit(packet)
        elif msg_id == StocMessage.CHAT:
            reply = self._gamemanager.on_chat(packet)
        elif msg_id == StocMessage.PLAYER_ENTER:
            reply = self._gamemanager.on_player_enter(packet)
        elif msg_id == StocMessage.PLAYER_CHANGE:
            reply = self._gamemanager.on_player_change(packet)
        elif msg_id == StocMessage.WATCH_CHANGE:
            reply = self._gamemanager.on_watch_change(packet)
        elif msg_id == StocMessage.REMATCH:
            reply = self._gamemanager.on_rematch(packet)

        if reply:
            await self._connection.send(reply)
