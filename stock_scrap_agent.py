from phi.agent import Agent
from phi.tools.crawl4ai_tools import Crawl4aiTools
from phi.model.groq import Groq
import json
from prettytable import PrettyTable  # For neat CLI output
from phi.tools.yfinance import YFinanceTools

# Updated Agent Setup: stricter instructions for a precise JSON response
indian_stock_agent = Agent(
    role="You are an Indian Stock Market Data Scraping Specialist",
    model=Groq(id="llama-3.3-70b-versatile", api_key="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"),
    tools=[Crawl4aiTools(), YFinanceTools()],
    description="An AI-powered agent designed to scrape real-time stock market data from NSE India, BSE India, Moneycontrol, and Economic Times.",
    instructions=(
        "Scrape Indian stock market data from NSE India, BSE India, Moneycontrol, and Economic Times. "
        "Return a JSON object with exactly these fields: "
        "'Stock Symbol' (string), 'Company Name' (string), 'Current Price' (number), "
        "'Market Cap' (string or number), 'P/E Ratio' (number), '52-Week High' (number), "
        "'52-Week Low' (number), 'Volume' (number or string), and "
        "'Recent News' (a list of objects, each with keys 'title', 'source', and 'url'). "
        "Do not include any additional commentary or keys."
    ),
    markdown=True,
    show_tool_calls=True
)

def scrape_stock_data(stock_symbol):
    """Scrapes stock market data for a given stock symbol from Indian sources."""
    try:
        # Automatically append ".NS" if no exchange suffix is provided.
        if not (stock_symbol.endswith('.NS') or stock_symbol.endswith('.BO')):
            stock_symbol_query = stock_symbol + '.NS'
        else:
            stock_symbol_query = stock_symbol

        query = (
            f"Scrape real-time stock data for {stock_symbol_query} from NSE India, BSE India, Moneycontrol, "
            "and Economic Times. Return the result as a JSON object with the following keys: "
            "'Stock Symbol', 'Company Name', 'Current Price', 'Market Cap', 'P/E Ratio', "
            "'52-Week High', '52-Week Low', 'Volume', and 'Recent News'. "
            "The 'Recent News' key should be a list of objects with 'title', 'source', and 'url'. "
            "Do not include any extra commentary."
        )

        response = indian_stock_agent.run(query)

        # Extract and parse JSON content
        json_string = response.content  
        if isinstance(json_string, str):
            data = json.loads(json_string)
            return data
        else:
            print(f"Unexpected response type: {type(json_string)}")
            return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}. Response content: {json_string}")
        return None
    except Exception as e:
        print(f"Scraping error: {e}")
        return None

def display_stock_data(data):
    """Displays stock data in a well-formatted table."""
    if not data:
        print("No data available.")
        return

    table = PrettyTable()
    table.field_names = [
        "Stock Symbol", "Company Name", "Current Price (INR)",
        "Market Cap", "P/E Ratio", "52-Week High", "52-Week Low", "Volume"
    ]

    table.add_row([
        data.get("Stock Symbol", "N/A"),
        data.get("Company Name", "N/A"),
        f"₹{data.get('Current Price', 'N/A')}",
        data.get("Market Cap", "N/A"),
        data.get("P/E Ratio", "N/A"),
        f"₹{data.get('52-Week High', 'N/A')}",
        f"₹{data.get('52-Week Low', 'N/A')}",
        data.get("Volume", "N/A"),
    ])

    print("\n📊 Indian Stock Market Data 📊\n")
    print(table)

    if "Recent News" in data and isinstance(data["Recent News"], list):
        print("\n📰 Latest Financial News 📰\n")
        for i, news in enumerate(data["Recent News"][:5], 1):
            print(f"{i}. {news.get('title', 'N/A')} - {news.get('source', 'N/A')}")
            print(f"   {news.get('url', '#')}\n")

def store_data(data, stock_symbol):
    """Stores stock data in a markdown file for better readability."""
    if not data:
        print("No data to store.")
        return

    try:
        filename = f"{stock_symbol}_stock_report.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"# 📈 Indian Stock Market Report for {stock_symbol}\n\n")
            f.write(f"**Company Name:** {data.get('Company Name', 'N/A')}\n\n")
            f.write(f"**Current Price:** ₹{data.get('Current Price', 'N/A')}\n")
            f.write(f"**Market Cap:** {data.get('Market Cap', 'N/A')}\n")
            f.write(f"**P/E Ratio:** {data.get('P/E Ratio', 'N/A')}\n")
            f.write(f"**52-Week High:** ₹{data.get('52-Week High', 'N/A')}\n")
            f.write(f"**52-Week Low:** ₹{data.get('52-Week Low', 'N/A')}\n")
            f.write(f"**Volume:** {data.get('Volume', 'N/A')}\n\n")

            if "Recent News" in data and isinstance(data["Recent News"], list):
                f.write("## 📰 Latest Financial News\n\n")
                for i, news in enumerate(data["Recent News"][:5], 1):
                    f.write(f"{i}. **{news.get('title', 'N/A')}** - {news.get('source', 'N/A')}\n")
                    f.write(f"   [Read more]({news.get('url', '#' )})\n\n")

        print(f"\n📄 Stock report saved as: {filename}")
    except Exception as e:
        print(f"Error storing data: {e}")

# --- Main Execution ---
stock_symbol = input("Enter the Indian stock symbol (e.g., RELIANCE, TCS, INFY): ").strip().upper()

if stock_symbol:
    stock_data = scrape_stock_data(stock_symbol)
    if stock_data:
        display_stock_data(stock_data)
        store_data(stock_data, stock_symbol)
else:
    print("No stock symbol provided. Exiting.")
