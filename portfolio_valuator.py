import json
import os

def get_ticker_from_json(amfi_code: str, json_path: str = "ticker_map.json") -> str:
    """
    Reads the local JSON registry to instantly translate a 6-digit AMFI 
    scheme code to its corresponding Yahoo Finance ticker symbol.
    """
    # 1. Active File Guardrail
    if not os.path.exists(json_path):
        print(f"❌ Error: Registry file '{json_path}' could not be located.")
        return None

    try:
        # 2. Extract Data Matrix
        with open(json_path, "r") as file:
            ticker_map = json.load(file)
        
        # 3. Secure the Match
        # (Casting to string ensures it matches the JSON key format perfectly)
        yahoo_ticker = ticker_map.get(str(amfi_code))
        
        if not yahoo_ticker:
            print(f"⚠️ Warning: AMFI Code '{amfi_code}' is missing from the registry mapping.")
            return None
            
        return yahoo_ticker

    # 4. Technical Exception Catching
    except json.JSONDecodeError:
        print(f"❌ Error: '{json_path}' is corrupted or improperly formatted.")
        return None
    except Exception as e:
        print(f"❌ Unexpected lookup failure: {e}")
        return None


# 🛡️ THE SCRIPT GUARD BLOCK
if __name__ == "__main__":
    print("=" * 60)
    print("🧪 RUNNING ISOLATED TICKER LOOKUP FUNCTION DIAGNOSTIC TEST")
    print("=" * 60)
    
    # Test case 1: Validate a known working asset in your JSON (HDFC Mid-Cap)
    test_code_1 = "118989"
    result_1 = get_ticker_from_json(test_code_1)
    print(f"🔹 Test 1 (Valid Code): AMFI {test_code_1} ──► Yahoo Ticker: {result_1}")
    
    print("-" * 60)
    
    # Test case 2: Validate how it gracefully handles an unmapped or invalid code
    test_code_2 = "999999"
    result_2 = get_ticker_from_json(test_code_2)
    print(f"🔹 Test 2 (Invalid Code): AMFI {test_code_2} ──► Result: {result_2}")
    
    print("=" * 60)