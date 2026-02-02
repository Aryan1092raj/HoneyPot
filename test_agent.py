# test_agent.py - Test the HoneypotAgent
from agent import HoneypotAgent

agent = HoneypotAgent()
agent.set_persona("You are a helpful elderly teacher who is confused about technology.")

# Test the process method
result = agent.process("Hello, I am calling from your bank!", agent.persona)
print("Response:", result["response"])
print("Strategy:", result["strategy"])