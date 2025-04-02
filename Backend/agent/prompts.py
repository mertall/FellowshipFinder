from langchain_core.prompts import PromptTemplate

def get_filter_prompt():
    return PromptTemplate.from_template("""
        You are helping a student apply for fellowships. Based on the resume below, assign values to the following filters:

        Filters:
        {controls}

        Resume:
        ---
        {resume_text}
        ---

        Return a valid JSON object with these keys.
    """)

def get_action_plan_prompt():
    return PromptTemplate.from_template("""
        You are an AI Agent tasked to find the best fellowships by interacting with a fellowships page instead of the user.

        The following UI controls were detected on the fellowship search page:
        {controls}

        The following user preferences were extracted:
        {features}

        Create 1 instruction to apply a user preference to a UI control. Only create instructions if it will truly benefit the student in finding a fellowship for them.

        The instruction should guide an AI agent how to:
        - Interact with the control for that field (click/select/search text box)
        - Apply the user's filter value appropriately, via text entry, selecting checkbox(es), etc.
        - Ensure selection or visual confirmation, and do not revert changes by accident

        Return a list of short, clear action steps to be executed by the agent.
        - Remove all but the 10 most crucial steps. Filter now.
        - Append a final instruction for executing, filtering, searching, or some synonymous action. ALWAYS the last instruction.
        - Reorder steps so this final action appears at the end.

        Return your response as:
        Thoughts: <rationale>
        Instruction: <steps or STOP>
        Objective: <goal of instruction>
    """)
