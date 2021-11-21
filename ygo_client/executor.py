from abc import ABC, abstractmethod
from typing import List, Tuple

from ygo_core import Deck, Card
from ygo_core.enums import Player
from ygo_core.phase import MainPhase, BattlePhase


class DuelExecutor(ABC):

    @abstractmethod
    def on_start(self) -> None:
        """ Called when a new game starts. """
        raise NotImplementedError()


    @abstractmethod
    def on_new_turn(self) -> None:
        """ Called when a new turn starts. """
        raise NotImplementedError()


    @abstractmethod
    def on_new_phase(self) -> None:
        """ Called when a new phase starts. """
        raise NotImplementedError()


    @abstractmethod
    def on_win(self, win: bool) -> None:
        """ Called when a game ends. """
        raise NotImplementedError()

    
    @abstractmethod
    def rematch(self, win_on_match: bool) -> bool:
        """ Called when a match ends.\n
        Return True if you want to rematch. """
        raise NotImplementedError()


    @abstractmethod
    def select_hand(self) -> int:
        raise NotImplementedError()


    @abstractmethod
    def select_tp(self) -> bool:
        """ Return True if you go first """
        pass

    @abstractmethod
    def select_mainphase_action(self, main: MainPhase) -> int:
        pass


    @abstractmethod
    def select_battle_action(self, battle: BattlePhase) -> int:
        pass


    @abstractmethod
    def select_effect_yn(self, card: Card, description: int) -> bool:
        pass


    @abstractmethod
    def select_yn(self) -> bool:
        pass


    @abstractmethod
    def select_battle_replay(self) -> bool:
        pass

    
    @abstractmethod
    def select_option(self, options: List[int]) -> int:
        pass


    @abstractmethod
    def select_card(self, choices: List[Card], min_: int, max_: int, cancelable: bool, select_hint: int) -> List[int]:
        pass

    
    @abstractmethod
    def select_tribute(self, choices: List[Card], min_: int, max_: int, cancelable: bool, select_hint: int) -> List[int]:
        pass
    

    @abstractmethod
    def select_chain(self, choices: List[Card], descriptions: List[int], forced: bool) -> int:
        pass


    @abstractmethod
    def select_place(self, player: Player, choices: List[int]) -> int:
        pass


    @abstractmethod
    def select_position(self, card_id: int, choices: List[int]) -> int:
        pass


    @abstractmethod
    def select_sum(self, choices: List[Tuple[Card, int, int]], sum_value: int, min_: int, max_: int, must_just: bool, select_hint: int) -> List[int]:
        pass


    @abstractmethod
    def select_unselect(self, choices: List[Card], min_: int, max_: int, cancelable: bool, hint: int) -> list[int]:
        pass


    @abstractmethod
    def select_counter(self, counter_type: int, quantity: int, cards: List[Card], counters: List[int]) -> List[int]:
        pass


    @abstractmethod
    def select_number(self, choices: List[int]) -> int:
        pass


    @abstractmethod
    def sort_card(self, cards: List[Card]) -> List[int]:
        pass


    @abstractmethod
    def announce_attr(self, choices: List[int], count: int) -> List[int]:
        pass


    @abstractmethod
    def announce_race(self, choices: List[int], count: int) -> List[int]:
        pass


    @abstractmethod
    def change_side(self, deck: Deck) -> None:
        pass