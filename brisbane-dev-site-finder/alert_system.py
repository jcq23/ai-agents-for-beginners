"""
Alert Notification System for Brisbane Development Site Finder

This system monitors property listings and sends alerts when new sites
matching the criteria are found.
"""

import os
import json
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from agent import BrisbaneDevelopmentAgent
from tools.property_listing_tool import PropertyListingTool
from tools.planning_zoning_tool import PlanningZoningTool


class AlertSystem:
    """System for monitoring and alerting on development site opportunities."""

    def __init__(self, config_path: str = "alert_config.json"):
        """
        Initialize the alert system.

        Args:
            config_path: Path to alert configuration file
        """
        self.config_path = config_path
        self.config = self._load_config()
        self.property_tool = PropertyListingTool()
        self.planning_tool = PlanningZoningTool()
        self.seen_listings = set()
        self.alert_history_path = "data/alert_history.json"

        # Load alert history
        self._load_alert_history()

        print("✅ Alert System initialized!")

    def _load_config(self) -> Dict:
        """Load alert configuration."""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                return json.load(f)
        else:
            # Return default configuration
            return {
                "search_criteria": {
                    "suburbs": ["Fortitude Valley", "South Brisbane", "West End", "New Farm"],
                    "min_land_area": 600,
                    "max_price": 5000000,
                    "property_types": ["Commercial", "House", "Land", "Industrial"],
                    "zones": ["High Density Residential", "Major Centre", "Mixed Use"]
                },
                "alert_preferences": {
                    "email_enabled": False,
                    "email_to": "your-email@example.com",
                    "console_enabled": True,
                    "min_roi_percentage": 20,
                    "min_estimated_dwellings": 5
                },
                "monitoring": {
                    "check_interval_minutes": 60,
                    "enabled": True
                }
            }

    def _save_config(self):
        """Save alert configuration."""
        with open(self.config_path, 'w') as f:
            json.dumps(self.config, f, indent=2)

    def _load_alert_history(self):
        """Load history of sent alerts."""
        if os.path.exists(self.alert_history_path):
            with open(self.alert_history_path, 'r') as f:
                history = json.load(f)
                self.seen_listings = set(history.get("seen_listings", []))
        else:
            self.seen_listings = set()

    def _save_alert_history(self):
        """Save history of sent alerts."""
        os.makedirs(os.path.dirname(self.alert_history_path), exist_ok=True)
        with open(self.alert_history_path, 'w') as f:
            json.dump({
                "seen_listings": list(self.seen_listings),
                "last_updated": datetime.now().isoformat()
            }, f, indent=2)

    def check_for_matches(self) -> List[Dict]:
        """
        Check for properties matching the search criteria.

        Returns:
            List of matching properties
        """
        criteria = self.config["search_criteria"]

        # Search for properties
        results = self.property_tool.search_by_criteria(
            suburbs=criteria.get("suburbs"),
            min_land_area=criteria.get("min_land_area"),
            max_price=criteria.get("max_price"),
            property_type=None,  # Search all types
            development_potential=True
        )

        # Filter new listings only
        new_matches = []
        for listing in results:
            listing_id = listing["listing_id"]
            if listing_id not in self.seen_listings:
                # Calculate development metrics
                metrics = self.property_tool.calculate_development_metrics(listing_id)

                # Check if meets ROI and dwelling criteria
                alert_prefs = self.config["alert_preferences"]
                if (metrics.get("roi_percentage", 0) >= alert_prefs.get("min_roi_percentage", 0) and
                    metrics.get("buildable_units", 0) >= alert_prefs.get("min_estimated_dwellings", 0)):

                    # Get zoning info
                    zoning = self.planning_tool.search_by_address(listing["address"])

                    new_matches.append({
                        "listing": listing,
                        "metrics": metrics,
                        "zoning": zoning,
                        "found_date": datetime.now().isoformat()
                    })

                    # Mark as seen
                    self.seen_listings.add(listing_id)

        # Save updated history
        if new_matches:
            self._save_alert_history()

        return new_matches

    def send_alert(self, matches: List[Dict]):
        """
        Send alerts for matched properties.

        Args:
            matches: List of matched properties with analysis
        """
        if not matches:
            return

        alert_prefs = self.config["alert_preferences"]

        # Console alert
        if alert_prefs.get("console_enabled", True):
            self._send_console_alert(matches)

        # Email alert
        if alert_prefs.get("email_enabled", False):
            self._send_email_alert(matches)

    def _send_console_alert(self, matches: List[Dict]):
        """Print alert to console."""
        print("\n" + "=" * 90)
        print("🚨 NEW DEVELOPMENT SITE ALERT!")
        print("=" * 90)
        print(f"\nFound {len(matches)} new matching propert{'y' if len(matches) == 1 else 'ies'}:\n")

        for i, match in enumerate(matches, 1):
            listing = match["listing"]
            metrics = match["metrics"]
            zoning = match["zoning"]

            print(f"\n{i}. {listing['address']}")
            print(f"   📍 Suburb: {listing['suburb']}")
            print(f"   💰 Purchase Price: ${listing['price']:,}")
            print(f"   📏 Land Area: {listing['land_area_sqm']} sqm")

            # Holding income metrics
            rental_income = metrics.get('current_rental_income_pa', 0)
            passing_yield = metrics.get('passing_yield_percentage', 0)
            if rental_income > 0:
                print(f"   💵 Current Rental Income: ${rental_income:,} p.a.")
                print(f"   📈 Passing Yield: {passing_yield:.2f}%")
            else:
                print(f"   💵 Current Rental Income: Vacant (no holding income)")

            print(f"   🏗️  Zoning: {zoning.get('zone', 'Unknown')} (FAR: {metrics.get('floor_area_ratio', 0)})")

            # Developable area metrics
            print(f"\n   📐 DEVELOPABLE AREA:")
            print(f"      • Gross Floor Area: {metrics.get('gross_floor_area_sqm', 0):,.0f} sqm")
            print(f"      • Net Floor Area (80% efficiency): {metrics.get('net_floor_area_sqm', 0):,.0f} sqm")
            print(f"      • Buildable Units (60sqm avg): {metrics.get('buildable_units', 0)} units")

            # Cost metrics
            print(f"\n   💲 COST METRICS:")
            print(f"      • Price per Land sqm: ${metrics.get('price_per_land_sqm', 0):,.2f}")
            print(f"      • Price per Developable sqm: ${metrics.get('price_per_developable_sqm', 0):,.2f}")
            print(f"      • Price per Buildable Unit: ${metrics.get('price_per_buildable_unit', 0):,.2f}")

            # Development potential
            print(f"\n   🏘️  DEVELOPMENT POTENTIAL:")
            print(f"      • Estimated ROI: {metrics.get('roi_percentage', 0):.1f}%")
            print(f"      • Estimated Profit: ${metrics.get('estimated_profit', 0):,}")
            print(f"      • Potential Gross Value: ${metrics.get('potential_gross_value', 0):,}")
            print(f"      • Est. Construction Cost: ${metrics.get('estimated_construction_cost', 0):,}")

            print(f"\n   📱 Agent: {listing['agent']} - {listing['contact']}")
            print(f"   📝 {listing['description']}")
            print(f"   🔗 Listing ID: {listing['listing_id']}")

            # Listing URL
            listing_url = listing.get('listing_url', 'URL not available')
            print(f"   🌐 View Listing: {listing_url}")

            # Summary Section
            print(f"\n   📋 SUMMARY:")
            print(f"      • Purchase Yield: {passing_yield:.2f}%" if rental_income > 0 else f"      • Purchase Yield: N/A (vacant)")
            print(f"      • Price per Unit: ${metrics.get('price_per_buildable_unit', 0):,.2f}")

        print("\n" + "=" * 90)

    def _send_email_alert(self, matches: List[Dict]):
        """
        Send email alert (requires SMTP configuration).

        Args:
            matches: List of matched properties
        """
        alert_prefs = self.config["alert_preferences"]
        email_to = alert_prefs.get("email_to")

        if not email_to or email_to == "your-email@example.com":
            print("⚠️  Email alerts not configured. Set email_to in alert_config.json")
            return

        # Create email content
        subject = f"🚨 {len(matches)} New Development Site{'s' if len(matches) > 1 else ''} Found in Brisbane!"

        html_content = self._create_email_html(matches)

        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = os.getenv("SMTP_FROM_EMAIL", "alerts@dev-site-finder.com")
        msg['To'] = email_to

        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)

        # Send email (requires SMTP configuration)
        try:
            smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
            smtp_port = int(os.getenv("SMTP_PORT", "587"))
            smtp_username = os.getenv("SMTP_USERNAME")
            smtp_password = os.getenv("SMTP_PASSWORD")

            if not smtp_username or not smtp_password:
                print("⚠️  SMTP credentials not configured. Set SMTP_USERNAME and SMTP_PASSWORD environment variables.")
                return

            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.send_message(msg)

            print(f"✅ Email alert sent to {email_to}")

        except Exception as e:
            print(f"❌ Failed to send email: {e}")

    def _create_email_html(self, matches: List[Dict]) -> str:
        """Create HTML email content."""
        properties_html = ""

        for match in matches:
            listing = match["listing"]
            metrics = match["metrics"]
            zoning = match["zoning"]

            # Format holding income section
            rental_income = metrics.get('current_rental_income_pa', 0)
            passing_yield = metrics.get('passing_yield_percentage', 0)
            holding_income_html = ""
            if rental_income > 0:
                holding_income_html = f"""
                <p><strong>💵 Current Rental Income:</strong> ${rental_income:,} p.a.</p>
                <p><strong>📈 Passing Yield:</strong> {passing_yield:.2f}%</p>
                """
            else:
                holding_income_html = "<p><strong>💵 Current Rental Income:</strong> Vacant (no holding income)</p>"

            properties_html += f"""
            <div style="border: 1px solid #ddd; padding: 20px; margin: 20px 0; border-radius: 8px; background-color: #f9f9f9;">
                <h3 style="color: #2c3e50; margin-top: 0;">{listing['address']}</h3>
                <p><strong>📍 Suburb:</strong> {listing['suburb']}</p>
                <p><strong>💰 Purchase Price:</strong> ${listing['price']:,}</p>
                <p><strong>📏 Land Area:</strong> {listing['land_area_sqm']} sqm</p>
                {holding_income_html}
                <p><strong>🏗️ Zoning:</strong> {zoning.get('zone', 'Unknown')} (FAR: {metrics.get('floor_area_ratio', 0)})</p>

                <h4 style="color: #34495e; margin-top: 15px; margin-bottom: 10px;">📐 Developable Area</h4>
                <ul style="margin: 5px 0;">
                    <li><strong>Gross Floor Area:</strong> {metrics.get('gross_floor_area_sqm', 0):,.0f} sqm</li>
                    <li><strong>Net Floor Area (80% efficiency):</strong> {metrics.get('net_floor_area_sqm', 0):,.0f} sqm</li>
                    <li><strong>Buildable Units (60sqm avg):</strong> {metrics.get('buildable_units', 0)} units</li>
                </ul>

                <h4 style="color: #34495e; margin-top: 15px; margin-bottom: 10px;">💲 Cost Metrics</h4>
                <ul style="margin: 5px 0;">
                    <li><strong>Price per Land sqm:</strong> ${metrics.get('price_per_land_sqm', 0):,.2f}</li>
                    <li><strong>Price per Developable sqm:</strong> ${metrics.get('price_per_developable_sqm', 0):,.2f}</li>
                    <li><strong>Price per Buildable Unit:</strong> ${metrics.get('price_per_buildable_unit', 0):,.2f}</li>
                </ul>

                <h4 style="color: #34495e; margin-top: 15px; margin-bottom: 10px;">🏘️ Development Potential</h4>
                <ul style="margin: 5px 0;">
                    <li><strong>Estimated ROI:</strong> {metrics.get('roi_percentage', 0):.1f}%</li>
                    <li><strong>Estimated Profit:</strong> ${metrics.get('estimated_profit', 0):,}</li>
                    <li><strong>Potential Gross Value:</strong> ${metrics.get('potential_gross_value', 0):,}</li>
                    <li><strong>Est. Construction Cost:</strong> ${metrics.get('estimated_construction_cost', 0):,}</li>
                </ul>

                <p style="margin-top: 15px;"><strong>📱 Agent:</strong> {listing['agent']} - {listing['contact']}</p>
                <p style="color: #7f8c8d;">{listing['description']}</p>
                <p><em>Listing ID: {listing['listing_id']}</em></p>
                <p><strong>🌐 View Listing:</strong> <a href="{listing.get('listing_url', '#')}">{listing.get('listing_url', 'URL not available')}</a></p>

                <h4 style="color: #27ae60; margin-top: 15px; margin-bottom: 10px;">📋 Summary</h4>
                <ul style="margin: 5px 0; background-color: #e8f5e9; padding: 10px; border-radius: 4px;">
                    <li><strong>Purchase Yield:</strong> {passing_yield:.2f}%</li>
                    <li><strong>Price per Unit:</strong> ${metrics.get('price_per_buildable_unit', 0):,.2f}</li>
                </ul>
            </div>
            """

        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background-color: #3498db; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .footer {{ background-color: #ecf0f1; padding: 10px; text-align: center; font-size: 12px; color: #7f8c8d; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🚨 New Development Sites Found!</h1>
                <p>Brisbane Development Site Finder Alert</p>
            </div>
            <div class="content">
                <p>Great news! We found {len(matches)} new development site{'s' if len(matches) > 1 else ''} matching your criteria:</p>
                {properties_html}
                <p style="margin-top: 30px;"><em>Note: These estimates are simplified. Always conduct proper due diligence before proceeding with any development.</em></p>
            </div>
            <div class="footer">
                <p>Brisbane Development Site Finder | Powered by AI</p>
                <p>{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            </div>
        </body>
        </html>
        """

        return html

    async def start_monitoring(self):
        """Start continuous monitoring for new properties."""
        print("\n🔍 Starting monitoring for development sites...")
        print(f"⏰ Check interval: {self.config['monitoring']['check_interval_minutes']} minutes")
        print("Press Ctrl+C to stop\n")

        check_count = 0

        try:
            while self.config['monitoring']['enabled']:
                check_count += 1
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"\n[{timestamp}] Check #{check_count}: Searching for new listings...")

                # Check for matches
                matches = self.check_for_matches()

                if matches:
                    print(f"✅ Found {len(matches)} new matching propert{'y' if len(matches) == 1 else 'ies'}!")
                    self.send_alert(matches)
                else:
                    print("ℹ️  No new matches found.")

                # Wait before next check
                interval = self.config['monitoring']['check_interval_minutes'] * 60
                print(f"💤 Waiting {self.config['monitoring']['check_interval_minutes']} minutes until next check...")
                await asyncio.sleep(interval)

        except KeyboardInterrupt:
            print("\n\n⏹️  Monitoring stopped by user.")

    def run_once(self):
        """Run a single check for matching properties."""
        print("\n🔍 Checking for development sites...\n")

        matches = self.check_for_matches()

        if matches:
            print(f"✅ Found {len(matches)} matching propert{'y' if len(matches) == 1 else 'ies'}!")
            self.send_alert(matches)
        else:
            print("ℹ️  No new matches found.")

        return matches


async def main():
    """Main function for running the alert system."""
    import argparse

    parser = argparse.ArgumentParser(description="Brisbane Development Site Alert System")
    parser.add_argument(
        "--mode",
        choices=["once", "monitor"],
        default="once",
        help="Run once or continuous monitoring (default: once)"
    )
    parser.add_argument(
        "--config",
        default="alert_config.json",
        help="Path to alert configuration file"
    )

    args = parser.parse_args()

    print("=" * 80)
    print("Brisbane Development Site Alert System")
    print("=" * 80)

    alert_system = AlertSystem(config_path=args.config)

    if args.mode == "once":
        alert_system.run_once()
    else:
        await alert_system.start_monitoring()


if __name__ == "__main__":
    asyncio.run(main())
