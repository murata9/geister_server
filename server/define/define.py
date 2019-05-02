#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from enum import Enum

PIECE_MAX_COUNT_BY_PLAYER = 8 # 1プレイヤーの駒数

# 勝敗
class Victory(Enum):
    Undecided = 0
    Win = 1
    Lose = 2
