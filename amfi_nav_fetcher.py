"""
AMFI Mutual Fund NAV Data Fetcher
Fetches daily NAV data from AMFI and filters by fund IDs
"""

import requests
from typing import List, Set
from datetime import datetime, date, timedelta


def fetch_nav_data() -> str:
    """
    Fetch the latest NAV data from AMFI website

    Returns:
        str: Raw text content of NAV data (pipe-delimited format)

    Raises:
        requests.RequestException: If network request fails
    """
    url = "https://www.amfiindia.com/spages/NAVAll.txt"

    try:
        response = requests.get(url, timeout=10, allow_redirects=True)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching data from {url}: {e}")
        raise


def parse_nav_data(raw_text: str) -> List[List]:
    """
    Parse semicolon-delimited NAV data from AMFI

    Args:
        raw_text: Raw text content from AMFI file

    Returns:
        List[List]: Each row contains [ID, Name, Date, NAV_Value]
    """
    parsed_data = []
    lines = raw_text.strip().split("\n")

    header_skipped = False

    for line in lines:
        if not line.strip():
            continue

        if not header_skipped and "Scheme Code" in line:
            header_skipped = True
            continue

        if line.count(";") < 2:
            continue

        try:
            parts = line.split(";")
            if len(parts) < 6:
                continue

            fund_id = parts[0].strip()
            scheme_name = parts[3].strip()
            nav_value = parts[4].strip()
            nav_date = parts[5].strip()

            if not fund_id.isdigit():
                continue

            if not fund_id or not scheme_name or not nav_value or not nav_date:
                continue

            try:
                float(nav_value)
            except ValueError:
                continue

            parsed_data.append([fund_id, scheme_name, nav_date, nav_value])

        except Exception:
            continue

    return parsed_data


def filter_by_ids(all_navs: List[List], fund_ids: Set[int]) -> List[List]:
    """
    Filter NAV data by specific fund IDs

    Args:
        all_navs: List of all NAV records [ID, Name, Date, NAV]
        fund_ids: Set of fund IDs to filter

    Returns:
        List[List]: Filtered NAV records matching the fund IDs
    """
    fund_ids_str = {str(fid) for fid in fund_ids}
    filtered = []
    found_ids = set()

    for nav_record in all_navs:
        if nav_record[0] in fund_ids_str:
            filtered.append(nav_record)
            found_ids.add(nav_record[0])

    missing_ids = fund_ids_str - found_ids
    if missing_ids:
        print(f"Warning: The following IDs were not found: {', '.join(sorted(missing_ids))}")

    return filtered


def get_last_weekday(reference_date: date | None = None) -> date:
    """
    Return the most recent weekday before the reference date.

    For example:
    - Monday -> previous Friday
    - Tuesday-Friday -> previous day
    - Saturday/Sunday -> Friday
    """
    current_date = reference_date or date.today()
    last_weekday = current_date - timedelta(days=1)

    while last_weekday.weekday() >= 5:
        last_weekday -= timedelta(days=1)

    return last_weekday


def find_stale_funds(nav_data: List[List], reference_date: date | None = None) -> List[List]:
    """
    Return funds whose NAV date is older than the last weekday.
    """
    cutoff_date = get_last_weekday(reference_date)
    stale_funds = []

    for record in nav_data:
        _, _, nav_date, _ = record

        try:
            parsed_nav_date = datetime.strptime(nav_date, "%d-%b-%Y").date()
        except ValueError:
            continue

        if parsed_nav_date < cutoff_date:
            stale_funds.append(record)

    return stale_funds


def print_stale_fund_warning(nav_data: List[List], reference_date: date | None = None):
    """
    Print a warning message that lists funds with stale NAV dates.
    """
    cutoff_date = get_last_weekday(reference_date)
    stale_funds = find_stale_funds(nav_data, reference_date)

    if not stale_funds:
        return

    print("\n" + "!" * 80)
    print("WARNING: Some funds have stale NAV data".center(80))
    print("!" * 80)
    print(f"Last acceptable NAV date: {cutoff_date.strftime('%d-%b-%Y')}")
    print("The following funds have NAV dates older than that:")

    for fund_id, fund_name, nav_date, _ in stale_funds:
        print(f" - {fund_id} | {fund_name} | NAV date: {nav_date}")

    print("!" * 80 + "\n")


def get_nav_data(fund_ids: Set[int]) -> List[List]:
    """
    Main function: Fetch and filter NAV data for given fund IDs

    Args:
        fund_ids: Set of fund IDs to retrieve data for
                  Example: {118955, 118989, 122639}

    Returns:
        List[List]: List of [ID, Fund_Name, NAV_Date, NAV_Value] for matched funds
    """
    print("Fetching AMFI NAV data...")
    raw_data = fetch_nav_data()

    print("Parsing NAV data...")
    all_navs = parse_nav_data(raw_data)
    print(f"Total funds in AMFI database: {len(all_navs)}")

    print(f"Filtering for {len(fund_ids)} fund(s)...")
    filtered_navs = filter_by_ids(all_navs, fund_ids)
    print(f"Found {len(filtered_navs)} fund(s)")
    print_stale_fund_warning(filtered_navs)

    return filtered_navs


def print_results(nav_data: List[List], title: str = "AMFI NAV Data"):
    """
    Pretty print NAV data results

    Args:
        nav_data: List of [ID, Name, Date, NAV] records
        title: Title for the output table
    """
    print(f"\n{'=' * 80}")
    print(f"{title:^80}")
    print(f"{'=' * 80}")
    print(f"{'Fund ID':<12} {'Fund Name':<45} {'NAV Date':<12} {'NAV Value':<10}")
    print(f"{'-' * 80}")

    for record in nav_data:
        fund_id, fund_name, nav_date, nav_value = record
        fund_name_trunc = fund_name[:42] + "..." if len(fund_name) > 45 else fund_name
        print(f"{fund_id:<12} {fund_name_trunc:<45} {nav_date:<12} {nav_value:>10}")

    print(f"{'=' * 80}\n")


if __name__ == "__main__":
    FUND_IDS = {118955, 118989, 122639}

    print("AMFI Mutual Fund NAV Fetcher")
    print(f"Requested Fund IDs: {FUND_IDS}\n")

    try:
        nav_results = get_nav_data(FUND_IDS)

        if nav_results:
            print_results(nav_results)
            print("As Python List:")
            print(nav_results)
        else:
            print("No data found for the requested fund IDs")

    except Exception as e:
        print(f"Error: {e}")
