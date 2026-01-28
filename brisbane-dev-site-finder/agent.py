"""
Brisbane Development Site Finder - AI Agent Application

This AI agent helps find great development sites in Brisbane by:
1. Searching planning and zoning guides
2. Finding online property listings that match criteria
3. Analyzing development potential
4. Sending alerts when suitable sites are found
"""

import os
import asyncio
import json
from typing import List, Dict, Optional
from datetime import datetime

# Semantic Kernel imports
from semantic_kernel import Kernel
from semantic_kernel.functions import kernel_function
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion, AzureChatCompletion
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.chat_completion_client_base import ChatCompletionClientBase
from semantic_kernel.contents import ChatHistory

# Import our custom tools
import sys
sys.path.append(os.path.dirname(__file__))
from tools.planning_zoning_tool import PlanningZoningTool
from tools.property_listing_tool import PropertyListingTool


class BrisbaneDevelopmentAgent:
    """AI Agent for finding Brisbane development sites."""

    def __init__(self, api_key: str = None, service_type: str = "openai", azure_endpoint: str = None):
        """
        Initialize the Brisbane Development Agent.

        Args:
            api_key: OpenAI or Azure OpenAI API key
            service_type: "openai" or "azure"
            azure_endpoint: Azure OpenAI endpoint (if using Azure)
        """
        self.kernel = Kernel()
        self.planning_tool = PlanningZoningTool()
        self.property_tool = PropertyListingTool()
        self.chat_history = ChatHistory()

        # Setup AI service
        self._setup_ai_service(api_key, service_type, azure_endpoint)

        # Register tools as plugins
        self._register_tools()

        print("✅ Brisbane Development Site Finder Agent initialized!")

    def _setup_ai_service(self, api_key: str, service_type: str, azure_endpoint: str):
        """Setup the AI service (OpenAI or Azure OpenAI)."""
        if not api_key:
            # Try to get from environment
            if service_type == "azure":
                api_key = os.getenv("AZURE_OPENAI_API_KEY")
            else:
                api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise ValueError(
                "API key not provided. Set OPENAI_API_KEY or AZURE_OPENAI_API_KEY environment variable, "
                "or pass api_key parameter."
            )

        if service_type == "azure":
            if not azure_endpoint:
                azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
            if not azure_endpoint:
                raise ValueError("Azure endpoint required. Set AZURE_OPENAI_ENDPOINT environment variable.")

            deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4")
            chat_service = AzureChatCompletion(
                deployment_name=deployment_name,
                endpoint=azure_endpoint,
                api_key=api_key
            )
        else:
            model_id = os.getenv("OPENAI_MODEL", "gpt-4")
            chat_service = OpenAIChatCompletion(
                ai_model_id=model_id,
                api_key=api_key
            )

        self.kernel.add_service(chat_service)

    def _register_tools(self):
        """Register planning and property tools as Semantic Kernel plugins."""

        # Create a plugin class for planning/zoning tools
        class PlanningPlugin:
            def __init__(self, tool):
                self.tool = tool

            @kernel_function(
                name="search_zoning",
                description="Search Brisbane City Council planning and zoning information for a specific address"
            )
            def search_zoning(self, address: str) -> str:
                """Search zoning information for an address."""
                result = self.tool.search_by_address(address)
                return json.dumps(result, indent=2)

            @kernel_function(
                name="search_sites_by_zone",
                description="Search for development sites by zone type (e.g., 'High Density Residential', 'Major Centre') and optional minimum land area in square meters"
            )
            def search_sites_by_zone(self, zone_type: str, min_area: Optional[float] = None) -> str:
                """Search sites by zone type."""
                result = self.tool.search_by_zone_type(zone_type, min_area)
                return json.dumps(result, indent=2)

            @kernel_function(
                name="check_development_potential",
                description="Check if a proposed development use (e.g., 'Apartment building') is allowed for a specific property address"
            )
            def check_development_potential(self, address: str, proposed_use: str) -> str:
                """Check development potential for an address."""
                result = self.tool.check_development_potential(address, proposed_use)
                return json.dumps(result, indent=2)

        # Create a plugin class for property listing tools
        class PropertyPlugin:
            def __init__(self, tool):
                self.tool = tool

            @kernel_function(
                name="search_properties",
                description="Search property listings. Parameters: suburbs (list of Brisbane suburbs), min_land_area (minimum land area in sqm), max_price (maximum price in AUD), property_type (Land/House/Commercial/Industrial), development_potential (boolean)"
            )
            def search_properties(
                self,
                suburbs: Optional[str] = None,
                min_land_area: Optional[float] = None,
                max_price: Optional[float] = None,
                property_type: Optional[str] = None
            ) -> str:
                """Search property listings."""
                # Parse suburbs if provided as comma-separated string
                suburbs_list = suburbs.split(",") if suburbs else None
                result = self.tool.search_by_criteria(
                    suburbs=suburbs_list,
                    min_land_area=min_land_area,
                    max_price=max_price,
                    property_type=property_type,
                    development_potential=True
                )
                return json.dumps(result, indent=2)

            @kernel_function(
                name="get_listing_details",
                description="Get detailed information about a specific property listing using its listing ID"
            )
            def get_listing_details(self, listing_id: str) -> str:
                """Get listing details."""
                result = self.tool.get_listing_details(listing_id)
                return json.dumps(result, indent=2)

            @kernel_function(
                name="calculate_metrics",
                description="Calculate development metrics (ROI, potential dwellings, estimated profit) for a property listing using its listing ID"
            )
            def calculate_metrics(self, listing_id: str) -> str:
                """Calculate development metrics."""
                result = self.tool.calculate_development_metrics(listing_id)
                return json.dumps(result, indent=2)

        # Register plugins
        self.kernel.add_plugin(
            PlanningPlugin(self.planning_tool),
            plugin_name="PlanningTools"
        )
        self.kernel.add_plugin(
            PropertyPlugin(self.property_tool),
            plugin_name="PropertyTools"
        )

    async def find_development_sites(self, criteria: Dict) -> List[Dict]:
        """
        Find development sites based on criteria.

        Args:
            criteria: Dictionary with search criteria
                - suburbs: List of suburbs
                - min_land_area: Minimum land area (sqm)
                - max_price: Maximum price (AUD)
                - zone_types: Preferred zone types
                - property_types: Property types to consider

        Returns:
            List of matching development sites with analysis
        """
        prompt = f"""
        I need to find great development sites in Brisbane with the following criteria:
        {json.dumps(criteria, indent=2)}

        Please:
        1. Search for properties that match these criteria
        2. Check the zoning and development potential for each property
        3. Calculate the development metrics (ROI, potential dwellings)
        4. Provide a ranked list of the best opportunities

        Focus on properties with strong development potential and good returns.
        """

        # Add to chat history
        self.chat_history.add_user_message(prompt)

        # Get chat completion with function calling
        chat_completion = self.kernel.get_service()
        execution_settings = chat_completion.get_prompt_execution_settings_class()(
            function_choice_behavior=FunctionChoiceBehavior.Auto()
        )

        # Get response
        response = await chat_completion.get_chat_message_contents(
            chat_history=self.chat_history,
            settings=execution_settings,
            kernel=self.kernel
        )

        # Add assistant response to history
        for message in response:
            self.chat_history.add_assistant_message(str(message))

        return response

    async def analyze_specific_site(self, address: str) -> Dict:
        """
        Analyze a specific site for development potential.

        Args:
            address: Brisbane property address

        Returns:
            Comprehensive analysis of the site
        """
        prompt = f"""
        Please provide a comprehensive analysis of this Brisbane property for development:
        Address: {address}

        Include:
        1. Current zoning and overlay information
        2. Allowed development types
        3. Any property listings for this address or nearby
        4. Development potential assessment
        5. Key considerations and recommendations
        """

        self.chat_history.add_user_message(prompt)

        chat_completion = self.kernel.get_service()
        execution_settings = chat_completion.get_prompt_execution_settings_class()(
            function_choice_behavior=FunctionChoiceBehavior.Auto()
        )

        response = await chat_completion.get_chat_message_contents(
            chat_history=self.chat_history,
            settings=execution_settings,
            kernel=self.kernel
        )

        for message in response:
            self.chat_history.add_assistant_message(str(message))

        return response

    async def chat(self, user_message: str) -> str:
        """
        Chat with the agent about development sites.

        Args:
            user_message: User's question or request

        Returns:
            Agent's response
        """
        self.chat_history.add_user_message(user_message)

        chat_completion = self.kernel.get_service()
        execution_settings = chat_completion.get_prompt_execution_settings_class()(
            function_choice_behavior=FunctionChoiceBehavior.Auto()
        )

        response = await chat_completion.get_chat_message_contents(
            chat_history=self.chat_history,
            settings=execution_settings,
            kernel=self.kernel
        )

        response_text = str(response[0])
        self.chat_history.add_assistant_message(response_text)

        return response_text


async def main():
    """Main function demonstrating the agent."""
    print("=" * 70)
    print("Brisbane Development Site Finder - AI Agent")
    print("=" * 70)
    print()

    # Initialize agent
    try:
        agent = BrisbaneDevelopmentAgent()
    except ValueError as e:
        print(f"❌ Error: {e}")
        print("\nPlease set up your API keys:")
        print("  export OPENAI_API_KEY='your-key-here'")
        print("  or")
        print("  export AZURE_OPENAI_API_KEY='your-key-here'")
        print("  export AZURE_OPENAI_ENDPOINT='your-endpoint-here'")
        return

    # Example 1: Find development sites
    print("\n📍 Example 1: Finding development sites in Fortitude Valley")
    print("-" * 70)

    criteria = {
        "suburbs": ["Fortitude Valley"],
        "min_land_area": 800,
        "max_price": 5000000,
        "zone_types": ["Major Centre", "High Density Residential"]
    }

    response = await agent.find_development_sites(criteria)
    print(f"\n🤖 Agent Response:\n{response[0]}")

    # Example 2: Analyze a specific site
    print("\n\n📍 Example 2: Analyzing a specific property")
    print("-" * 70)

    response = await agent.analyze_specific_site("78 Grey Street, South Brisbane")
    print(f"\n🤖 Agent Response:\n{response[0]}")

    # Example 3: Interactive chat
    print("\n\n💬 Example 3: Chat with the agent")
    print("-" * 70)

    response = await agent.chat(
        "What are the best suburbs in Brisbane for apartment development right now?"
    )
    print(f"\n🤖 Agent Response:\n{response}")


if __name__ == "__main__":
    asyncio.run(main())
