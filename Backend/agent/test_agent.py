import pytest
import time
import os
import csv
from main import FellowshipSearchAgent
import os
os.environ["TELEMETRY_VAR"] = "NONE"


@pytest.fixture(scope="module")
def agent():
    """Fixture to create an instance of FellowshipSearchAgent for testing."""
    agent = FellowshipSearchAgent(use_local_llm=False)
    yield agent
    agent.close()

def test_agent_initialization(agent):
    """Test that the LaVague agent is initialized properly."""
    assert agent.llm is not None
    assert agent.driver is not None
    assert agent.world_model is not None
    assert agent.agent is not None 


def test_assess_search_response_format_and_keywords(agent):
    """Ensure the result from assess_search_options contains required structure and key terms."""
    result = agent.assess_search_options()
    print(result)

    assert result is not None, "Agent returned None instead of a response string."
    result_text = result.strip().lower()

    assert "thoughts:" in result_text, "Missing 'Thoughts:' section in output."
    assert "instruction:" in result_text, "Missing 'Instruction:' section in output."

    # Extract filter names from the result
    extracted = agent.extract_controls(result)
    expected_keywords = [
        "Search Fellowships", "Division", "Level", "Deadline", "Type", "Eligibility"
    ]

    for keyword in expected_keywords:
        if keyword in extracted:
            assert keyword.lower() in result_text, f"Expected keyword '{keyword}' not found in result."


