"""
Main script to fetch and display AMFI Mutual Fund NAV data
"""

from amfi_nav_fetcher import get_nav_data, print_results


def main():
    """Main execution function"""
    
    # Define the fund IDs to retrieve
    fund_ids = {118955, 118989, 122639, 147946, 119783}
    
    print("\n" + "="*80)
    print("AMFI Mutual Fund NAV Data Retrieval".center(80))
    print("="*80 + "\n")
    
    # Fetch NAV data
    nav_results = get_nav_data(fund_ids)
    
    # Print results
    if nav_results:
        print_results(nav_results, "Retrieved Fund Data")
        
        # Print additional info
        print(f"Total funds retrieved: {len(nav_results)}\n")
        
        # Print each record in detail
        print("Detailed Records:")
        print("-" * 80)
        for idx, record in enumerate(nav_results, 1):
            fund_id, fund_name, nav_date, nav_value = record
            print(f"\n{idx}. Fund ID: {fund_id}")
            print(f"   Name: {fund_name}")
            print(f"   NAV Date: {nav_date}")
            print(f"   NAV Value: ₹{nav_value}")
        
        print("\n" + "-" * 80)
        print(f"\n✅ Successfully retrieved NAV data for {len(nav_results)} fund(s)")
    else:
        print("❌ No data found for the requested fund IDs\n")


if __name__ == "__main__":
    main()
