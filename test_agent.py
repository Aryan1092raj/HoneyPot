# test_agent.py (temporary file)
from agent import HoneypotAgent

agent = HoneypotAgent()
agent.set_persona("You are a helpful assistant.")
response = agent.chat("Hello!")
print(response)