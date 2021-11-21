import logging
from typing import Optional

from ygo_core.deck import Deck
from ygo_core.duel import Duel, Card
from ygo_core.zone import Zone, ZoneID
from ygo_core.phase import MainPhase, BattlePhase
from ygo_core.card import Location, Position, Race, Attribute, Type
from ygo_core.enums import Player, Phase, Query

from ygo_client.executor import DuelExecutor
from ygo_client.connection.packet import Packet
from ygo_client.connection.enums.ctos_message import CtosMessage
from ygo_client.connection.enums.error_type import ErrorType


logger = logging.getLogger(__name__)

SERVER_HANDSHAKE: int = 4043399681

class GameManager:
    deck: Deck
    executor: DuelExecutor
    duel: Duel
    _select_hint: int = 0


    def __init__(self, deck: Deck, executor: DuelExecutor) -> None:
        self.deck = deck
        self.executor = executor
        self.duel = Duel()


    def on_error_msg(self, packet: Packet) -> Optional[Packet]:
        error_type: int = packet.read_int(1)
        if error_type is ErrorType.JOINERROR:
            logger.error('Join Error')

        elif error_type is ErrorType.DECKERROR:
            logger.error('Deck Error')

        elif error_type is ErrorType.SIDEERROR:
            logger.error('Side Error')
        
        elif error_type is ErrorType.VERSIONERROR:
            logger.error('Version Error')

        elif error_type is ErrorType.VERSIONERROR2:
            logger.critical('Version Error')
            unknown = packet.read_int(3)
            version = packet.read_int(4)
            logger.critical(f'Host Version: {version & 0xff}.{(version >> 8) & 0xff}.{(version >> 16) & 0xff}.{(version >> 24) & 0xff}')
        
        else:
            assert False, 'unknown ErrorType'
        return None


    def on_select_hand(self, packet: Packet) -> Optional[Packet]:
        hand: int = self.executor.select_hand()
        assert hand in {1, 2, 3}
        reply: Packet = Packet(CtosMessage.HAND_RESULT)
        reply.write_int(hand, byte_size=1)
        return reply


    def on_select_tp(self, packet: Packet) -> Optional[Packet]:
        has_selected_first: bool = self.executor.select_tp()
        reply: Packet = Packet(CtosMessage.TP_RESULT)
        reply.write_bool(has_selected_first)
        return reply


    def on_change_side(self, packet: Packet) -> Optional[Packet]:
        self.executor.change_side(self.deck)
        reply: Packet = Packet(CtosMessage.UPDATE_DECK)
        reply.write_int(self.deck.count_main + self.deck.count_extra)
        reply.write_int(self.deck.count_side)
        for card in self.deck.main + self.deck.extra + self.deck.side:
            reply.write_int(card)
        return reply


    def on_joined_game(self, packet: Packet) -> Optional[Packet]:
        lflist: int = packet.read_int(4)
        rule: int = packet.read_int(1)
        mode: int = packet.read_int(1)
        duel_rule: int = packet.read_int(1)
        nocheck_deck: bool = packet.read_bool()
        noshuffle_deck: bool = packet.read_bool()
        align: bytes = packet.read_bytes(3)
        start_lp = packet.read_int(4)
        start_hand: int = packet.read_int(1)
        draw_count: int = packet.read_int(1)
        time_limit: int = packet.read_int(2)
        align = packet.read_bytes(4)
        handshake: int = packet.read_int(4)
        version: int = packet.read_int(4)
        team1: int = packet.read_int(4)
        team2: int = packet.read_int(4)
        best_of: int = packet.read_int(4)
        duel_flag: int = packet.read_int(4)
        forbidden_types: int = packet.read_int(4)
        extra_rules: int = packet.read_int(4)

        if handshake != SERVER_HANDSHAKE:
            logger.error('handshake error')
            raise ConnectionRefusedError('Handshake is failed')
        
        reply: Packet = Packet(CtosMessage.UPDATE_DECK)
        reply.write_int(self.deck.count_main + self.deck.count_extra)
        reply.write_int(self.deck.count_side)
        for card in self.deck.main + self.deck.extra + self.deck.side:
            reply.write_int(card)
        return reply


    def on_type_changed(self, packet: Packet) -> Optional[Packet]:
        is_spectator: int = 7
        position = packet.read_int(1)
        if position < 0 or position >= is_spectator:
            return None

        return Packet(CtosMessage.READY)


    def on_duel_start(self, packet: Packet) -> Optional[Packet]:
        return None


    def on_duel_end(self, packet: Packet) -> Optional[Packet]:
        return None


    def on_replay(self, packet: Packet) -> Optional[Packet]:
        return None


    def on_timelimit(self, packet: Packet) -> Optional[Packet]:
        player: Player = self.duel.players[packet.read_int(1)]
        if player == Player.ME:  
            return Packet(CtosMessage.TIME_CONFIRM)
        return None

    def on_chat(self, packet: Packet) -> Optional[Packet]:
        return None


    def on_player_enter(self, packet: Packet) -> Optional[Packet]:
        name: str = packet.read_str(40)
        return None


    def on_player_change(self, packet: Packet) -> Optional[Packet]:
        return None


    def on_watch_change(self, packet: Packet) -> Optional[Packet]:
        return None


    def on_rematch(self, packet: Packet) -> Optional[Packet]:
        win = False
        ans: bool = self.executor.rematch(win) 
        reply: Packet = Packet(CtosMessage.REMATCH_RESPONSE)
        reply.write_bool(ans)
        return reply



    def on_retry(self, packet: Packet) -> Optional[Packet]:
        raise NotImplementedError()


    def on_hint(self, packet: Packet) -> Optional[Packet]:
        HINT_EVENT = 1
        HINT_MESSAGE = 2
        HINT_SELECT = 3
        MAINPHASE_END = 23
        BATTLEING = 24
        hint_type: int = packet.read_int(1)
        player_msg_sent_to: Player = self.duel.players[packet.read_int(1)]
        data: int = packet.read_int(8)
        if hint_type == HINT_EVENT:
            if data == MAINPHASE_END:
                self.duel.at_mainphase_end()
                
            elif data == BATTLEING:
                self.duel.field[0].under_attack = False
                self.duel.field[1].under_attack = False

        if hint_type == HINT_SELECT:
            self._select_hint = data
        return None


    def on_start(self, packet: Packet) -> Optional[Packet]:
        is_first = not packet.read_bool()
        first_player: Player = Player.ME if is_first else Player.OPPONENT
        self.duel.on_start(first_player)

        for player in self.duel.players:
            self.duel.on_lp_update(player, packet.read_int(4))
        
        for player in self.duel.players:
            num_of_main: int = packet.read_int(2)
            num_of_extra: int = packet.read_int(2)
            self.duel.set_deck(player, num_of_main, num_of_extra)

        self.executor.on_start()
        return None


    def on_win(self, packet: Packet) -> Optional[Packet]:
        win: bool = self.duel.players[packet.read_int(1)] == Player.ME
        self.executor.on_win(win)
        return None


    def on_new_turn(self, packet: Packet) -> Optional[Packet]:
        turn_player: Player = self.duel.players[packet.read_int(1)]
        self.duel.on_new_turn(turn_player)
        self.executor.on_new_turn()
        return None

    
    def on_new_phase(self, packet: Packet) -> Optional[Packet]:
        phase: Phase = packet.read_phase()
        self.duel.on_new_phase(phase)
        self.executor.on_new_phase()
        return None


    def on_select_idle_cmd(self, packet: Packet) -> Packet:
        player_msg_sent_to: Player = self.duel.players[packet.read_int(1)] 
        main: MainPhase = MainPhase()
        for card_list in main:
            if card_list is main.activatable: 
                for _ in range(packet.read_int(4)):
                    card_id: int = packet.read_id()
                    controller: Player = self.duel.players[packet.read_int(1)]
                    location: Location = packet.read_location()
                    index: int = packet.read_int(4)
                    description: int = packet.read_int(8)
                    operation_type: int = packet.read_int(1)

                    card: Card = self.duel.get_card(controller, location, index)
                    card.id = card_id
                    main.activatable.append(card)
                    main.activation_descs.append(description)

            else:
                for _ in range(packet.read_int(4)):
                    card_id = packet.read_id()
                    controller = self.duel.players[packet.read_int(1)]
                    location = packet.read_location()
                    index = packet.read_int(4) if card_list is not main.repositionable else packet.read_int(1)

                    card = self.duel.get_card(controller, location, index)
                    card.id = card_id
                    card_list.append(card)

        main.can_battle = packet.read_bool()
        main.can_end = packet.read_bool()
        can_shuffle = packet.read_bool()
        
        selected: int = self.executor.select_mainphase_action(main)
        reply: Packet = Packet(CtosMessage.RESPONSE)
        reply.write_int(selected)
        return reply


    def on_select_battle_cmd(self, packet: Packet) -> Optional[Packet]:
        player_msg_sent_to: Player = self.duel.players[packet.read_int(1)]
        battle: BattlePhase = BattlePhase()

        # activatable cards
        for _ in range(packet.read_int(4)):
            card_id: int = packet.read_id()
            controller: Player = self.duel.players[packet.read_int(1)]
            location: Location = packet.read_location()
            index: int = packet.read_int(4)
            description: int = packet.read_int(8)
            operation_type: bytes = packet.read_bytes(1)

            card: Card = self.duel.get_card(controller, location, index)
            card.id = card_id
            battle.activatable.append(card)
            battle.activation_descs.append(description)

        # attackable cards
        for _ in range(packet.read_int(4)):
            card_id = packet.read_id()
            controller = self.duel.players[packet.read_int(1)]
            location = packet.read_location()
            index = packet.read_int(1)
            direct_attackable: bool = packet.read_bool()

            card = self.duel.get_card(controller, location, index)
            card.id = card_id
            card.can_direct_attack = direct_attackable
            card.attacked = False
            battle.attackable.append(card)

        battle.can_main2 = packet.read_bool()
        battle.can_end = packet.read_bool()

        selected: int = self.executor.select_battle_action(battle)
        reply: Packet = Packet(CtosMessage.RESPONSE)
        reply.write_int(selected)
        return reply


    def on_select_effect_yn(self, packet: Packet) -> Optional[Packet]:
        player_msg_sent_to: Player = self.duel.players[packet.read_int(1)]
        card_id: int = packet.read_id()
        controller: Player = self.duel.players[packet.read_int(1)]
        location: Location = packet.read_location()
        index: int = packet.read_int(4)
        position: Position = packet.read_position()
        description: int = packet.read_int(8)

        card: Card = self.duel.get_card(controller, location, index)
        card.id = card_id
        ans: bool = self.executor.select_effect_yn(card, description)

        reply: Packet = Packet(CtosMessage.RESPONSE)
        reply.write_int(ans)
        return reply


    def on_select_yesno(self, packet: Packet) -> Optional[Packet]:
        REPLAY_BATTLE = 30
        player_msg_sent_to: int = self.duel.players[packet.read_int(1)]
        desc: int = packet.read_int(8)
        if desc == REPLAY_BATTLE:
            ans: bool = self.executor.select_battle_replay()
        else:
            ans = self.executor.select_yn()
        reply: Packet = Packet(CtosMessage.RESPONSE)
        reply.write_bool(ans)
        return reply


    def on_select_option(self, packet: Packet) -> Optional[Packet]:
        player_msg_sent_to: int = packet.read_int(1)
        num_of_options: int = packet.read_int(1)
        options: list[int] = [packet.read_int(8) for _ in range(num_of_options)]
        ans: int = self.executor.select_option(options)

        reply: Packet = Packet(CtosMessage.RESPONSE)
        reply.write_int(ans)
        return reply


    def on_select_card(self, packet: Packet) -> Optional[Packet]:
        player_msg_sent_to: Player = self.duel.players[packet.read_int(1)]
        cancelable: bool = packet.read_bool()
        min_: int = packet.read_int(4) # min number of cards to select
        max_: int = packet.read_int(4) # max number of cards to select

        choices: list[Card] = []
        for _ in range(packet.read_int(4)):
            card_id: int = packet.read_id()
            controller: Player = self.duel.players[packet.read_int(1)]
            location: Location = packet.read_location()
            index: int = packet.read_int(4)
            position: Position = packet.read_position()
            card: Card = self.duel.get_card(controller, location, index)
            card.id = card_id
            choices.append(card)

        selected: list[int] = self.executor.select_card(choices, min_, max_, cancelable, self._select_hint)

        reply: Packet = Packet(CtosMessage.RESPONSE)
        reply.write_int(0)
        reply.write_int(len(selected))
        for i in selected:
            reply.write_int(i)
        return reply


    def on_select_chain(self, packet: Packet) -> Optional[Packet]:
        player_msg_sent_to: Player = self.duel.players[packet.read_int(1)]
        specount: int = packet.read_int(1)
        forced: bool = packet.read_bool()
        hint1: int = packet.read_int(4)
        hint2: int = packet.read_int(4)

        choices: list[Card] = []
        descriptions: list[int] = []

        for _ in range(packet.read_int(4)):
            card_id = packet.read_int(4)
            controller: Player = self.duel.players[packet.read_int(1)]
            location: Location = packet.read_location()
            index: int = packet.read_int(4)
            position: Position = packet.read_position()
            description: int = packet.read_int(8)
            card: Card = self.duel.get_card(controller, location, index)
            card.id = card_id
            choices.append(card)
            descriptions.append(description)
            operation_type: bytes = packet.read_bytes(1)

        reply: Packet = Packet(CtosMessage.RESPONSE)
        if len(choices) == 0:
            reply.write_int(-1)
        else:
            selected: int = self.executor.select_chain(choices, descriptions, forced)
            reply.write_int(selected)
        return reply


    def on_select_position(self, packet: Packet) -> Optional[Packet]:
        player_msg_sent_to: Player = self.duel.players[packet.read_int(1)]
        card_id: int = packet.read_id()
        selectable_position: int = packet.read_int(1)

        POSITION: list[Position.enum] = [
            Position.enum.FASEUP_ATTACK, 
            Position.enum.FASEDOWN_ATTACK, 
            Position.enum.FASEUP_DEFENCE, 
            Position.enum.FASEDOWN_DEFENCE
        ]
        
        choices: list[int] = [int(pos) for pos in POSITION if selectable_position & pos]
        selected: int = self.executor.select_position(card_id, choices)

        reply: Packet = Packet(CtosMessage.RESPONSE)
        reply.write_int(selected)
        return reply


    def on_select_tribute(self, packet: Packet) -> Packet:
        player_msg_sent_to: Player = self.duel.players[packet.read_int(1)]
        cancelable: bool = packet.read_bool()
        min_: int = packet.read_int(4) # min number of cards to select
        max_: int = packet.read_int(4) # max number of cards to select

        choices: list[Card] = []
        for _ in range(packet.read_int(4)):
            card_id: int = packet.read_id()
            controller: Player = self.duel.players[packet.read_int(1)]
            location: Location = packet.read_location()
            index: int = packet.read_int(4)
            packet.read_bytes(1)
            card: Card = self.duel.get_card(controller, location, index)
            card.id = card_id
            choices.append(card)

        selected: list[int] = self.executor.select_tribute(choices, min_, max_, cancelable, self._select_hint)

        reply: Packet = Packet(CtosMessage.RESPONSE)
        reply.write_int(0)
        reply.write_int(len(selected))
        for integer in selected:
            reply.write_int(integer)
        return reply


    def on_select_counter(self, packet: Packet) -> Optional[Packet]:
        player_msg_sent_to: Player = self.duel.players[packet.read_int(1)]
        counter_type: int = packet.read_int(2)
        quantity: int = packet.read_int(4)

        cards: list[Card] = []
        counters: list[int] = []

        for _ in range(packet.read_int(1)):
            card_id: int = packet.read_id()
            controller: Player = self.duel.players[packet.read_int(1)]
            location: Location = packet.read_location()
            index: int = packet.read_int(1)
            num_of_counter: int = packet.read_int(2)

            card: Card = self.duel.get_card(controller, location, index)
            card.id = card_id
            cards.append(card)
            counters.append(num_of_counter)

        used: list[int] = self.executor.select_counter(counter_type, quantity, cards, counters)

        reply: Packet = Packet(CtosMessage.RESPONSE)
        for i in used:
            reply.write_int(i, byte_size=2)
        return reply


    def on_select_sum(self, packet: Packet) -> Optional[Packet]:
        player_msg_sent_to: Player = self.duel.players[packet.read_int(1)]
        must_just: bool = not packet.read_bool()
        sum_value: int = packet.read_int(4)
        min_: int = packet.read_int(4)
        max_: int = packet.read_int(4)

        must_selected: list[Card] = []
        choices: list[tuple[Card, int, int]] = []

        for _ in range(packet.read_int(4)):
            card_id: int = packet.read_id()
            controller: Player = self.duel.players[packet.read_int(1)]
            location: Location = packet.read_location()
            index: int = packet.read_int(4)
            card: Card = self.duel.get_card(controller, location, index)
            card.id = card_id
            values: tuple[int, int] = (packet.read_int(2), packet.read_int(2))
            must_selected.append(card)
            sum_value -= max(values)

        for _ in range(packet.read_int(4)):
            card_id = packet.read_id()
            controller = self.duel.players[packet.read_int(1)]
            location = packet.read_location()
            index = packet.read_int(4)
            card = self.duel.get_card(controller, location, index)
            card.id = card_id
            values = (packet.read_int(2), packet.read_int(2))
            choices.append((card, *values))

        selected: list[int] = self.executor.select_sum(choices, sum_value, min_, max_, must_just, self._select_hint)

        reply: Packet = Packet(CtosMessage.RESPONSE)
        reply.write_bytes(b'\x00\x01\x00\x00')
        reply.write_int(len(must_selected)+len(selected), byte_size=4)
        for _ in must_selected:
            packet.write_int(0, byte_size=1)
        for i in selected:
            packet.write_int(i, byte_size=1)
        return reply


    def on_select_place(self, packet: Packet) -> Optional[Packet]:
        player_msg_sent_to: Player = self.duel.players[packet.read_int(1)]
        min_: int = packet.read_int(1)
        selectable: int = 0xffffffff - packet.read_int(4)

        is_pzone: bool = bool(selectable & (ZoneID.PZONE | (ZoneID.PZONE << ZoneID.OPPONENT)))
        if selectable & ZoneID.MONSTER_ZONE:
            player = Player.ME
            location = Location(Location.enum.MONSTER_ZONE)

        elif selectable & ZoneID.SPELL_ZONE:
            player = Player.ME
            location = Location(Location.enum.SPELL_ZONE)

        elif selectable & (ZoneID.MONSTER_ZONE << ZoneID.OPPONENT):
            player = Player.OPPONENT
            location = Location(Location.enum.MONSTER_ZONE)

        elif selectable & (ZoneID.SPELL_ZONE << ZoneID.OPPONENT):
            player = Player.OPPONENT
            location = Location(Location.enum.SPELL_ZONE)
        

        zones: list[Zone] = self.duel.field[player].where_zones(location)
        choices: list[int] = [i for i, zone in enumerate(zones) if bool(selectable & zone.id)]
        selected: int = self.executor.select_place(player, choices)

        reply: Packet = Packet(CtosMessage.RESPONSE)
        reply.write_int(self.duel.players.index(player), byte_size=1)
        reply.write_int(location.value, byte_size=1)
        reply.write_int(selected, byte_size=1)
        return reply


    def on_select_unselect(self, packet: Packet) -> Optional[Packet]:
        player_msg_snt_to: Player = self.duel.players[packet.read_int(1)]
        finishable: bool = packet.read_bool()
        cancelable: bool = packet.read_bool() or finishable
        min: int = packet.read_int(4)
        max: int = packet.read_int(4)

        cards: list[Card] = []

        for _ in range(packet.read_int(4)):
            card_id: int = packet.read_id()
            controller: Player = self.duel.players[packet.read_int(1)]
            location: Location = packet.read_location()
            index: int = packet.read_int(4)
            position: Position = packet.read_position()

            card: Card = self.duel.get_card(controller, location, index)
            card.id = card_id
            card.position = position
            cards.append(card)

        # unknown  
        for _ in range(packet.read_int(4)):
            card_id = packet.read_id()
            controller = self.duel.players[packet.read_int(1)]
            location = packet.read_location()
            index = packet.read_int(4)
            position = packet.read_position()

        max = 1
        selected: list[int] = self.executor.select_unselect(cards, int(not finishable), max, cancelable, self._select_hint)

        reply: Packet = Packet(CtosMessage.RESPONSE)
        if len(selected) == 0:
            reply.write_int(-1)
        else:
            reply.write_int(len(selected))
            for integer in selected:
                reply.write_int(integer)
        return reply


    def on_announce_race(self, packet: Packet) -> Optional[Packet]:
        player_msg_sent_to: Player = self.duel.players[packet.read_int(1)]
        count: int = packet.read_int(1)
        available: int = packet.read_int(4)
        choices: list[int] = [int(race) for race in Race.enum if available & race]

        selected: list[int] = self.executor.announce_race(choices, count)

        reply: Packet = Packet(CtosMessage.RESPONSE)
        reply.write_int(sum(selected))
        return reply


    def on_announce_card(self, packet: Packet) -> Optional[Packet]:
        raise NotImplementedError()


    def on_announce_attr(self, packet: Packet) -> Optional[Packet]:
        player_msg_sent_to: Player = self.duel.players[packet.read_int(1)]
        count: int = packet.read_int(1)
        available: int = packet.read_int(4)
        choices: list[int] = [int(attr) for attr in Attribute.enum if available & attr]

        selected: list[int] = self.executor.announce_attr(choices, count)

        reply: Packet = Packet(CtosMessage.RESPONSE)
        reply.write_int(sum(selected))
        return reply


    def on_announce_number(self, packet: Packet) -> Optional[Packet]:
        player_msg_sent_to: Player = self.duel.players[packet.read_int(1)]
        count: int = packet.read_int(1)
        choices: list[int] = [packet.read_int(4) for _ in range(count)]
        selected: int = self.executor.select_number(choices)

        reply: Packet = Packet(CtosMessage.RESPONSE)
        reply.write_int(selected)
        return reply


    def on_update_data(self, packet: Packet) -> Optional[Packet]:
        player: Player = self.duel.players[packet.read_int(1)]
        location: Location = packet.read_location()
        size: int = packet.read_int(4)
        cards: list[Optional[Card]] = self.duel.get_cards(player, location)
        for card in cards:
            if card:
                self._update_card(card, packet)
            else:
                packet.read_bytes(2) # read \x00\x00, which means no card
        return None
        

    def on_update_card(self, packet: Packet) -> Optional[Packet]:
        player: Player = self.duel.players[packet.read_int(1)]
        location: Location = packet.read_location()
        index: int = packet.read_int(1)

        card: Card = self.duel.get_card(player, location, index)
        self._update_card(card, packet)
        return None


    def _update_card(self, card: Card, packet: Packet) -> None:
        while True:
            size: int = packet.read_int(2)
            if size == 0:
                return

            query: int = packet.read_int(4)

            if query == Query.ID:
                card.id = packet.read_int(4)

            elif query == Query.POSITION:
                card.position = Position(packet.read_int(4))

            elif query == Query.ALIAS:
                card.arias = packet.read_int(4)

            elif query == Query.TYPE:
                card.type = Type(packet.read_int(4))

            elif query == Query.LEVEL:
                card.level = packet.read_int(4)

            elif query == Query.RANK:
                card.rank = packet.read_int(4)

            elif query == Query.ATTRIBUTE:
                card.attribute = Attribute(packet.read_int(4))

            elif query == Query.RACE:
                card.race = Race(packet.read_int(4))

            elif query == Query.ATTACK:
                card.attack = packet.read_int(4)

            elif query == Query.DEFENCE:
                card.defence = packet.read_int(4)

            elif query == Query.BASE_ATTACK:
                card.base_attack = packet.read_int(4)

            elif query == Query.BASE_DEFENCE:
                card.base_defence = packet.read_int(4)

            elif query == Query.REASON:
                card.reason = packet.read_int(4)

            elif query == Query.REASON_CARD:
                controller = self.duel.players[packet.read_int(1)]
                location = packet.read_location()
                index = packet.read_int(4)
                position = packet.read_position()
                card.reason_card = self.duel.get_card(controller, location, index)

            elif query == Query.EQUIP_CARD:
                controller = self.duel.players[packet.read_int(1)]
                location = packet.read_location()
                index = packet.read_int(4)
                position = packet.read_position()
                ecard: Card = self.duel.get_card(controller, location, index)
                card.equip_target = ecard
                ecard.equip_cards.append(card)

            elif query == Query.TARGET_CARD:
                card.target_cards.clear()
                for _ in range(packet.read_int(4)):
                    controller = self.duel.players[packet.read_int(1)]
                    location = packet.read_location()
                    index = packet.read_int(4)
                    position = packet.read_position()
                    tcard = self.duel.get_card(controller, location, index)
                    card.target_cards.append(tcard)
                    tcard.targeted_by.append(card)

            elif query == Query.OVERLAY_CARD:
                card.overlays.clear()
                for _ in range(packet.read_int(4)):
                    card.overlays.append(packet.read_id())

            elif query == Query.COUNTERS:
                card.counters.clear()
                for _ in range(packet.read_int(4)):
                    counter_info: int = packet.read_int(4)
                    counter_type: int = counter_info & 0xffff
                    counter_count: int = counter_info >> 16
                    card.counters[counter_type] = counter_count
            
            elif query == Query.CONTROLLER:
                card.controller = self.duel.players[packet.read_int(1)]

            elif query == Query.STATUS:
                card.status = packet.read_int(4)

            elif query == Query.IS_PUBLIC:
                is_public: bool = packet.read_bool()

            elif query == Query.LSCALE:
                card.lscale = packet.read_int(4)

            elif query == Query.RSCALE:
                card.rscale = packet.read_int(4)

            elif query == Query.LINK:
                card.link = packet.read_int(4)
                card.linkmarker = packet.read_int(4)
            
            elif query == Query.IS_HIDDEN:
                pass

            elif query == Query.COVER:
                pass

            elif query == Query.END:
                return

            else:
                packet.read_bytes(size - 4) # 4 is bytesize of 'query'


    def on_shuffle_deck(self, packet: Packet) -> Optional[Packet]:
        player: Player = self.duel.players[packet.read_int(1)]
        for card in self.duel.field[player].deck:
            card.id = 0
        return None


    def on_shuffle_hand(self, packet: Packet) -> Optional[Packet]:
        player: Player = self.duel.players[packet.read_int(1)]
        num_of_hand: int = packet.read_int(4)
        for card in self.duel.field[player].hand:
            card.id = packet.read_int(4)
        return None


    def on_shuffle_extra(self, packet: Packet) -> Optional[Packet]:
        player: Player = self.duel.players[packet.read_int(1)]
        num_of_extra: int = packet.read_int(4)
        for card in self.duel.field[player].extradeck:
            if not card.is_faceup:
                card.id = packet.read_int(4)
        return None

    def on_shuffle_setcard(self, packet: Packet) -> Optional[Packet]:
        location: Location = packet.read_location()
        count: int = packet.read_int(1)

        old: list[Card] = []
        for _ in range(count):
            controller: Player = self.duel.players[packet.read_int(1)]
            location = packet.read_location()
            index: int = packet.read_int(4)
            position: Position = packet.read_position()
            card: Card = self.duel.get_card(controller, location, index)
            card.id = 0
            old.append(card)

        for i in range(count):
            controller = self.duel.players[packet.read_int(1)]
            location = packet.read_location()
            index = packet.read_int(4)
            position = packet.read_position()
            self.duel.add_card(old[i], controller, location, index)
        return None

    def on_sort_card(self, packet: Packet) -> Optional[Packet]:
        player_msg_sent_to: Player = self.duel.players[packet.read_int(1)]
        cards: list[Card] = []
        for _ in range(packet.read_int(4)):
            card_id = packet.read_id()
            controller: Player = self.duel.players[packet.read_int(1)]
            location: Location = packet.read_location()
            index: int = packet.read_int(4)
            card: Card = self.duel.get_card(controller, location, index)
            card.id = card_id
            cards.append(card)
        
        selected: list[int] = self.executor.sort_card(cards)
        
        reply: Packet = Packet(CtosMessage.RESPONSE)
        for integer in selected:
            reply.write_int(integer, byte_size=1)
        return reply


    def on_sort_chain(self, packet: Packet) -> Optional[Packet]:
        reply: Packet = Packet(CtosMessage.RESPONSE)
        reply.write_int(-1)
        return reply


    def on_move(self, packet: Packet) -> Optional[Packet]:
        card_id: int = packet.read_id()
        # p means previous, c means current
        p_controller: Player = self.duel.players[packet.read_int(1)]
        p_location: Location = packet.read_location()
        p_index: int = packet.read_int(4)
        p_position: Position = packet.read_position()
        c_controller: Player = self.duel.players[packet.read_int(1)]
        c_location: Location = packet.read_location()
        c_index: int = packet.read_int(4)
        c_position: Position = packet.read_position()
        reason: int = packet.read_int(4)

        card: Card = self.duel.get_card(p_controller, p_location, p_index)
        card.id = card_id
        self.duel.remove_card(card, p_controller, p_location, p_index)
        self.duel.add_card(card, c_controller, c_location, c_index)
        return None


    def on_poschange(self, packet: Packet) -> Optional[Packet]:
        card_id: int = packet.read_id()
        # p means previous, c means current
        p_controller: Player = self.duel.players[packet.read_int(1)]
        p_location: Location = packet.read_location()
        p_index: int = packet.read_int(1)
        p_position: Position = Position(packet.read_int(1))
        c_position: Position = Position(packet.read_int(1))

        card: Card = self.duel.get_card(p_controller, p_location, p_index)
        card.position = c_position
        return None


    def on_set(self, packet: Packet) -> Optional[Packet]:
        return None


    def on_swap(self, packet: Packet) -> Optional[Packet]:
        # p means previous, c means current
        card_id_1: int = packet.read_id()
        controller_1: Player = self.duel.players[packet.read_int(1)]
        location_1: Location = packet.read_location()
        index_1: int = packet.read_int(4)
        position_1: Position = packet.read_position()
        card_id_2: int = packet.read_id()
        controller_2: Player = self.duel.players[packet.read_int(1)]
        location_2: Location = packet.read_location()
        index_2: int = packet.read_int(4)
        position_2: Position = packet.read_position()

        card_1: Card = self.duel.get_card(controller_1, location_1, index_1)
        card_1.id = card_id_1
        card_2: Card = self.duel.get_card(controller_2, location_2, index_2)
        card_2.id = card_id_2

        self.duel.remove_card(card_1, controller_1, location_1, index_1)
        self.duel.remove_card(card_2, controller_2, location_2, index_2)
        self.duel.add_card(card_1, controller_2, location_2, index_2)
        self.duel.add_card(card_2, controller_1, location_1, index_1)
        return None


    def on_summoning(self, packet: Packet) -> Optional[Packet]:
        card_id: int = packet.read_id()
        controller: Player = self.duel.players[packet.read_int(1)]
        location: Location = packet.read_location()
        index: int = packet.read_int(4)
        position: Position = packet.read_position()
        card: Card = self.duel.get_card(controller, location, index)
        card.id = card_id
        self.duel.on_summoning(controller, card)
        return None


    def on_summoned(self, packet: Packet) -> Optional[Packet]:
        self.duel.on_summoned()
        return None


    def on_spsummoning(self, packet: Packet) -> Optional[Packet]:
        card_id: int = packet.read_id()
        controller: Player = self.duel.players[packet.read_int(1)]
        location: Location = packet.read_location()
        index: int = packet.read_int(4)
        position: Position = packet.read_position()
        card: Card = self.duel.get_card(controller, location, index)
        card.id = card_id
        self.duel.on_summoning(controller, card)
        return None


    def on_spsummoned(self, packet: Packet) -> Optional[Packet]:
        self.duel.on_spsummoned()
        return None


    def on_chaining(self, packet: Packet) -> Optional[Packet]:
        card_id: int = packet.read_id()
        controller: Player = self.duel.players[packet.read_int(1)]
        location: Location = packet.read_location()
        index: int = packet.read_int(4)
        position: Position = packet.read_position()
        card: Card = self.duel.get_card(controller, location, index)
        card.id = card_id
        last_chain_player: Player = self.duel.players[packet.read_int(1)]
        self.duel.on_chaining(last_chain_player, card)
        return None


    def on_chain_end(self, packet: Packet) -> Optional[Packet]:
        self.duel.on_chain_end()
        return None


    def on_become_target(self, packet: Packet) -> Optional[Packet]:
        for _ in range(packet.read_int(4)):
            controller: Player = self.duel.players[packet.read_int(1)]
            location: Location = packet.read_location()
            index: int = packet.read_int(4)
            position: Position = packet.read_position()
            card: Card = self.duel.get_card(controller, location, index)
            self.duel.on_become_target(card)
        return None


    def on_draw(self, packet: Packet) -> Optional[Packet]:
        player: Player = self.duel.players[packet.read_int(1)]
        for _ in range(packet.read_int(4)):
            self.duel.on_draw(player)
        return None


    def on_damage(self, packet: Packet) -> Optional[Packet]:
        player: Player = self.duel.players[packet.read_int(1)]
        damage: int = packet.read_int(4)
        self.duel.on_damage(player, damage)
        return None


    def on_recover(self, packet: Packet) -> Optional[Packet]:
        player: Player = self.duel.players[packet.read_int(1)]
        recover: int = packet.read_int(4)
        self.duel.on_recover(player, recover)
        return None


    def on_equip(self, packet: Packet) -> Optional[Packet]:
        controller_1: Player = self.duel.players[packet.read_int(1)]
        location_1: Location = packet.read_location()
        index_1: int = packet.read_int(4)
        position_1: Position = packet.read_position()
        controller_2: Player = self.duel.players[packet.read_int(1)]
        location_2: Location = packet.read_location()
        index_2: int = packet.read_int(4)
        position_2: Position = packet.read_position()

        equip: Card = self.duel.get_card(controller_1, location_1, index_1)
        equipped: Card = self.duel.get_card(controller_2, location_2, index_2)

        if equip.equip_target is not None:
            equip.equip_target.equip_cards.remove(equip)
        equip.equip_target = equipped
        equipped.equip_cards.append(equip)
        return None


    def on_unequip(self, packet: Packet) -> Optional[Packet]:
        controller: Player = self.duel.players[packet.read_int(1)]
        location: Location = packet.read_location()
        index: int = packet.read_int(4)
        position: Position = packet.read_position()
        equip: Card = self.duel.get_card(controller, location, index)
        if equip.equip_target:
            equip.equip_target.equip_cards.remove(equip)
        equip.equip_target = None
        return None


    def on_lp_update(self, packet: Packet) -> Optional[Packet]:
        player: Player = self.duel.players[packet.read_int(1)]
        lp: int = packet.read_int(4)
        self.duel.on_lp_update(player, lp)
        return None


    def on_card_target(self, packet: Packet) -> Optional[Packet]:
        controller_1: Player = self.duel.players[packet.read_int(1)]
        location_1: Location = packet.read_location()
        index_1: int = packet.read_int(4)
        position_1: Position = packet.read_position()
        controller_2: Player = self.duel.players[packet.read_int(1)]
        location_2: Location = packet.read_location()
        index_2: int = packet.read_int(4)
        position_2: Position = packet.read_position()
        targeting: Card = self.duel.get_card(controller_1, location_1, index_1)
        targeted: Card = self.duel.get_card(controller_2, location_2, index_2)
        targeting.target_cards.append(targeted)
        targeted.targeted_by.append(targeting)
        return None


    def on_cancel_target(self, packet: Packet) -> Optional[Packet]:
        controller_1: Player = self.duel.players[packet.read_int(1)]
        location_1: Location = packet.read_location()
        index_1: int = packet.read_int(4)
        position_1: Position = packet.read_position()
        controller_2: Player = self.duel.players[packet.read_int(1)]
        location_2: Location = packet.read_location()
        index_2: int = packet.read_int(4)
        position_2: Position = packet.read_position()
        targeting: Card = self.duel.get_card(controller_1, location_1, index_1)
        targeted: Card = self.duel.get_card(controller_2, location_2, index_2)
        targeting.target_cards.remove(targeted)
        targeted.targeted_by.remove(targeting)
        return None


    def on_attack(self, packet: Packet) -> Optional[Packet]:
        controller_1: Player = self.duel.players[packet.read_int(1)]
        location_1: Location = packet.read_location()
        index_1: int = packet.read_int(4)
        position_1: Position = packet.read_position()
        controller_2: Player = self.duel.players[packet.read_int(1)]
        location_2: Location = packet.read_location()
        index_2: int = packet.read_int(4)
        position_2: Position = packet.read_position()
        attacking: Card = self.duel.get_card(controller_1, location_1, index_1)
        attacked: Card = self.duel.get_card(controller_2, location_2, index_2)
        self.duel.on_attack(attacking, attacked)
        return None
        

    def on_battle(self, packet: Packet) -> Optional[Packet]:
        self.duel.on_battle()
        return None


    def on_attack_disabled(self, packet: Packet) -> Optional[Packet]:
        self.duel.on_battle()
        return None


    def on_rock_paper_scissors(self, packet: Packet) -> Optional[Packet]:
        return None


    def on_tag_swap(self, packet: Packet) -> Optional[Packet]:
        raise NotImplementedError()
