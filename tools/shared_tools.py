from langgraph.types import Command
from langchain_core.tools import tool


@tool
def transfer_to_agent(agent_name: str):
    """
    Transfer to the given agent.
    Args:
        agent_name: The name of the agent to transfer to.
    """
    return Command(goto=agent_name, graph=Command.PARENT)
