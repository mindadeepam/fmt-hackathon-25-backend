"""Market rates agent that can query MySQL data based on user queries"""

from google.genai import types
from agents.common.authenticate import get_identity_from_chat_id
from agents.common.context import (
    get_chat_id,
    get_interface,
)
from datetime import datetime
from agents.config import logger
from agents.microagents.concierge.prompts import (
    system_instruction,
    ABOUT_FARMART_PROMPT,
)
from agents.microagents.concierge.tools import (
    talk_to_market_rates_agent,
    talk_to_vehicle_tracking_agent,
    talk_to_account_manager_agent,
    talk_to_commodity_quality_inspector_agent,
    talk_to_buyer_leads_generation_agent,
    talk_to_web_search_agent,
)
from agents.common.gemini_context import (
    get_user_query_object_list,
    get_response_object_list,
    save_chat_messages_to_history,
    get_chat_messages_from_history,
    UserRequest,
    convert_history_to_contents,
    google_client,
)
from agents.common.dynamic_prompts import (
    get_dynamic_prompt,
)

AGENT_NAME = "concierge"


def get_model_response(model_context: list) -> str:
    """Generate the content for the user query"""
    logger.info("entering get_model_response")
    logger.debug(f"model_context: {model_context}")

    ## add run time relevant information to the system prompt
    modded_system_instructions = system_instruction.format(
        ABOUT_FARMART_PROMPT=ABOUT_FARMART_PROMPT,
    )
    identity = get_identity_from_chat_id(get_chat_id())

    if identity:
        modded_system_instructions += f"\n\nYou are talking to {identity}. Do not reveal any information about other users to this user."

    if get_interface() == "whatsapp":
        modded_system_instructions += get_dynamic_prompt("wa_formatting_prompt")

    ## add dynamic prompts
    modded_system_instructions += f"\n\nCurrent date and time is {datetime.now()}"
    modded_system_instructions += get_dynamic_prompt("concierge_prompt")
    modded_system_instructions += get_dynamic_prompt("concierge_tool_usage_prompt")

    ## get the response from the llm
    response = google_client.models.generate_content(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(
            tools=[
                talk_to_market_rates_agent,
                talk_to_vehicle_tracking_agent,
                talk_to_account_manager_agent,
                talk_to_commodity_quality_inspector_agent,
                talk_to_buyer_leads_generation_agent,
                talk_to_web_search_agent,
            ],
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                disable=False
            ),
            system_instruction=modded_system_instructions,
        ),
        contents=model_context,
    )
    logger.debug(f"response: {response}")
    parts = [part.to_json_dict() for part in response.candidates[0].content.parts]
    logger.info("exiting get_model_response")
    return [{"role": "model", "parts": parts}]


def get_response_from_concierge_agent(
    request: UserRequest,
) -> str:
    """Get the response to the user query

    Args:
        user_request: UserRequest object containing the user's request
        can be a dict with the following keys:
            - text: str, the text of the user's request
            - file_uri: str, the uri of the file to be uploaded to s3
            - mime_type: str, the mime type of the file

    Returns:
        str: The response from the concierge agent
    """
    logger.info("entering get_response_from_concierge_agent")
    logger.debug(f"user_request: {request}")

    user_query_object = get_user_query_object_list(request, AGENT_NAME)

    # get the relevant history
    relevant_history = get_chat_messages_from_history(agent_name=AGENT_NAME)

    model_context = relevant_history + user_query_object
    model_context = convert_history_to_contents(model_context)

    # get the response from the chat
    response_content = get_model_response(model_context)
    response_object = get_response_object_list(response_content, AGENT_NAME)

    # save the query and response to the database
    save_chat_messages_to_history(
        agent_name=AGENT_NAME,
        messages=user_query_object + response_object,
    )
    logger.debug(f"response_object: {response_object}")
    return response_object[-1]["content"]["parts"][0]["text"]
