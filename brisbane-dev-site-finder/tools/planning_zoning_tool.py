"""
Planning and Zoning Search Tool for Brisbane Development Sites
This tool searches Brisbane City Council planning and zoning data.
"""

import json
from typing import List, Dict, Optional
from datetime import datetime
import requests


class PlanningZoningTool:
    """Tool for searching Brisbane planning and zoning information."""

    def __init__(self):
        # Brisbane City Council Planning Scheme zones
        # Source: https://www.brisbane.qld.gov.au/planning-and-building/planning-guidelines-and-tools/neighbourhood-plans
        self.development_zones = {
            "High Density Residential": ["Multiple dwelling", "Apartment building", "Mixed use"],
            "Low-Medium Density Residential": ["Dual occupancy", "Multiple dwelling", "Townhouse"],
            "Community Facilities": ["Child care centre", "Community use", "Educational establishment"],
            "Major Centre": ["Shopping centre", "Office", "Entertainment facility", "Hotel"],
            "Industry": ["Warehouse", "Service industry", "Low impact industry"],
            "Mixed Use": ["Shop", "Office", "Residential", "Entertainment"]
        }

    def search_by_address(self, address: str) -> Dict:
        """
        Search planning and zoning information for a specific address.

        Args:
            address: Brisbane address to search

        Returns:
            Dictionary containing zoning information
        """
        # In production, this would call Brisbane City Council's API
        # For now, we'll simulate the response

        # Simulate API call
        zoning_info = self._simulate_zoning_lookup(address)
        return zoning_info

    def search_by_zone_type(self, zone_type: str, min_area: Optional[float] = None) -> List[Dict]:
        """
        Search for sites by zone type.

        Args:
            zone_type: Type of zone (e.g., "High Density Residential")
            min_area: Minimum land area in square meters

        Returns:
            List of sites matching the criteria
        """
        # Simulate searching for sites by zone
        sites = self._simulate_zone_search(zone_type, min_area)
        return sites

    def check_development_potential(self, address: str, proposed_use: str) -> Dict:
        """
        Check if a proposed development use is allowed in the zone.

        Args:
            address: Property address
            proposed_use: Proposed development use

        Returns:
            Dictionary with assessment results
        """
        zoning_info = self.search_by_address(address)
        zone_type = zoning_info.get("zone", "Unknown")

        # Check if proposed use is allowed in this zone
        allowed_uses = self.development_zones.get(zone_type, [])

        assessment = {
            "address": address,
            "current_zone": zone_type,
            "proposed_use": proposed_use,
            "is_allowed": proposed_use in allowed_uses,
            "allowed_uses": allowed_uses,
            "requires_approval": True,  # Most developments need approval
            "assessment_date": datetime.now().isoformat()
        }

        return assessment

    def _simulate_zoning_lookup(self, address: str) -> Dict:
        """Simulate looking up zoning information (replace with real API in production)."""

        # Sample data for demonstration
        # In production, this would query Brisbane City Council's data
        sample_zones = {
            "fortitude valley": {
                "address": address,
                "zone": "Major Centre",
                "overlay": ["Character residential area", "Transport"],
                "height_limit": "No limit (subject to assessment)",
                "plot_ratio": "Up to 3:1",
                "council_area": "Brisbane City",
                "suburb": "Fortitude Valley",
                "last_updated": "2026-01-15"
            },
            "new farm": {
                "address": address,
                "zone": "Low-Medium Density Residential",
                "overlay": ["Character residential area"],
                "height_limit": "8.5m (2 storeys)",
                "plot_ratio": "0.5:1",
                "council_area": "Brisbane City",
                "suburb": "New Farm",
                "last_updated": "2026-01-15"
            },
            "south brisbane": {
                "address": address,
                "zone": "High Density Residential",
                "overlay": ["Mixed use"],
                "height_limit": "Subject to assessment",
                "plot_ratio": "2:1",
                "council_area": "Brisbane City",
                "suburb": "South Brisbane",
                "last_updated": "2026-01-15"
            }
        }

        # Simple matching based on address
        address_lower = address.lower()
        for suburb, data in sample_zones.items():
            if suburb in address_lower:
                return data

        # Default response if no match
        return {
            "address": address,
            "zone": "Unknown",
            "overlay": [],
            "height_limit": "Unknown",
            "plot_ratio": "Unknown",
            "council_area": "Brisbane City",
            "suburb": "Unknown",
            "note": "Use Brisbane City Council's online mapping tool for accurate information",
            "last_updated": datetime.now().strftime("%Y-%m-%d")
        }

    def _simulate_zone_search(self, zone_type: str, min_area: Optional[float]) -> List[Dict]:
        """Simulate searching for sites by zone type."""

        # Sample development sites
        sample_sites = [
            {
                "address": "123 Brunswick Street, Fortitude Valley QLD 4006",
                "zone": "Major Centre",
                "land_area_sqm": 850,
                "frontage_m": 15,
                "depth_m": 56.67,
                "existing_use": "Commercial building",
                "potential": "High-rise mixed use development"
            },
            {
                "address": "45 Merthyr Road, New Farm QLD 4005",
                "zone": "Low-Medium Density Residential",
                "land_area_sqm": 650,
                "frontage_m": 12.5,
                "depth_m": 52,
                "existing_use": "Residential house",
                "potential": "Dual occupancy or townhouse development"
            },
            {
                "address": "78 Grey Street, South Brisbane QLD 4101",
                "zone": "High Density Residential",
                "land_area_sqm": 1200,
                "frontage_m": 20,
                "depth_m": 60,
                "existing_use": "Old warehouse",
                "potential": "Apartment building development"
            },
            {
                "address": "22 Boundary Street, West End QLD 4101",
                "zone": "Mixed Use",
                "land_area_sqm": 950,
                "frontage_m": 19,
                "depth_m": 50,
                "existing_use": "Retail shop",
                "potential": "Mixed use residential and commercial"
            }
        ]

        # Filter by zone type and minimum area
        results = []
        for site in sample_sites:
            if zone_type and zone_type != site["zone"]:
                continue
            if min_area and site["land_area_sqm"] < min_area:
                continue
            results.append(site)

        return results


# Semantic Kernel function decorators for AI agent integration
def get_planning_tool_functions():
    """Returns planning/zoning functions for Semantic Kernel integration."""

    tool = PlanningZoningTool()

    functions = {
        "search_zoning_by_address": {
            "function": tool.search_by_address,
            "description": "Search Brisbane City Council planning and zoning information for a specific address",
            "parameters": {
                "address": "The Brisbane address to search for zoning information"
            }
        },
        "search_sites_by_zone": {
            "function": tool.search_by_zone_type,
            "description": "Search for development sites by zone type and minimum land area",
            "parameters": {
                "zone_type": "Zone type (e.g., 'High Density Residential', 'Major Centre', 'Mixed Use')",
                "min_area": "Minimum land area in square meters (optional)"
            }
        },
        "check_development_potential": {
            "function": tool.check_development_potential,
            "description": "Check if a proposed development use is allowed for a property",
            "parameters": {
                "address": "Property address",
                "proposed_use": "Proposed development type (e.g., 'Apartment building', 'Mixed use')"
            }
        }
    }

    return functions


if __name__ == "__main__":
    # Test the tool
    tool = PlanningZoningTool()

    print("=== Testing Planning & Zoning Tool ===\n")

    # Test 1: Search by address
    print("1. Searching zoning for Fortitude Valley address:")
    result = tool.search_by_address("123 Brunswick Street, Fortitude Valley")
    print(json.dumps(result, indent=2))

    print("\n2. Searching sites by zone type:")
    sites = tool.search_by_zone_type("High Density Residential", min_area=1000)
    print(json.dumps(sites, indent=2))

    print("\n3. Checking development potential:")
    assessment = tool.check_development_potential(
        "78 Grey Street, South Brisbane",
        "Apartment building"
    )
    print(json.dumps(assessment, indent=2))
