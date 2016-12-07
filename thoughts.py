from enum import Enum, IntEnum
from collections import namedtuple, defaultdict
from itertools import combinations
import random


class Suits(Enum):
    SPADES = "\U00002660"
    HEARTS = "\U00002661"
    CLUBS = "\U00002663"
    DIAMONDS = "\U00002662"

    def __str__(e):
        return e.value


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

    def __str__(e):
        return { PokerHands.ROYAL_FLUSH: "Royal Flush",
                 PokerHands.STRAIGHT_FLUSH: "Straight Flush",
                 PokerHands.FOUR_OF_A_KIND: "Four of a Kind",
                 PokerHands.FULL_HOUSE: "Full House",
                 PokerHands.FLUSH: "Flush",
                 PokerHands.STRAIGHT: "Straight",
                 PokerHands.THREE_OF_A_KIND: "Three of a Kind",
                 PokerHands.TWO_PAIR: "Two Pair",
                 PokerHands.PAIR: "Pair" }[e]


Card = namedtuple("Card", ["rank", "suit"])


def create_deck():
    return [Card(rank, suit) for suit in Suits
                             for rank in ['A', 2, 3, 4, 5, 6, 7, 8, 9, 10, 'J', 'Q', 'K']]


# The following functions all take a number of Cards as a parameter.
# The parameter names have meaning:
#
#   card    a Card
#   cards   an iterable: any number of cards
#   hand    an iterable: 5 distinct Cards
#   deck    an iterable: 52 distinct Cards


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
    """
    Sort cards into a list of sets, where each set contains all the
    cards of a single rank.  Sort largest sets first; same-size sets
    ordered by rank, highest first.
    """

    def _importance(s):
        return (len(s), aces_high(s.copy().pop()))

    groups = defaultdict(set)
    for card in cards:
        groups[card.rank].add(card)
    return sorted(groups.values(), key=_importance, reverse=True)


def is_pair(cards, groups=None):
    if groups is None:
        groups = group_by_rank(cards)
    # it's a pair if any group (we'll try the largest first)
    # has two or more cards in it.
    return len(groups[0]) >= 2


def is_two_pair(cards, groups=None):
    if groups is None:
        groups = group_by_rank(cards)
    # It's two-pair if it's four-of-a-kind _or_ if there are at least
    # two groups with at least two cards in each.
    return len(groups[0])==4 or (len(groups)>=2 and len(groups[1])>=2)


def is_three_of_a_kind(cards, groups=None):
    if groups is None:
        groups = group_by_rank(cards)
    # It's three-of-a-kind if the largest group has at least 3 cards in it.
    return len(groups[0]) >= 3


def is_straight(hand):
    def _is_straight(hand, keyFn):
        # It's a straight if all five cards are different ranks and span
        # the length of a straight (4 single-steps between the five cards).
        ranks = {keyFn(card) for card in hand}
        return len(ranks) == 5 and max(ranks)-min(ranks) == 4

    # Check it it's a straight both ways: aces low, or aces high
    return _is_straight(hand, aces_low) or _is_straight(hand, aces_high)


def is_flush(cards):
    # It's a flush if the set of all the suits present contains only one
    # suit.
    return len({card.suit for card in cards}) == 1


def is_full_house(cards, groups=None):
    if groups is None:
        groups = group_by_rank(cards)
    # It's a full-house if there's a group of at least three and another
    # group of at least two.
    return len(groups)>=2 and len(groups[0])>=3 and len(groups[1])>=2


def is_four_of_a_kind(cards, groups=None):
    if groups is None:
        groups = group_by_rank(cards)
    # It's four-of-a-kind if the largest group contains all four cards
    # of that rank.
    return len(groups[0]) == 4


def is_royal_straight(hand):
    return is_straight(hand) and min(hand, key=aces_high).rank == 10


def Card_to_str(card):
    return "{}{}".format(str(card.rank), str(card.suit))


def hand_to_str(hand):
    keyFn = aces_high
    if is_straight(hand) and not is_royal_straight(hand):
        keyFn = aces_low
    return ", ".join([Card_to_str(card) for card in sorted(hand, key=keyFn)])


def characterize_hand(hand):
    """
    Return a tuple whose first element is the PokerHands constant
    identifying this hand, and whose remaining elements are tie-breakers
    according to the type of hand.  The results are directly comparable.
    E.g., if characterize_hand(h0) > characterize_hand(h1), then h0
    beats h1 according to the rules of Poker.
    """

    def _tie_breaker(hand, groups):
        return tuple(aces_high(s.pop()) for s in groups)

    groups = group_by_rank(hand)

    if len(groups)==5 and not is_straight(hand):
        result = (0,) + _tie_breaker(hand, groups)
    elif is_royal_straight(hand) and is_flush(hand):
        result = (PokerHands.ROYAL_FLUSH,)
    elif is_straight(hand) and is_flush(hand):
        keyFn = aces_low
        tieBreaker = keyFn(high_card(hand, keyFn))
        result = (PokerHands.STRAIGHT_FLUSH, tieBreaker)
    elif is_four_of_a_kind(hand, groups):
        tieBreaker = aces_high(groups[0].pop())
        result = (PokerHands.FOUR_OF_A_KIND, tieBreaker)
    elif is_full_house(hand, groups):
        tieBreaker = aces_high(groups[0].pop())
        result = (PokerHands.FULL_HOUSE, tieBreaker)
    elif is_flush(hand):
        keyFn = aces_high
        tieBreaker = tuple([keyFn(card) for card in sorted(hand, key=keyFn, reverse=True)])
        result = (PokerHands.FLUSH,) + tieBreaker
    elif is_straight(hand):
        keyFn = aces_high if is_royal_straight(hand) else aces_low
        tieBreaker = keyFn(high_card(hand, keyFn))
        result = (PokerHands.STRAIGHT, tieBreaker)
    elif is_three_of_a_kind(hand, groups):
        result = (PokerHands.THREE_OF_A_KIND,) + _tie_breaker(hand, groups)
    elif is_two_pair(hand, groups):
        result = (PokerHands.TWO_PAIR,) + _tie_breaker(hand, groups)
    elif is_pair(hand, groups):
        result = (PokerHands.PAIR,) + _tie_breaker(hand, groups)
    return result


def choose_best_hand(cards):
    """
    Return the best 5-card hand that can be made from the cards in cards.
    Typically, len(cards)==7, but any number is allowed.
    """

    best = None
    for hand in combinations(cards, 5):
        c = characterize_hand(hand)
        if best is None or c > best:
            best = c
            best_hand = hand
            # optimization
            if best[0] == PokerHands.ROYAL_FLUSH:
                break
    return best_hand
