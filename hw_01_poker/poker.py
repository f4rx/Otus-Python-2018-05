#!/usr/bin/env python

import itertools
from collections import namedtuple


"""
>>> for i in itertools.combinations(a, 5): print(i);
...
('7C', '7D', '8C', '8S', 'TC')
('7C', '7D', '8C', '8S', 'TD')
('7C', '7D', '8C', '8S', 'TH')
('7C', '7D', '8C', 'TC', 'TD')
('7C', '7D', '8C', 'TC', 'TH')
('7C', '7D', '8C', 'TD', 'TH')
('7C', '7D', '8S', 'TC', 'TD')
('7C', '7D', '8S', 'TC', 'TH')
('7C', '7D', '8S', 'TD', 'TH')
('7C', '7D', 'TC', 'TD', 'TH')
('7C', '8C', '8S', 'TC', 'TD')
('7C', '8C', '8S', 'TC', 'TH')
('7C', '8C', '8S', 'TD', 'TH')
('7C', '8C', 'TC', 'TD', 'TH')
('7C', '8S', 'TC', 'TD', 'TH')
('7D', '8C', '8S', 'TC', 'TD')
('7D', '8C', '8S', 'TC', 'TH')
('7D', '8C', '8S', 'TD', 'TH')
('7D', '8C', 'TC', 'TD', 'TH')
('7D', '8S', 'TC', 'TD', 'TH')
('8C', '8S', 'TC', 'TD', 'TH')
"""

# -----------------
# Реализуйте функцию best_hand, которая принимает на вход
# покерную "руку" (hand) из 7ми карт и возвращает лучшую
# (относительно значения, возвращаемого hand_rank)
# "руку" из 5ти карт. У каждой карты есть масть(suit) и
# ранг(rank)
# Масти: трефы(clubs, C), пики(spades, S), червы(hearts, H), бубны(diamonds, D)
# Ранги: 2, 3, 4, 5, 6, 7, 8, 9, 10 (ten, T), валет (jack, J), дама (queen, Q), король (king, K), туз (ace, A)
# Например: AS - туз пик (ace of spades), TH - дестяка черв (ten of hearts), 3C - тройка треф (three of clubs)

# Задание со *
# Реализуйте функцию best_wild_hand, которая принимает на вход
# покерную "руку" (hand) из 7ми карт и возвращает лучшую
# (относительно значения, возвращаемого hand_rank)
# "руку" из 5ти карт. Кроме прочего в данном варианте "рука"
# может включать джокера. Джокеры могут заменить карту любой
# масти и ранга того же цвета, в колоде два джокерва.
# Черный джокер '?B' может быть использован в качестве треф
# или пик любого ранга, красный джокер '?R' - в качестве черв и бубен
# любого ранга.

# Одна функция уже реализована, сигнатуры и описания других даны.
# Вам наверняка пригодится itertoolsю
# Можно свободно определять свои функции и т.п.
# -----------------


def hand_rank(hand):
    """Возвращает значение определяющее ранг 'руки'"""
    ranks = card_ranks(hand)
    # print("ranks", ranks)
    if straight(ranks) and flush(hand):
        return (8, max(ranks))
    elif kind(4, ranks):
        return (7, kind(4, ranks), kind(1, ranks))
    elif kind(3, ranks) and kind(2, ranks):
        return (6, kind(3, ranks), kind(2, ranks))
    elif flush(hand):
        return (5, ranks)
    elif straight(ranks):
        return (4, max(ranks))
    elif kind(3, ranks):
        return (3, kind(3, ranks), ranks)
    elif two_pair(ranks):
        return (2, two_pair(ranks), ranks)
    elif kind(2, ranks):
        return (1, kind(2, ranks), ranks)
    else:
        return (0, ranks)


rank_aliases = {
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "T": 10,
    "J": 11,
    "Q": 12,
    "K": 13,
    "A": 14,
}

def card_ranks(hand):
    """Возвращает список рангов (его числовой эквивалент),
    отсортированный от большего к меньшему"""
    ranks = [rank_aliases[card[0]] for card in hand]
    # for card in hand:
    #     ranks.append(card[0])
    return sorted(ranks)


def flush(hand):
    """Возвращает True, если все карты одной масти"""
    suit = hand[0][1]

    for card in hand[1:]:
        if card[1] != suit:
            return
    return True


def straight(ranks):
    """Возвращает True, если отсортированные ранги формируют последовательность 5ти,
    где у 5ти карт ранги идут по порядку (стрит)"""
    for i, rank in enumerate(sorted(ranks[:-1])):
        if ranks[i+1] - rank != 1:
            return
    return True


def kind(n, ranks):
    """Возвращает первый ранг, который n раз встречается в данной руке.
    Возвращает None, если ничего не найдено"""
    # for _ranks in itertools.combinations(ranks, n):
    #     if _ranks.count(_ranks[0]) == n and ranks.count(_ranks[0]) == n:
            # if ranks == [8, 8, 10, 10, 10]:
            #     print(ranks)
            # return _ranks[0]
    rank = 0
    for _rank in ranks:
        if ranks.count(_rank) == n and _rank > rank:
            rank = _rank
    if rank == 0:
        return
    return rank


def two_pair(ranks):
    """Если есть две пары, то возврщает два соответствующих ранга,
    иначе возвращает None"""
    pairs = set()
    for _ranks in itertools.combinations(ranks, 2):
        if _ranks[0] == _ranks[1]:
            pairs.add(_ranks[0])
    if len(pairs) == 2:
        pairs = list(pairs)
        pairs.sort(reverse=True)
        return pairs
    return


def best_hand(hand):
    """Из "руки" в 7 карт возвращает лучшую "руку" в 5 карт """
    Hand = namedtuple('Hand', ['hand', 'hand_rank'])
    top_hand = Hand(hand=None, hand_rank=(-1,))
    for _hand in itertools.combinations(hand, 5):
        _hand_rank = hand_rank(_hand)
        if _hand_rank[0] > top_hand.hand_rank[0]:
            # print("old hand:", top_hand.hand, "new hand:", _hand, "rank:", _hand_rank)
            top_hand = Hand(hand=_hand, hand_rank=_hand_rank)
            print("old hand:", top_hand.hand, "new hand:", _hand, "rank:", _hand_rank)
        elif _hand_rank[0] == top_hand.hand_rank[0]:
            # Check Rank in Flash Royal
            # rank: (8, 11)
            if _hand_rank[0] == 8 or _hand_rank[0] == 4 or _hand_rank[0] == 0:
                if _hand_rank[1] > top_hand.hand_rank[1]:
                    print("old hand:", top_hand.hand, "new hand:", _hand, "rank:", _hand_rank)
                    top_hand = Hand(hand=_hand, hand_rank=_hand_rank)
            # Test Flash
            # rank: (5, [5, 7, 9, 10, 12])
            # rank: (5, [5, 8, 9, 10, 12])
            elif _hand_rank[0] == 5:
                if sorted(_hand_rank[1], reverse=True) > sorted(top_hand.hand_rank[1], reverse=True):
                    print("old hand:", top_hand.hand, "new hand:", _hand, "rank:", _hand_rank)
                    top_hand = Hand(hand=_hand, hand_rank=_hand_rank)

            elif _hand_rank[0] in [7, 6, 3, 1]:
                if _hand_rank[1] > int(top_hand.hand_rank[1]) or (_hand_rank[1] == int(top_hand.hand_rank[1]) and
                                                                  _hand_rank[2] > top_hand.hand_rank[2]):
                    print("old hand:", top_hand.hand, "new hand:", _hand, "rank:", _hand_rank)
                    top_hand = Hand(hand=_hand, hand_rank=_hand_rank)
            elif _hand_rank[0] == 2:
                # Сравниваем две пары, если пары одинаковые, то выьираем пятой карту с наибольшим рангом.
                # rank: (2, [5, 2], [2, 2, 5, 5, 8])
                # rank: (2, [5, 2], [2, 2, 5, 5, 10])
                if _hand_rank[1][0] > top_hand.hand_rank[1][0] or \
                    (_hand_rank[1][0] == top_hand.hand_rank[1][0] and _hand_rank[1][1] > top_hand.hand_rank[1][1]) or \
                    (_hand_rank[1][0] == top_hand.hand_rank[1][0] and _hand_rank[1][1] == top_hand.hand_rank[1][1] and
                     kind(1, _hand_rank[2]) > kind(1, top_hand.hand_rank[2])):
                        print("old hand:", top_hand.hand, "new hand:", _hand, "rank:", _hand_rank)
                        top_hand = Hand(hand=_hand, hand_rank=_hand_rank)

    print("Best hand", sorted(top_hand.hand), "\n")
    return list(top_hand.hand)


def best_wild_hand(hand):
    """best_hand но с джокерами"""
    return

def test_best_hand():
    print("test_best_hand...")
    # Test Flash Royal (8)
    assert (sorted(best_hand("AS KS JS 8S 7S QS TS".split()))
            == sorted(['TS', 'JS', 'QS', 'KS', 'AS']))
    assert (sorted(best_hand("7C 8C 9C TC JC QC KC".split()))
            == sorted(['9C', 'JC', 'TC', 'QC', 'KC']))

    # # Test 4 Q (7)
    assert (sorted(best_hand("6C 7C QC QS QH QD KS".split()))
            == sorted(['QC', 'QS', 'QH', 'QD', 'KS']))

    # # Test kind(3, ranks) and kind(2, ranks) (6)
    assert (sorted(best_hand("6C 7C 7S 7H 8C 8S JS".split()))
            == sorted(['7C', '7S', '7H', '8C', '8S']))

    # # Test Flash (5)
    assert (sorted(best_hand("5C 7C 8C 9C TC JS QC".split()))
            == sorted(['7C', '8C', '9C', 'TC', 'QC']))

    # Test straight (4)
    assert (sorted(best_hand("5S 7C 8S 9C TC JS QC".split()))
            == sorted(['8S', '9C', 'TC', 'JS', 'QC']))

    # Test 3 same and others (3)
    assert (sorted(best_hand("7S 7C 7D 6C 5C 4S 2C".split()))
            == sorted(['7S', '7C', '7D', '6C', '5C']))

    # Test 2 pair (2)
    assert (sorted(best_hand("7S 7C 5D JC KD JS 2C".split()))
            == sorted(['7C', '7S', 'JC', 'JS', 'KD']))

    # Test 1 pair (1)
    assert (sorted(best_hand("2S 2C 5D 4C KD JS 3C".split()))
            == sorted(['2C', '2S', '5D', 'JS', 'KD']))

    assert (sorted(best_hand("6C 7C 8C 9C TC 5C JS".split()))
            == ['6C', '7C', '8C', '9C', 'TC'])
    assert (sorted(best_hand("TD TC TH 7C 7D 8C 8S".split()))
            == ['8C', '8S', 'TC', 'TD', 'TH'])
    assert (sorted(best_hand("JD TC TH 7C 7D 7S 7H".split()))
            == ['7C', '7D', '7H', '7S', 'JD'])
    assert (sorted(best_hand("2D 2C 5H 5C 7D 8S TH".split()))
            == ['2C', '2D', '5C', '5H', 'TH'])
    print('OK')


def test_best_wild_hand():
    print("test_best_wild_hand...")
    assert (sorted(best_wild_hand("6C 7C 8C 9C TC 5C ?B".split()))
            == ['7C', '8C', '9C', 'JC', 'TC'])
    assert (sorted(best_wild_hand("TD TC 5H 5C 7C ?R ?B".split()))
            == ['7C', 'TC', 'TD', 'TH', 'TS'])
    assert (sorted(best_wild_hand("JD TC TH 7C 7D 7S 7H".split()))
            == ['7C', '7D', '7H', '7S', 'JD'])
    print('OK')


if __name__ == '__main__':
    test_best_hand()
    # test_best_wild_hand()
