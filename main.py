import aiohttp
import asyncio
import argparse
from datetime import datetime, timedelta


class PrivatBankAPI:
    API_URL = "https://api.privatbank.ua/p24api/exchange_rates?json&date="

    async def fetch_currency_rates(self, date):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.API_URL}{date}") as response:
                data = await response.json()
                return data["exchangeRate"] if "exchangeRate" in data else []

    async def get_currency_rates(self, days):
        today = datetime.now()
        rates = []

        for i in range(days):
            current_date = today - timedelta(days=i)
            formatted_date = current_date.strftime("%d.%m.%Y")

            rates_data = await self.fetch_currency_rates(formatted_date)

            if not rates_data:
                print(f"No data available for {formatted_date}")
                continue

            eur_rate = next(
                (item for item in rates_data if item["currency"] == "EUR"), None
            )
            usd_rate = next(
                (item for item in rates_data if item["currency"] == "USD"), None
            )

            if eur_rate and usd_rate:
                rates.append(
                    {
                        formatted_date: {
                            "EUR": {
                                "sale": eur_rate["saleRate"],
                                "purchase": eur_rate["purchaseRate"],
                            },
                            "USD": {
                                "sale": usd_rate["saleRate"],
                                "purchase": usd_rate["purchaseRate"],
                            },
                        }
                    }
                )

        return rates


async def main():
    parser = argparse.ArgumentParser(
        description="Get currency rates from PrivatBank API"
    )
    parser.add_argument(
        "days", type=int, help="Number of days to retrieve currency rates"
    )

    args = parser.parse_args()

    if args.days > 10:
        print("Error: You can only retrieve currency rates for the last 10 days.")
        return

    api = PrivatBankAPI()
    rates = await api.get_currency_rates(args.days)
    print(rates)
    input("Press Enter to exit...")


if __name__ == "__main__":
    asyncio.run(main())
