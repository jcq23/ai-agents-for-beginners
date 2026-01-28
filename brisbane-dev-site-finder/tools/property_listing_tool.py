"""
Property Listing Search Tool for Brisbane Development Sites
This tool searches online property listings for development opportunities.
"""

import json
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import random


class PropertyListingTool:
    """Tool for searching property listings for development sites."""

    def __init__(self):
        # Simulated property listings database
        # In production, this would integrate with real estate APIs like:
        # - Domain.com.au API
        # - REA (realestate.com.au) API
        # - CoreLogic API
        # - Private real estate agent feeds
        self.listings = self._generate_sample_listings()

    def search_by_criteria(
        self,
        suburbs: Optional[List[str]] = None,
        min_land_area: Optional[float] = None,
        max_price: Optional[float] = None,
        property_type: Optional[str] = None,
        development_potential: bool = True
    ) -> List[Dict]:
        """
        Search property listings by various criteria.

        Args:
            suburbs: List of Brisbane suburbs to search
            min_land_area: Minimum land area in square meters
            max_price: Maximum price in AUD
            property_type: Type of property (e.g., "Land", "House", "Commercial")
            development_potential: Filter for properties with development potential

        Returns:
            List of matching property listings
        """
        results = []

        for listing in self.listings:
            # Filter by suburb
            if suburbs and listing["suburb"] not in suburbs:
                continue

            # Filter by land area
            if min_land_area and listing["land_area_sqm"] < min_land_area:
                continue

            # Filter by price
            if max_price and listing["price"] > max_price:
                continue

            # Filter by property type
            if property_type and listing["property_type"] != property_type:
                continue

            # Filter by development potential
            if development_potential and not listing["development_potential"]:
                continue

            results.append(listing)

        return results

    def get_listing_details(self, listing_id: str) -> Optional[Dict]:
        """
        Get detailed information about a specific listing.

        Args:
            listing_id: Unique identifier for the listing

        Returns:
            Detailed listing information or None if not found
        """
        for listing in self.listings:
            if listing["listing_id"] == listing_id:
                return listing
        return None

    def calculate_development_metrics(self, listing_id: str) -> Dict:
        """
        Calculate development metrics for a property.

        Args:
            listing_id: Unique identifier for the listing

        Returns:
            Development metrics and analysis
        """
        listing = self.get_listing_details(listing_id)
        if not listing:
            return {"error": "Listing not found"}

        # Calculate metrics
        price_per_sqm = listing["price"] / listing["land_area_sqm"]

        # Estimate development potential based on zoning
        zone = listing.get("zone", "Unknown")
        estimated_dwellings = self._estimate_dwellings(listing["land_area_sqm"], zone)

        # Calculate potential returns (simplified)
        avg_apartment_value = 650000  # Average Brisbane apartment value
        potential_gross_value = estimated_dwellings * avg_apartment_value
        construction_cost_per_sqm = 2500  # Approximate construction cost
        estimated_construction_cost = estimated_dwellings * 80 * construction_cost_per_sqm  # 80sqm avg apartment

        metrics = {
            "listing_id": listing_id,
            "address": listing["address"],
            "price_per_sqm": round(price_per_sqm, 2),
            "estimated_dwellings": estimated_dwellings,
            "potential_gross_value": potential_gross_value,
            "estimated_construction_cost": estimated_construction_cost,
            "estimated_profit": potential_gross_value - listing["price"] - estimated_construction_cost,
            "roi_percentage": round(
                ((potential_gross_value - listing["price"] - estimated_construction_cost) / listing["price"]) * 100,
                2
            ),
            "note": "These are simplified estimates. Conduct proper due diligence before proceeding."
        }

        return metrics

    def _estimate_dwellings(self, land_area: float, zone: str) -> int:
        """Estimate number of dwellings based on land area and zone."""
        # Simplified estimation
        if zone == "High Density Residential":
            return max(1, int(land_area / 100))  # ~100sqm per dwelling
        elif zone == "Major Centre":
            return max(1, int(land_area / 80))  # ~80sqm per dwelling
        elif zone == "Mixed Use":
            return max(1, int(land_area / 120))  # ~120sqm per dwelling
        else:
            return max(1, int(land_area / 300))  # Low density

    def _generate_sample_listings(self) -> List[Dict]:
        """Generate sample property listings for demonstration."""
        base_date = datetime.now()

        listings = [
            {
                "listing_id": "BNE-001",
                "address": "123 Brunswick Street, Fortitude Valley QLD 4006",
                "suburb": "Fortitude Valley",
                "property_type": "Commercial",
                "price": 2800000,
                "land_area_sqm": 850,
                "zone": "Major Centre",
                "development_potential": True,
                "description": "Prime corner site in heart of Fortitude Valley. Ideal for mixed-use development.",
                "existing_improvements": "Old commercial building",
                "frontage_m": 15,
                "listed_date": (base_date - timedelta(days=14)).strftime("%Y-%m-%d"),
                "agent": "Ray White Commercial",
                "contact": "07 3123 4567"
            },
            {
                "listing_id": "BNE-002",
                "address": "78 Grey Street, South Brisbane QLD 4101",
                "suburb": "South Brisbane",
                "property_type": "Industrial",
                "price": 3500000,
                "land_area_sqm": 1200,
                "zone": "High Density Residential",
                "development_potential": True,
                "description": "Warehouse conversion opportunity. High density residential zoning. Walk to CBD.",
                "existing_improvements": "Warehouse circa 1960s",
                "frontage_m": 20,
                "listed_date": (base_date - timedelta(days=7)).strftime("%Y-%m-%d"),
                "agent": "Colliers International",
                "contact": "07 3222 3333"
            },
            {
                "listing_id": "BNE-003",
                "address": "45 Merthyr Road, New Farm QLD 4005",
                "suburb": "New Farm",
                "property_type": "House",
                "price": 1650000,
                "land_area_sqm": 650,
                "zone": "Low-Medium Density Residential",
                "development_potential": True,
                "description": "Character home on large block. Dual occupancy or townhouse potential.",
                "existing_improvements": "1920s Queenslander home",
                "frontage_m": 12.5,
                "listed_date": (base_date - timedelta(days=21)).strftime("%Y-%m-%d"),
                "agent": "Place Estate Agents",
                "contact": "07 3358 8888"
            },
            {
                "listing_id": "BNE-004",
                "address": "22 Boundary Street, West End QLD 4101",
                "suburb": "West End",
                "property_type": "Commercial",
                "price": 2200000,
                "land_area_sqm": 950,
                "zone": "Mixed Use",
                "development_potential": True,
                "description": "Mixed-use site on busy Boundary Street. Retail below, residential above potential.",
                "existing_improvements": "Two-storey retail building",
                "frontage_m": 19,
                "listed_date": (base_date - timedelta(days=3)).strftime("%Y-%m-%d"),
                "agent": "CBRE",
                "contact": "07 3222 1111"
            },
            {
                "listing_id": "BNE-005",
                "address": "156 Latrobe Terrace, Paddington QLD 4064",
                "suburb": "Paddington",
                "property_type": "House",
                "price": 2100000,
                "land_area_sqm": 810,
                "zone": "Low-Medium Density Residential",
                "development_potential": True,
                "description": "Blue-chip Paddington address. Excellent for townhouse development.",
                "existing_improvements": "1930s cottage (ready for demolition)",
                "frontage_m": 15.5,
                "listed_date": (base_date - timedelta(days=10)).strftime("%Y-%m-%d"),
                "agent": "McGrath Estate Agents",
                "contact": "07 3369 9999"
            },
            {
                "listing_id": "BNE-006",
                "address": "88 Wickham Street, Fortitude Valley QLD 4006",
                "suburb": "Fortitude Valley",
                "property_type": "Land",
                "price": 4200000,
                "land_area_sqm": 1500,
                "zone": "Major Centre",
                "development_potential": True,
                "description": "Rare vacant land in Fortitude Valley. Approved plans for 15-storey tower available.",
                "existing_improvements": "Vacant land",
                "frontage_m": 25,
                "listed_date": (base_date - timedelta(days=5)).strftime("%Y-%m-%d"),
                "agent": "Knight Frank",
                "contact": "07 3246 8888"
            },
            {
                "listing_id": "BNE-007",
                "address": "33 Robertson Street, Fortitude Valley QLD 4006",
                "suburb": "Fortitude Valley",
                "property_type": "Commercial",
                "price": 1950000,
                "land_area_sqm": 600,
                "zone": "Major Centre",
                "development_potential": True,
                "description": "Small but perfectly formed site. Ideal for boutique apartment building.",
                "existing_improvements": "Small office building",
                "frontage_m": 12,
                "listed_date": (base_date - timedelta(days=28)).strftime("%Y-%m-%d"),
                "agent": "LJ Hooker Commercial",
                "contact": "07 3252 5555"
            },
            {
                "listing_id": "BNE-008",
                "address": "210 Given Terrace, Paddington QLD 4064",
                "suburb": "Paddington",
                "property_type": "House",
                "price": 1250000,
                "land_area_sqm": 405,
                "zone": "Low-Medium Density Residential",
                "development_potential": False,
                "description": "Renovated character home. Not suitable for development due to size.",
                "existing_improvements": "Renovated Queenslander",
                "frontage_m": 10,
                "listed_date": (base_date - timedelta(days=12)).strftime("%Y-%m-%d"),
                "agent": "Ray White Paddington",
                "contact": "07 3368 7777"
            }
        ]

        return listings


# Semantic Kernel function decorators for AI agent integration
def get_property_tool_functions():
    """Returns property listing functions for Semantic Kernel integration."""

    tool = PropertyListingTool()

    functions = {
        "search_properties": {
            "function": tool.search_by_criteria,
            "description": "Search property listings by criteria including suburbs, land area, price, and development potential",
            "parameters": {
                "suburbs": "List of Brisbane suburbs to search (optional)",
                "min_land_area": "Minimum land area in square meters (optional)",
                "max_price": "Maximum price in AUD (optional)",
                "property_type": "Property type: 'Land', 'House', 'Commercial', 'Industrial' (optional)",
                "development_potential": "Filter for properties with development potential (default: True)"
            }
        },
        "get_listing_details": {
            "function": tool.get_listing_details,
            "description": "Get detailed information about a specific property listing",
            "parameters": {
                "listing_id": "Unique listing identifier (e.g., 'BNE-001')"
            }
        },
        "calculate_development_metrics": {
            "function": tool.calculate_development_metrics,
            "description": "Calculate development metrics including ROI, potential dwellings, and estimated profit for a property",
            "parameters": {
                "listing_id": "Unique listing identifier"
            }
        }
    }

    return functions


if __name__ == "__main__":
    # Test the tool
    tool = PropertyListingTool()

    print("=== Testing Property Listing Tool ===\n")

    # Test 1: Search by criteria
    print("1. Searching for properties in Fortitude Valley with min 800 sqm:")
    results = tool.search_by_criteria(
        suburbs=["Fortitude Valley"],
        min_land_area=800
    )
    for prop in results:
        print(f"  - {prop['address']}: {prop['land_area_sqm']} sqm, ${prop['price']:,}")

    print("\n2. Getting listing details:")
    details = tool.get_listing_details("BNE-002")
    print(json.dumps(details, indent=2))

    print("\n3. Calculating development metrics:")
    metrics = tool.calculate_development_metrics("BNE-002")
    print(json.dumps(metrics, indent=2))
