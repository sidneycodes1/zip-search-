import asyncio
from app.services.aggregator.search_aggregator import SearchAggregator

async def main():
    agg = SearchAggregator()
    print("--- First Search ---")
    results1 = await agg.search(
        name="Elon Musk",
        description="CEO Tesla SpaceX"
    )
    print(f"Total results: {len(results1)}")

    print("\n--- Second Search ---")
    results2 = await agg.search(
        name="Elon Musk",
        description="CEO Tesla SpaceX"
    )
    print(f"Total results: {len(results2)}")

if __name__ == "__main__":
    asyncio.run(main())
