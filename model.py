from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam
from rl.agents import DQNAgent
from rl.memory import SequentialMemory
from rl.policy import LinearAnnealedPolicy, EpsGreedyQPolicy
from env import flappy_env


def build_model():
    model = Sequential()
    model.add(Dense(16, input_shape=(4,), activation='relu'))
    model.add(Dense(16, activation='relu'))
    model.add(Dense(2, activation='linear'))
    return model


def build_agent(sequential_model):
    policy = LinearAnnealedPolicy(EpsGreedyQPolicy(), attr='eps', value_max=1., value_min=.1, value_test=.2, nb_steps=10000)
    memory = SequentialMemory(limit=1000, window_length=3)
    dqn = DQNAgent(model=sequential_model, memory=memory, policy=policy,
                   enable_dueling_network=True, dueling_type='avg',
                   nb_actions=2, nb_steps_warmup=1000)
    return dqn


env = flappy_env()
model = build_model()
model.summary()
dqn = build_agent(model)
dqn.compile(Adam(learning_rate=1e-4))
dqn.fit(env, nb_steps=10000, visualize=False)
