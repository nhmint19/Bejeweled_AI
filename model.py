# Inspired by https://github.com/patrickloeber/snake-ai-pytorch
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import os

class Linear_QNet(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super().__init__()
        self.linear1 = nn.Linear(input_size, hidden_size)
        self.linear2 = nn.Linear(hidden_size, output_size)
    
    # get the prediction
    def forward(self, x):
        x = F.relu(self.linear1(x))
        x = self.linear2(x)
        return x

    # save weigh for further training
    def save(self, file_name='model.pth'):
        model_folder_path = './model'
        if not os.path.exists(model_folder_path):
            os.makedirs(model_folder_path)

        file_name = os.path.join(model_folder_path, file_name)
        torch.save(self.state_dict(), file_name)

    # load weigh from previous training
    def load(self, file_path='./model/model.pth'):
        if os.path.exists(file_path):
            # load the saved weights
            self.load_state_dict(torch.load(file_path))
            print("Model weights loaded successfully!")
        else:
            print("Saved weights not found!")

class QTrainer(object):
    def __init__(self, model, lr, gamma):
        self.lr = lr
        self.gamma = gamma
        self.model = model
        self.optimizer = optim.Adam(model.parameters(), lr=self.lr) # Adam model
        self.criterion = nn.MSELoss()

    def train_step(self, state, action, reward, next_state, gameover):
        state = torch.tensor(state, dtype=torch.float)
        next_state = torch.tensor(next_state, dtype=torch.float)
        action = torch.tensor(action, dtype=torch.long)
        reward = torch.tensor(reward, dtype=torch.float)
        # gameover = torch.tensor(gameover, dtype=torch.bool)

        if len(state.shape) == 1:
            state = torch.unsqueeze(state, 0) # create a new dimension
            next_state = torch.unsqueeze(next_state, 0)
            action = torch.unsqueeze(action, 0)
            reward = torch.unsqueeze(reward, 0)
            gameover = (gameover, )

        # predicted Q values with current state
        pred = self.model(state)

        target = pred.clone()
        for idx in range(len(gameover)):
            Q_new = reward[idx]
            if not gameover[idx]:
                Q_new = reward[idx] + self.gamma * torch.max(self.model(next_state[idx]))

            target[idx][torch.argmax(action[idx]).item()] = Q_new
    
        # 2: Q_new = r + y * max( next_predicted Q value )
        self.optimizer.zero_grad()
        loss = self.criterion(target, pred)
        loss.backward()

        self.optimizer.step()