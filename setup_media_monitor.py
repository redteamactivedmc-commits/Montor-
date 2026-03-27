import anthropic
import os

client = anthropic.Anthropic(
    # defaults to os.environ.get("ANTHROPIC_API_KEY")
    api_key=os.environ.get("ANTHROPIC_API_KEY"),
)

message = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=20000,
    system="Please write a Claude code that automates the monitoring of media coverage for the announcement by Denodo and Snowflake (link: https://www.denodo.com/en/press-release/2026-03-24/denodo-joins-snowflake-and-industry-leaders-advance-data-and-ai-interoperability-through-open), focusing specifically on the Middle East region. The script should include the following features:  1. Monitoring Tools:      - Retrieve data from Google search and support manual scan inputs.  2. Data to Track:      - Publication source      - Article link      - Publication date      - Market (region or country)      - Tier or classification of the outlet      - Message pull-through (key message coverage)      - UMV (Unique Monthly Visitors) or impressions metrics  3. Reporting Types:      - Generate a 24-hour coverage update report      - Optionally generate weekly summary reports      - Generate monthly detailed campaign reports  4. Reporting Standards:      - Ensure accuracy of the collected data      - Check for completeness of tracked fields      - Maintain visual consistency in the reports (format tables or charts clearly)  Please structure the code with modular functions for data collection, tracking, and reporting. Include comments to explain key parts and ensure that the solution can be run in a Python environment with commonly used libraries. Simulate or mock any API calls if necessary since some tools may require authentication or paid access. Aim for clean, maintainable code ready for practical use or further enhancement.Please write a claude code t that automates the monitoring of media coverage for the announcement by Denodo and Snowflake (link: https://www.denodo.com/en/press-release/2026-03-24/denodo-joins-snowflake-and-industry-leaders-advance-data-and-ai-interoperability-through-open), focusing specifically on the Middle East region. The script should include the following features:  1. Monitoring Tools:      - Retrieve data from Google search and support manual scan inputs.  2. Data to Track:      - Publication source      - Article link      - Publication date      - Market (region or country)      - Tier or classification of the outlet      - Message pull-through (key message coverage)      - UMV (Unique Monthly Visitors) or impressions metrics  3. Reporting Types:      - Generate a 24-hour coverage update report      - Optionally generate weekly summary reports      - Generate monthly detailed campaign reports  4. Reporting Standards:      - Ensure accuracy of the collected data      - Check for completeness of tracked fields      - Maintain visual consistency in the reports (format tables or charts clearly)  Please structure the code with modular functions for data collection, tracking, and reporting. Include comments to explain key parts and ensure that the solution can be run in a Python environment with commonly used libraries. Simulate or mock any API calls if necessary since some tools may require authentication or paid access. Aim for clean, maintainable code ready for practical use or further enhancement.",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "media-monitor/\n├── media_monitor/\n│   ├── __init__.py\n│   ├── data_collection.py      # Data fetching, manual scan processing\n│   ├── validation.py           # Field and record validations\n│   ├── reporting.py            # Summary tables, charts, reports\n│   ├── utils.py                # Common utilities\n│   └── cli.py                  # Argument parsing, main()\n├── tests/\n│   ├── __init__.py\n│   └── test_utils.py\n├── requirements.txt\n├── sample_manual_scan.csv\n└── README.md"
                }
            ]
        }
    ],
    thinking={
        "type": "enabled",
        "budget_tokens": 16000
    }
)

print(message.content)
