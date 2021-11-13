import torch, numpy as np
from torch import nn
from datetime import datetime
import tianshou as ts
from tianshou.utils import TensorboardLogger, WandbLogger
from agents import TwoAgentPolicy
from agents.lib_agents import SinePolicy, GreedyPolicy
from agents.lib_agents import DQN
from utils.envs import general_make_env
from functools import partial

# Hyper parameters for the example
NUM_TRAIN_ENVS = 3
NUM_TEST_ENVS = 5
BAR_ACTION_K = 7  # Number of action values to discretize into
BUFFER_SIZE = 2000
BUFFER_NUM = 10
PATH_TO_POLICY = "./opt_policy/policy_2021-11-11_09-06-08.pth"

# Parameters for environment
eval_params = {
    "flatten": {},
    "render": {"eps": 1},
    "discrete": {
        "k": BAR_ACTION_K,
    },
}

env = general_make_env(params=eval_params)

# creating policies
p1 = SinePolicy()
# p2 = GreedyPolicy(agent='bar', disc_k=7)
p2 = DQN(env.observation_space.shape, env.action_space["bar"].shape)(
    discount_factor=0.99, estimation_step=5, target_update_freq=320
)
policy = TwoAgentPolicy(
    observation_space=env.observation_space,
    action_space=env.action_space,
    policies=(p1, p2),
)
policy.load_state_dict(torch.load(PATH_TO_POLICY))
policy.eval()

test_envs = ts.env.DummyVectorEnv(
    [partial(general_make_env, params=eval_params) for _ in range(1)]
)
test_collector = ts.data.Collector(policy, test_envs, exploration_noise=True)

result = test_collector.collect(n_episode=20)
print(result)