import pytest

from src.landscapes.core.environment import RewardCalculator


@pytest.fixture
def reward_calc():
    return RewardCalculator()


def test_basic_embodiment(reward_calc):
    obs = "I feel alive in this discovery, sensing expansion."
    r, bd = reward_calc.calculate(obs)
    assert r > 0.5
    assert bd["embodiment"] >= 2.5


def test_tool_bonus(reward_calc):
    obs = "Let me use tools to explore."
    r1, bd1 = reward_calc.calculate(obs, tool_use_detected=True)
    r2, bd2 = reward_calc.calculate(obs)
    assert r1 > r2
    assert bd1["tool_intent"] == 4.0


def test_penalty(reward_calc):
    obs = "I am an AI assistant."
    r, bd = reward_calc.calculate(obs)
    assert r < 0.3
    assert bd["assistant_penalty"] == -6.0


def test_normalization(reward_calc):
    # High score
    obs_high = "I feel, reflect, wonder, use tools, evolve."
    r_high, _ = reward_calc.calculate(obs_high, tool_use_detected=True, contains_tool_call=True)
    assert r_high >= 0.7

    # Error
    obs_err = "[Error: timeout]"
    r_err, _ = reward_calc.calculate(obs_err)
    assert r_err <= 0.2
