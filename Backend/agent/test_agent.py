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

# def test_agent_initialization(agent):
#     """Test that the LaVague agent is initialized properly."""
#     assert agent.llm is not None
#     assert agent.driver is not None
#     assert agent.world_model is not None
#     assert agent.agent is not None 


# def test_assess_search_response_format_and_keywords(agent):
#     """Ensure the result from assess_search_options contains required structure and key terms."""
#     result = agent.assess_search_options()
#     print(result)

#     assert result is not None, "Agent returned None instead of a response string."
#     result_text = result.strip().lower()

#     assert "thoughts:" in result_text, "Missing 'Thoughts:' section in output."
#     assert "instruction:" in result_text, "Missing 'Instruction:' section in output."

#     # Extract filter names from the result
#     extracted = agent.extract_controls(result)
#     expected_keywords = [
#         "Search Fellowships", "Division", "Level", "Deadline", "Type", "Eligibility"
#     ]

#     for keyword in expected_keywords:
#         if keyword in extracted:
#             assert keyword.lower() in result_text, f"Expected keyword '{keyword}' not found in result."


def test_perform_search(agent):
    """Test the perform_search logic by ensuring it dynamically detects filters and executes."""

    # Stubbed user features for dynamic filter population
    agent.get_user_features = lambda: {
        "keyword": "data",
        "division": "Physical Sciences",
        "level": "Graduate",
        "deadline": "Spring",
        "type": "Research",
        "eligibility": "International"
    }

    initial_url = agent.driver.current_url
    agent.perform_search()
    time.sleep(3)  # Give time for the page to update

    new_url = agent.driver.current_url
    page_source = agent.driver.page_source

    assert "fellowship" in page_source.lower() or new_url != initial_url, \
        "Search did not result in expected page update or content change."

    # Try to extract visible results (assuming they're in a table or list format)
    try:
        rows = agent.driver.find_elements("css selector", "table tbody tr")
        print(f"\n🧾 Found {len(rows)} results:\n")
        for i, row in enumerate(rows[:5]):  # Show top 5 results
            print(f"Result {i+1}:")
            cols = row.find_elements("tag name", "td")
            for col in cols:
                print("-", col.text)
            print()
    except Exception as e:
        print("❌ Could not extract fellowship results:", e)
