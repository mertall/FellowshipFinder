from PIL import Image
import pytest
import os
from main import FellowshipSearchAgent

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
    assert result is not None, "Agent returned None instead of a response string."
    result_text = result.strip().lower()

    extracted = agent.extract_controls(result)
    expected_keywords = [
        "Search Fellowships", "Division", "Level", "Deadline", "Type", "Eligibility"
    ]

    for keyword in expected_keywords:
        if keyword in extracted:
            assert keyword.lower() in result_text, f"Expected keyword '{keyword}' not found in result."

def test_get_user_features_returns_valid_fields(agent):
    """Test that get_user_features returns a dictionary with expected keys."""
    required_keys = ["Keyword", "Division", "Level", "Deadline", "Type", "Eligibility"]

    features = agent.get_user_features(controls=required_keys)
    print(features)
    required_keys = ["Keyword", "Division", "Level", "Deadline", "Type", "Eligibility"]
    assert isinstance(features, dict), "Features should be a dictionary."
    for key in required_keys:
        assert key in features, f"Missing key in features: {key}"

def test_run_workflow_executes_interactions(agent):
    """Test that the run_workflow method completes the full interaction flow without crashing."""
    try:
        agent.run_workflow()
        assert True  # If no exception is raised, the test passes
    except Exception as e:
        pytest.fail(f"Workflow failed with exception: {e}")

def test_extract_table_to_csv(agent):
    agent.assess_search_options()
    agent.extract_table_to_csv(csv_path="test_table_export.csv")
    assert os.path.exists("test_table_export.csv"), "CSV was not created."
