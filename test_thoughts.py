import unittest
from thoughts import *

class TestThoughts(unittest.TestCase):
    def setUp(self):
        self.deck = shuffled(create_deck())
        self.hand = {Card('K', Suits.DIAMONDS), Card('A', Suits.CLUBS), Card(2, Suits.CLUBS), Card(5, Suits.HEARTS), Card(5, Suits.SPADES)}

    def test_suits_are_iterable(self):
        self.assertSetEqual(set(Suits), {Suits.SPADES, Suits.HEARTS, Suits.CLUBS, Suits.DIAMONDS})

    def test_suits_convert_to_strings(self):
        c = str(Suits.SPADES)
        self.assertEqual(c, "♠")

    def test_suits_compare_for_equality(self):
        self.assertNotEqual(Suits.SPADES, Suits.HEARTS)

    def test_suits_dont_compare(self):
        with self.assertRaises(TypeError):
            Suits.SPADES > Suits.DIAMONDS

    def test_hands_are_iterable(self):
        foundHands = [h.value for h in PokerHands]
        self.assertEqual(foundHands, list(range(9, 0, -1)))

    def test_ordered_hands(self):
        self.assertGreater(PokerHands.ROYAL_FLUSH, PokerHands.STRAIGHT)

    def test_card_is_immutable(self):
        card = Card('K', Suits.DIAMONDS)
        with self.assertRaises(AttributeError):
            card.suit = Suits.HEARTS

    def test_deck_is_52_distinct_cards(self):
        self.assertEqual(len(set(self.deck)), 52)
        self.assertEqual(len(self.deck), 52)

    def test_ace_of_spades_in_deck(self):
        self.assertIn(Card('A', Suits.SPADES), self.deck)
        foundAces = {card for card in self.deck if card.rank == 'A'}
        self.assertEqual(len(foundAces), 4)

    def test_shuffle(self):
        d0 = self.deck[:]
        d1 = shuffled(d0)
        self.assertNotEqual(d0, d1)
        self.assertSetEqual(set(d0), set(d1))

    def test_card_ordering(self):
        with self.assertRaises(TypeError):
            hand = sorted(self.hand)
        hand = sorted(self.hand, key=aces_low)
        self.assertEqual(hand[0].rank, 'A')
        hand = sorted(self.hand, key=aces_high)
        self.assertEqual(hand[4].rank, 'A')
        self.assertEqual(hand[0].rank, 2)
        self.assertEqual(high_card(self.hand).rank, 'A')
        self.assertEqual(high_card(self.hand, aces_low).rank, 'K')

    def test_is_pair(self):
        cards = {Card('A', Suits.CLUBS), Card(2, Suits.DIAMONDS)}
        self.assertFalse(is_pair(cards))
        cards.add(Card('A', Suits.SPADES))
        self.assertTrue(is_pair(cards))

    def test_is_two_pair(self):
        cards = {Card('A', suit) for suit in Suits}
        self.assertTrue(is_two_pair(cards))
        cards.remove(Card('A', Suits.SPADES))
        self.assertFalse(is_two_pair(cards))
        cards |= {Card(2, Suits.DIAMONDS), Card(2, Suits.CLUBS)}
        self.assertTrue(is_two_pair(cards))

    def test_is_three_of_a_kind(self):
        cards = {Card(2, Suits.CLUBS), Card(2, Suits.SPADES), Card(2, Suits.DIAMONDS)}
        self.assertTrue(is_three_of_a_kind(cards))
        cards.remove(Card(2, Suits.SPADES))
        self.assertFalse(is_three_of_a_kind(cards))

    def test_is_straight(self):
        hand = {Card(rank, Suits.CLUBS) for rank in ['A', 'K', 'Q', 'J', 10]}
        self.assertTrue(is_straight(hand))
        hand.remove(Card('A', Suits.CLUBS))
        hand.add(Card(9, Suits.DIAMONDS))
        self.assertTrue(is_straight(hand))
        hand.remove(Card(9, Suits.DIAMONDS))
        hand.add(Card(8, Suits.DIAMONDS))
        self.assertFalse(is_straight(hand))

    def test_is_flush(self):
        hand = {Card(rank, Suits.CLUBS) for rank in ['A', 'K', 'Q', 'J', 10]}
        self.assertTrue(is_flush(hand))
        hand.remove(Card('A', Suits.CLUBS))
        hand.add(Card('A', Suits.DIAMONDS))
        self.assertFalse(is_flush(hand))

    def test_is_full_house(self):
        aces = {Card('A', suit) for suit in [Suits.SPADES, Suits.CLUBS, Suits.HEARTS]}
        twos = {Card(2, suit) for suit in [Suits.CLUBS, Suits.HEARTS]}
        hand = aces | twos
        self.assertTrue(is_full_house(hand))
        hand.remove(Card(2, Suits.HEARTS))
        hand.add(Card(3, Suits.HEARTS))
        self.assertFalse(is_full_house(hand))

    def test_is_four_of_a_kind(self):
        aces = {Card('A', suit) for suit in [Suits.SPADES, Suits.CLUBS, Suits.HEARTS]}
        twos = {Card(2, suit) for suit in [Suits.CLUBS, Suits.HEARTS]}
        hand = aces | twos
        self.assertFalse(is_four_of_a_kind(hand))
        hand.remove(Card(2, Suits.HEARTS))
        hand.add(Card('A', Suits.DIAMONDS))
        self.assertTrue(is_four_of_a_kind(hand))
    
    def test_is_royal_straight(self):
        hand = {Card(rank, Suits.CLUBS) for rank in ['A', 'K', 'Q', 'J', 10]}
        self.assertTrue(is_royal_straight(hand))
        hand.remove(Card(10, Suits.CLUBS))
        hand.add(Card(10, Suits.DIAMONDS))
        self.assertTrue(is_royal_straight(hand))
        hand.remove(Card(10, Suits.DIAMONDS))
        hand.add(Card(9, Suits.CLUBS))
        self.assertFalse(is_royal_straight(hand))

    def test_group_by_rank(self):
        groups = group_by_rank(self.deck)
        self.assertEqual(len(groups), 13)
        self.assertEqual(len(groups[12]), 4)
        self.assertEqual(groups[12].pop().rank, 2)
        groups = group_by_rank(self.hand)
        self.assertEqual(len(groups), 4)
        self.assertEqual(len(groups[0]), 2)
        self.assertEqual(groups[3].pop().rank, 2)

if __name__ == "__main__":
    unittest.main()
