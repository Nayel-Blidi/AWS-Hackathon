"""
AWS init package. Every class can be imported from this folder without going deeper in the src/ tree.
"""

__all__ = [
    "BedrockRuntimeClient",
    "BedrockKnowledgeBase",
]


from bedrock.src.BedrockRuntimeClient import BedrockRuntimeClient
from bedrock.src.BedrockKnowledgeBase import BedrockKnowledgeBase
