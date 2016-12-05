from enum import Enum, IntEnum
from collections import namedtuple, defaultdict
from itertools import combinations
import random


class Suits(Enum):
    SPADES = "\U00002660"
    HEARTS = "\U00002661"
    CLUBS = "\U00002663"
    DIAMONDS = "\U00002662"

    def __str__(c):
        return c.value


class PokerHands(IntEnum):
    ROYAL_FLUSH = 9
    STRAIGHT_FLUSH = 8
    FOUR_OF_A_KIND = 7
    FULL_HOUSE = 6
    FLUSH = 5
    STRAIGHT = 4
    THREE_OF_A_KIND = 3
    TWO_PAIR = 2
    PAIR = 1

    def __str__(c):
        return { PokerHands.ROYAL_FLUSH: "Royal Flush",
                 PokerHands.STRAIGHT_FLUSH: "Straight Flush",
                 PokerHands.FOUR_OF_A_KIND: "Four of a Kind",
                 PokerHands.FULL_HOUSE: "Full House",
                 PokerHands.FLUSH: "Flush",
                 PokerHands.STRAIGHT: "Straight",
                 PokerHands.THREE_OF_A_KIND: "Three of a Kind",
                 PokerHands.TWO_PAIR: "Two Pair",
                 PokerHands.PAIR: "Pair" }[c]


Card = namedtuple("Card", ["rank", "suit"])


def create_deck():
    return [Card(rank, suit) for suit in Suits
                             for rank in ['A', 2, 3, 4, 5, 6, 7, 8, 9, 10, 'J', 'Q', 'K']]


def shuffled(cards):
    return random.sample(cards, len(cards))


def aces_low(card):
    r = card.rank
    return r if isinstance(r, int) else {'A':1, 'J':11, 'Q':12, 'K':13}[r]


def aces_high(card):
    r = card.rank
    return r if isinstance(r, int) else {'A':14, 'J':11, 'Q':12, 'K':13}[r]


def high_card(cards, keyFn=aces_high):
    return max(cards, key=keyFn)


def group_by_rank(cards):
    def _importance(s):
        """Largest groups first; same-size groups ordered by rank, highest first."""
        return (len(s), aces_high(s.copy().pop()))

    groups = defaultdict(set)
    for card in cards:
        groups[card.rank].add(card)
    return sorted(groups.values(), key=_importance, reverse=True)


def is_pair(cards):
    return len(group_by_rank(cards)[0]) >= 2


def is_two_pair(cards):
    groups = group_by_rank(cards)
    return len(groups[0])==4 or (len(groups)>=2 and len(groups[1])>=2)


def is_three_of_a_kind(cards):
    return len(group_by_rank(cards)[0]) >= 3


def is_straight(hand):
    def _is_straight(hand, keyFn):
        ranks = {keyFn(card) for card in hand}
        return len(ranks) == 5 and max(ranks)-min(ranks) == 4

    return _is_straight(hand, aces_low) or _is_straight(hand, aces_high)


def is_flush(cards):
    return len({card.suit for card in cards}) == 1


def is_full_house(hand):
    groups = group_by_rank(hand)
    return len(groups) == 2 and len(groups[0]) == 3


def is_four_of_a_kind(cards):
    return len(group_by_rank(cards)[0]) == 4


def is_royal_straight(hand):
    return is_straight(hand) and min(hand, key=aces_high).rank == 10


def Card_to_str(card):
    return "{}{}".format(str(card.rank), str(card.suit))


def hand_to_str(hand):
    key = aces_high
    if is_straight(hand) and not is_royal_straight(hand):
        key = aces_low
    return ", ".join([Card_to_str(card) for card in sorted(hand, key=key)])


def characterize_hand(hand):
    def _tie_breaker(hand):
        return tuple(aces_high(s.pop()) for s in group_by_rank(hand))

    if is_royal_straight(hand) and is_flush(hand):
        result = (PokerHands.ROYAL_FLUSH,)
    elif is_straight(hand) and is_flush(hand):
        tieBreaker = aces_low(high_card(hand))
        result = (PokerHands.STRAIGHT_FLUSH, tieBreaker)
    elif is_four_of_a_kind(hand):
        tieBreaker = aces_high(group_by_rank(hand)[0].pop())
        result = (PokerHands.FOUR_OF_A_KIND, tieBreaker)
    elif is_full_house(hand):
        tieBreaker = aces_high(group_by_rank(hand)[0].pop())
        result = (PokerHands.FULL_HOUSE, tieBreaker)
    elif is_flush(hand):
        keyFn = aces_high
        tieBreaker = tuple([keyFn(card) for card in sorted(hand, key=keyFn, reverse=True)])
        result = (PokerHands.FLUSH,) + tieBreaker
    elif is_straight(hand):
        keyFn = aces_high if is_royal_straight(hand) else aces_low
        tieBreaker = keyFn(high_card(hand, keyFn))
        result = (PokerHands.STRAIGHT, tieBreaker)
    elif is_three_of_a_kind(hand):
        result = (PokerHands.THREE_OF_A_KIND,) + _tie_breaker(hand)
    elif is_two_pair(hand):
        result = (PokerHands.TWO_PAIR,) + _tie_breaker(hand)
    elif is_pair(hand):
        result = (PokerHands.PAIR,) + _tie_breaker(hand)
    else:
        result = (0,) + _tie_breaker(hand)
    return result


def choose_best_hand(cards):
    best = None
    for hand in combinations(cards, 5):
        c = characterize_hand(hand)
        if best is None or c > best:
            best = c
            best_hand = hand
    return best_hand
