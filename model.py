import gym
from stable_baselines3 import DQN
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.evaluation import evaluate_policy

environment_name = "CartPole-v1"
env = gym.make(environment_name)
episodes = 5
for episode in range(1, episodes + 1):
    state = env.reset()
    done = False
    score = 0

    while not done:
        env.render()
        action = env.action_space.sample()
        n_state, reward, terminated, truncated, info = env.step(action)
        done = terminated or truncated
        score += reward
    print('Episode:{} Score:{}'.format(episode, score))

# 0-push cart to left, 1-push cart to the right
print(env.action_space.sample())
# [cart position, cart velocity, pole angle, pole angular velocity]
print(env.observation_space.sample())

env = gym.make(environment_name)
env = DummyVecEnv([lambda: env])
model = DQN('MlpPolicy', env, verbose=1)
model.learn(total_timesteps=100000, log_interval=1000)

env = gym.make(environment_name)
evaluate_policy(model, env, n_eval_episodes=10)
env.close()
