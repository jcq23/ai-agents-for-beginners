# Brisbane Development Site Finder 🏗️

An AI-powered application that finds great development sites in Brisbane by searching planning and zoning guides and monitoring online property listings. It automatically sends alerts when suitable development opportunities are found.

## Features

- 🔍 **AI-Powered Search**: Uses AI agents to intelligently search and analyze development opportunities
- 📋 **Planning & Zoning Integration**: Searches Brisbane City Council planning and zoning data
- 🏘️ **Property Listing Monitor**: Monitors online property listings for development opportunities
- 📊 **Development Analysis**: Calculates ROI, potential dwellings, and estimated profits
- 🚨 **Smart Alerts**: Sends notifications when properties matching your criteria are found
- 💬 **Interactive Chat**: Chat with the AI agent about development opportunities

## Architecture

This application demonstrates the **Tool Use Design Pattern** for AI agents, using Microsoft's Semantic Kernel framework:

```
┌─────────────────────────────────────────────┐
│         AI Agent (Semantic Kernel)          │
│                                             │
│  • Natural language understanding           │
│  • Function calling & tool orchestration    │
│  • Context-aware recommendations            │
└─────────────────┬───────────────────────────┘
                  │
        ┌─────────┴──────────┐
        │                    │
┌───────▼────────┐  ┌───────▼────────┐
│ Planning Tool  │  │ Property Tool  │
│                │  │                │
│ • Zoning info  │  │ • Listings     │
│ • Development  │  │ • Metrics      │
│   potential    │  │ • Analysis     │
└────────────────┘  └────────────────┘
```

## Installation

### Prerequisites

- Python 3.8 or higher
- OpenAI API key or Azure OpenAI access
- (Optional) SMTP credentials for email alerts

### Setup Steps

1. **Clone or navigate to the directory**:
   ```bash
   cd brisbane-dev-site-finder
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

   Required configuration:
   ```bash
   # For OpenAI
   OPENAI_API_KEY=your-openai-api-key-here

   # OR for Azure OpenAI
   AZURE_OPENAI_API_KEY=your-azure-openai-api-key-here
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   ```

5. **Configure alert preferences** (optional):
   Edit `alert_config.json` to customize:
   - Suburbs to monitor
   - Price range
   - Minimum land area
   - ROI thresholds
   - Email settings

## Usage

### 1. Interactive AI Agent

Chat with the AI agent to find and analyze development sites:

```bash
python agent.py
```

Example interactions:
- "Find me development sites in Fortitude Valley under $4 million"
- "Analyze 78 Grey Street, South Brisbane for apartment development"
- "What are the best suburbs for high-density residential development?"

### 2. Alert System - Single Check

Run a one-time check for matching properties:

```bash
python alert_system.py --mode once
```

This will:
- Search for properties matching your criteria
- Analyze development potential
- Display console alerts for new matches
- Save results to avoid duplicate alerts

### 3. Alert System - Continuous Monitoring

Run continuous monitoring for new listings:

```bash
python alert_system.py --mode monitor
```

This will:
- Check for new listings at regular intervals (default: every 60 minutes)
- Send alerts when matches are found
- Continue running until you press Ctrl+C

### 4. Test Individual Tools

Test the planning/zoning tool:

```bash
python tools/planning_zoning_tool.py
```

Test the property listing tool:

```bash
python tools/property_listing_tool.py
```

## Configuration

### Alert Configuration (`alert_config.json`)

```json
{
  "search_criteria": {
    "suburbs": ["Fortitude Valley", "South Brisbane", "West End"],
    "min_land_area": 600,
    "max_price": 5000000,
    "zones": ["High Density Residential", "Major Centre", "Mixed Use"]
  },
  "alert_preferences": {
    "email_enabled": false,
    "console_enabled": true,
    "min_roi_percentage": 20,
    "min_estimated_dwellings": 5
  },
  "monitoring": {
    "check_interval_minutes": 60
  }
}
```

### Email Alerts

To enable email alerts:

1. Set up SMTP credentials in `.env`:
   ```bash
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   ```

2. Enable email in `alert_config.json`:
   ```json
   {
     "alert_preferences": {
       "email_enabled": true,
       "email_to": "your-email@example.com"
     }
   }
   ```

**Note**: For Gmail, you'll need to use an [App Password](https://support.google.com/accounts/answer/185833) instead of your regular password.

## How It Works

### 1. Planning & Zoning Tool

Searches Brisbane City Council data for:
- Current zoning classification
- Overlay zones
- Height limits and plot ratios
- Allowed development types
- Development potential assessment

### 2. Property Listing Tool

Searches property listings for:
- Land area and frontage
- Price and location
- Existing improvements
- Development potential indicators

### 3. AI Agent Integration

The AI agent:
- Orchestrates both tools to gather comprehensive information
- Analyzes development potential using multiple data sources
- Calculates financial metrics (ROI, estimated profit)
- Provides natural language recommendations
- Answers questions about specific sites or suburbs

### 4. Alert System

The alert system:
- Continuously monitors for new listings
- Filters based on your criteria
- Calculates development metrics automatically
- Sends alerts only for new matches
- Maintains history to avoid duplicate alerts

## Development Metrics Calculated

For each property, the system estimates:

- **Price per sqm**: Land cost efficiency
- **Estimated dwellings**: Based on zoning and land area
- **Potential gross value**: Estimated total sale value
- **Construction costs**: Rough construction estimate
- **Estimated profit**: Potential profit after costs
- **ROI percentage**: Return on investment

**Important**: These are simplified estimates. Always conduct proper due diligence with:
- Professional quantity surveyors
- Town planners
- Real estate valuers
- Financial advisors

## Data Sources

### Current Implementation (Demo)

The current implementation uses **simulated data** for demonstration purposes:
- Sample Brisbane suburbs and zones
- Representative property listings
- Realistic development scenarios

### Production Implementation (Future)

For production use, integrate with:

**Planning & Zoning Data**:
- Brisbane City Council Planning Scheme API
- Queensland Government Open Data Portal
- Planning alerts and DA tracker

**Property Listings**:
- Domain.com.au API
- REA (realestate.com.au) API
- CoreLogic API
- Private real estate agent feeds

## Customization

### Adding New Suburbs

Edit `alert_config.json`:

```json
{
  "search_criteria": {
    "suburbs": [
      "Your Suburb 1",
      "Your Suburb 2"
    ]
  }
}
```

### Adjusting ROI Thresholds

Edit `alert_config.json`:

```json
{
  "alert_preferences": {
    "min_roi_percentage": 25,
    "min_estimated_dwellings": 8
  }
}
```

### Adding New Tools

To extend the agent with additional tools:

1. Create a new tool in `tools/`
2. Add plugin class in `agent.py`
3. Register with `@kernel_function` decorator

Example:

```python
class MarketDataPlugin:
    @kernel_function(
        name="get_market_trends",
        description="Get market trends for Brisbane suburbs"
    )
    def get_market_trends(self, suburb: str) -> str:
        # Implementation
        pass
```

## Project Structure

```
brisbane-dev-site-finder/
├── agent.py                    # Main AI agent application
├── alert_system.py             # Alert monitoring system
├── alert_config.json           # Alert configuration
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── README.md                  # This file
├── tools/
│   ├── planning_zoning_tool.py    # Planning & zoning search
│   └── property_listing_tool.py    # Property listing search
└── data/
    └── alert_history.json         # Alert history (auto-generated)
```

## Example Use Cases

### Use Case 1: Finding Apartment Development Sites

```bash
python agent.py
```

Chat: "Find me sites in South Brisbane suitable for apartment buildings with at least 1000 sqm land area and under $4M"

### Use Case 2: Automated Monitoring

```bash
python alert_system.py --mode monitor
```

The system will continuously monitor and alert you when new suitable properties are listed.

### Use Case 3: Analyzing a Specific Property

```bash
python agent.py
```

Chat: "Analyze the development potential of 123 Brunswick Street, Fortitude Valley"

## Troubleshooting

### API Key Errors

```
❌ Error: API key not provided
```

**Solution**: Ensure your `.env` file has the correct API key:
```bash
OPENAI_API_KEY=sk-...
```

### Import Errors

```
ModuleNotFoundError: No module named 'semantic_kernel'
```

**Solution**: Install dependencies:
```bash
pip install -r requirements.txt
```

### Email Alerts Not Working

**Solution**:
1. Check SMTP credentials in `.env`
2. For Gmail, use an App Password
3. Ensure firewall allows SMTP connections

## Best Practices

1. **Due Diligence**: Always verify information with official sources
2. **Professional Advice**: Consult professionals before making investment decisions
3. **Regular Updates**: Keep criteria updated based on market conditions
4. **API Limits**: Be mindful of API rate limits and costs
5. **Data Privacy**: Keep your API keys and credentials secure

## Contributing

This project is part of the [AI Agents for Beginners](https://github.com/microsoft/ai-agents-for-beginners) curriculum. Contributions are welcome!

To contribute:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project follows the license of the parent repository (MIT License).

## Disclaimer

This tool is for **informational and educational purposes only**. Development metrics and analyses are estimates and should not be considered professional advice. Always:

- Conduct proper due diligence
- Consult with qualified professionals
- Verify all information with official sources
- Understand local regulations and requirements
- Assess risks appropriately

The creators and contributors are not responsible for any investment decisions made based on information provided by this tool.

## Resources

- [Brisbane City Council Planning Scheme](https://www.brisbane.qld.gov.au/planning-and-building)
- [Queensland Government Open Data](https://www.data.qld.gov.au/)
- [Semantic Kernel Documentation](https://learn.microsoft.com/en-us/semantic-kernel/)
- [AI Agents for Beginners Course](https://github.com/microsoft/ai-agents-for-beginners)

## Support

For issues or questions:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review the parent course materials
3. Open an issue in the repository

---

**Built with ❤️ using Microsoft Semantic Kernel and AI Agents**
