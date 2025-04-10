import json
from typing import Optional
from agents.feature_flags import FeatureFlags
from agents.config import logger
from agents.common.utils import UserRequest
from agents.microagents.web_search_agent.prompts import (
    system_instruction as web_search_system_instruction,
)


def talk_to_market_rates_agent(
    query: str, media_url: Optional[str] = None, mime_type: Optional[str] = None
) -> json:
    """Talk to the market rates agent
    This agent has all the information about market rates of all commodities. It can also get commodity prices(same as trade prices) and buyer prices (buyer details are provided along woth trade prices).
    Args:
        query: str: The query to execute
        media_url: str: The url of the media to analyze. pass "" if there is no media.
        mime_type: str: The mime type of the media (for eg. image/jpeg, image/png, audio/mpeg, video/mp4, etc.) infer it from the query or the url dont ask the user for it. pass "" if there is no media.
    Returns:
        str: The results of the query
    """
    logger.info("entering talk_to_market_rates_agent")
    logger.debug(
        f"market rates tool called with args: query: {query}, media_url: {media_url}, mime_type: {mime_type}"
    )
    if FeatureFlags.market_rates_agent:
        from agents.microagents.market_rates_agent.agent import (
            get_response_from_market_rates_agent,
        )

        user_request = UserRequest(text=query, file_uri=media_url, mime_type=mime_type)
        response = get_response_from_market_rates_agent(user_request)
    else:
        return "Feature flag is not enabled"
    logger.info("exiting talk_to_market_rates_agent")
    return response


def talk_to_vehicle_tracking_agent(
    query: str, media_url: Optional[str] = None, mime_type: Optional[str] = None
) -> json:
    """
    Description:
    Talk to the vehicle tracking agent.
    It can do the following:
    - create a new tracking session for a truck
    - get the truck location for a purchase crop order (PO)
    - get the truck location for a truck number
    Args:
        query: str: The query to execute
        media_url: str: The url of the media to analyze. pass "" if there is no media.
        mime_type: str: The mime type of the media (for eg. image/jpeg, image/png, audio/mpeg, video/mp4, etc.) infer it from the query or the url dont ask the user for it. pass "" if there is no media.
    Returns:
        str: The results of the query
    """
    logger.info("entering talk_to_vehicle_tracking_agent")
    logger.debug(
        f"vehicle tracking tool called with args: query: {query}, media_url: {media_url}, mime_type: {mime_type}"
    )
    if FeatureFlags.vehicle_tracking_agent:
        from agents.microagents.vehicle_tracking_agent.agent import (
            get_response_from_vehicle_tracking_agent,
        )

        user_request = UserRequest(text=query, file_uri=media_url, mime_type=mime_type)
        response = get_response_from_vehicle_tracking_agent(user_request)
    else:
        return "Feature flag is not enabled"
    logger.info("exiting talk_to_vehicle_tracking_agent")
    return response


def talk_to_account_manager_agent(
    query: str, media_url: Optional[str] = None, mime_type: Optional[str] = None
) -> json:
    """
    Description:
    You can help users connect to thier accounts manager. They will help you with any order related or accounts related information about a deal between farmart and a user, or information about a user's ledger like outstanding payments, payments received, payments due, deductions on orders, etc.
    You can also get information about a user's orders with farmart with this tool. for eg. what is the total number of orders a user has with farmart, what is the total number of orders a user has delivered, what is the total number of orders a user has pending, etc.
    You can also get information about a user's orders/POs with farmart with this tool. for eg. what is the total number of POs a user has with farmart, what is the total number of POs a user has delivered, what is the total number of POs a user has pending.
    etc.

    Args:
        query: str: The query to execute
        media_url: str: The url of the media to analyze. pass "" if there is no media.
        mime_type: str: The mime type of the media (for eg. image/jpeg, image/png, audio/mpeg, video/mp4, etc.) infer it from the query or the url dont ask the user for it. pass "" if there is no media.
    Returns:
        str: The results of the query
    """
    logger.info("entering talk_to_account_manager_agent")
    logger.debug(
        f"account manager tool called with args: query: {query}, media_url: {media_url}, mime_type: {mime_type}"
    )
    if FeatureFlags.account_manager_agent:
        from agents.microagents.account_manager.agent import (
            get_response_from_account_manager_agent,
        )

        user_request = UserRequest(text=query, file_uri=media_url, mime_type=mime_type)
        logger.info(
            f"received args in accounts and payables agent: query: {query}, media_url: {media_url}, mime_type: {mime_type}"
        )
        response = get_response_from_account_manager_agent(user_request)
    else:
        return "Feature flag is not enabled"
    logger.info("exiting talk_to_account_manager_agent")
    return response


def talk_to_buyer_leads_generation_agent(
    query: str, media_url: Optional[str] = None, mime_type: Optional[str] = None
) -> json:
    """Talk to the buyer leads generation agent.
    Args:
        query: str: The query to execute
    Returns:
        str: The results of the query
    """
    logger.info("entering talk_to_buyer_leads_generation_agent")
    logger.debug(
        f"buyer leads generation tool called with args: query: {query}, media_url: {media_url}, mime_type: {mime_type}"
    )
    if FeatureFlags.lead_generation_agent:
        from agents.microagents.lead_generation.agent import (
            get_response_from_lead_generation_agent,
        )

        user_request = UserRequest(text=query, file_uri=media_url, mime_type=mime_type)
        response = get_response_from_lead_generation_agent(user_request)
        logger.info("exiting talk_to_buyer_leads_generation_agent")
        return response
    else:
        logger.info("exiting talk_to_buyer_leads_generation_agent")
        return "Feature flag is not enabled"


def talk_to_commodity_quality_inspector_agent(
    query: str, media_url: str, mime_type: str
) -> json:
    """
    Description:
    Talk to the commodity quality inspector agent. when someone asks about the quality of a commodity or submits an image and asks for the quality of the commodity, you can use this tool to get the quality of the commodity.

    pass the media uri along with the query in 1 shot. this agent is stateless.

    To have a valid image for QC the person must lay some grains on a white background with a coin in the centre, preferably a 10 rupee coin. Tell the user to do so and then pass it to this function. We guage the distance via the coin size. If its a valid image, the agent will send a response on whatsapp with the results.


    Args:
        query: str: The query to execute
        media_url: str: The url of the media to analyze. it'll be a file-uri
        mime_type: str: The mime type of the media (for eg. image/jpeg)
    Returns:
        str: The results of the query
    """
    logger.info("entering talk_to_commodity_quality_inspector_agent")
    if FeatureFlags.commodity_quality_inspector_agent:
        from agents.microagents.commodity_quality_inspector.agent import (
            get_response_from_commodity_quality_inspector_agent,
        )

        user_request = UserRequest(text=query, file_uri=media_url, mime_type=mime_type)
        logger.info(f"user_request: {user_request}")
        response = get_response_from_commodity_quality_inspector_agent(user_request)
        logger.info("exiting talk_to_commodity_quality_inspector_agent")
        return response
    else:
        logger.info("exiting talk_to_commodity_quality_inspector_agent")
        return "Feature flag is not enabled"


def talk_to_web_search_agent(
    query: str, media_url: Optional[str] = None, mime_type: Optional[str] = None
) -> json:
    f"""

    Talk to the web search agent. This agent can search the web for information based on user queries. 
    Keep in mind the following:

    {web_search_system_instruction}

    Description:
    This agent can search the internet for information on any topic. It's useful when you need to find current
    information or facts that might not be in your knowledge base.

    Args:
        query: str: The search query to execute
        media_url: str: The url of the media to analyze. pass "" if there is no media.
        mime_type: str: The mime type of the media (for eg. image/jpeg, image/png, audio/mpeg, video/mp4, etc.) infer it from the query or the url dont ask the user for it. pass "" if there is no media.
    Returns:
        str: The results of the web search
    """
    logger.info("entering talk_to_web_search_agent")
    logger.debug(
        f"web search tool called with args: query: {query}, media_url: {media_url}, mime_type: {mime_type}"
    )
    if FeatureFlags.web_search_agent:
        from agents.microagents.web_search_agent.agent import (
            get_response_from_web_search_agent,
        )

        user_request = UserRequest(text=query, file_uri=media_url, mime_type=mime_type)
        response = get_response_from_web_search_agent(user_request)
        logger.info("exiting talk_to_web_search_agent")
        return response
    else:
        logger.info("exiting talk_to_web_search_agent")
        return "Feature flag is not enabled"
