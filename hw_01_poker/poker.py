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
    return ranks[-1] - ranks[0] == 4


def kind(n, ranks):
    """Возвращает первый ранг, который n раз встречается в данной руке.
    Возвращает None, если ничего не найдено"""
    for _ranks in itertools.combinations(ranks, n):
        if _ranks.count(_ranks[0]) == n and ranks.count(_ranks[0]) == n:
            # if ranks == [8, 8, 10, 10, 10]:
            #     print(ranks)
            return _ranks[0]
    return


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
        elif _hand_rank[0] == top_hand.hand_rank[0]:
            if _hand_rank[0] in [7, 6, 3, 1]:
                if _hand_rank[1] > int(top_hand.hand_rank[1]) or (_hand_rank[1] == int(top_hand.hand_rank[1]) and
                                                                  _hand_rank[2] >  int(top_hand.hand_rank[2])):
                    # print("old hand:", top_hand.hand, "new hand:", _hand, "rank:", _hand_rank)
                    top_hand = Hand(hand=_hand, hand_rank=_hand_rank)
            if _hand_rank[0] == 2:
                # Сравниваем две пары, если пары одинаковые, то выьираем пятой карту с наибольшим рангом.
                # rank: (2, [5, 2], [2, 2, 5, 5, 8])
                # rank: (2, [5, 2], [2, 2, 5, 5, 10])
                if _hand_rank[1][0] > top_hand.hand_rank[1][0] or \
                    (_hand_rank[1][0] == top_hand.hand_rank[1][0] and _hand_rank[1][1] > top_hand.hand_rank[1][1]) or \
                    (_hand_rank[1][0] == top_hand.hand_rank[1][0] and _hand_rank[1][1] == top_hand.hand_rank[1][1] and
                     kind(1, _hand_rank[2]) > kind(1, top_hand.hand_rank[2])):
                        print("old hand:", top_hand.hand, "new hand:", _hand, "rank:", _hand_rank)
                        top_hand = Hand(hand=_hand, hand_rank=_hand_rank)

    print("Best hand", top_hand.hand)
    return list(top_hand.hand)


def best_wild_hand(hand):
    """best_hand но с джокерами"""
    return


def test_best_hand():
    print("test_best_hand...")
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
