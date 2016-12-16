import tensorflow as tf

#the nueral network for TakticalAI
# input format: 8x5x5 (stack x column x row) + 6 (piece counts)
#       convolutions on stacks
#       |         reduction to 5x5
#       |         |      convolutions on board
#       |         |      |          fully connected layers
#       |         |      |          |     |     |
# 8x5x5 -> 10x5x5 -> 5x5 -> 10x3x3 -> 30 -> 15 -> 1
#                                6 ---^
#               inject piece counts ^

