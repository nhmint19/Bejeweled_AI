# Inspired by https://github.com/patrickloeber/snake-ai-pytorch
import torch
import random 
import numpy as np
from environment import Environment
from collections import deque
from Gem import MARGIN, CELL_SIZE
from Board import ROWS, COLUMNS
from model import Linear_QNet, QTrainer
import pygame
from pygame.locals import *
from GameState import StationaryState
from plot import plot

MAX_MEMORY = 1000000
BATCH_SIZE = 10000
LR = 0.01 # learning rate

class RLAgent:
    def __init__(self):
        self.games_num = 0
        # initiates the variables in Bellman's equation
        self.epsilon = 0 # to control randomness
        self.gamma = 0.8 # discount rate 
        self.memory = deque(maxlen=MAX_MEMORY) # maintain memory for training
        # all posisble actions
        self.actions = []
        for row in range(ROWS):
            for col in range(COLUMNS):
                # swap with the gem above if valid
                if row > 0:
                    self.actions.append(((row, col), (row - 1, col)))

                # swap with the gem below if valid
                if row < ROWS - 1:
                    self.actions.append(((row, col), (row + 1, col)))

                # swap with the gem to the left if valid
                if col > 0:
                    self.actions.append(((row, col), (row, col - 1)))

                # swap with the gem to the right if valid
                if col < COLUMNS - 1:
                    self.actions.append(((row, col), (row, col + 1)))
        self.model = Linear_QNet(ROWS * COLUMNS, 256, len(self.actions))
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

    def get_state(self, environment):
        state = []
        for r in environment.board.board:
            for gem in r:
                state.append(gem.gem_type)
        return np.array(state, dtype=int)

    def get_action(self, state, environment):
        # exploration: random moves
        self.epsilon = ROWS * COLUMNS * 2 - self.games_num
        r1, c1, r1, c2 = 0, 0, 0, 0
        if random.randint(0, ROWS * COLUMNS * 2) < self.epsilon:
            # random click value
            ((r1, c1), (r2, c2)) = random.choice(self.actions)
        else:
            print("exploit")
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            ((r1, c1), (r2, c2)) = self.actions[torch.argmax(prediction).item()]
        action = (environment.get_gem_coordinates(r1, c1), environment.get_gem_coordinates(r2, c2))
        return action

    def perform_action(self, action):
        pos1, pos2 = action
        mouse_event = pygame.event.Event(MOUSEBUTTONDOWN, button=1, pos=pos1)
        pygame.event.post(mouse_event)
        mouse_event = pygame.event.Event(MOUSEBUTTONDOWN, button=1, pos=pos2)
        pygame.event.post(mouse_event)

    def remember(self, state, action, reward, next_state, gameover):
        self.memory.append((state, action, reward, next_state, gameover))

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            # select a random sample
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, gameovers = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, gameovers)

    def train_short_memory(self, state, action, reward, next_state, gameover):
        self.trainer.train_step(state, action, reward, next_state, gameover)

def train():
    # for plotting purposes
    scores_plot = [] 
    mean_scores_plot = []
    total_score = 0
    highest_score = 0
    # initiate agents
    agent = RLAgent()
    environment = Environment()
    agent.model.load()
    while True:
        if environment.game_state != StationaryState:
            environment.run()
        else:
            # get old state
            old_state = agent.get_state(environment)
            # get action
            action = agent.get_action(old_state, environment)
            # perform action
            agent.perform_action(action)
            reward, gameover, score = environment.run() 
            # get new state
            new_state = agent.get_state(environment)
            # train short memory
            agent.train_short_memory(old_state, action, reward, new_state, gameover)
            # makes agent remember
            agent.remember(old_state, action, reward, new_state, gameover)
            # reset the game if gameover
            if gameover:
                environment.reset()
                agent.games_num += 1
                agent.train_long_memory()

                if score > highest_score:
                    highest_score = score
                    agent.model.save()

                print("Game: ", agent.games_num, ", Score: ", score, ", Record: ", highest_score)

                # plot statistics
                scores_plot.append(score)
                total_score += score
                mean_score = total_score / agent.games_num
                mean_scores_plot.append(mean_score)
                plot(scores_plot, mean_scores_plot)

if __name__ == '__main__':
    train()