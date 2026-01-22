#!/usr/bin/env python3
"""
Test the fixed location extraction logic
"""

def extract_city(user_message: str) -> str:
    """Extract city from user message - India only (FIXED VERSION)"""
    message_lower = user_message.lower()
    
    # 🔧 COUNTRY-LEVEL QUERY HANDLING
    country_aliases = ['india', 'bharat', 'hindustan']
    if any(country in message_lower for country in country_aliases):
        # Check if it's a pure country query (no specific city mentioned)
        city_mentioned = any(city in message_lower for city in [
            'erode', 'salem', 'tiruchengode', 'thiruchengode', 'kerala', 
            'chennai', 'bangalore', 'bengaluru', 'mumbai', 'delhi', 
            'hyderabad', 'pune', 'coimbatore', 'madurai', 'trichy'
        ])
        
        if not city_mentioned:
            # Pure country query - use capital city
            return "New Delhi,IN"
    
    # Specific city detection
    if "erode" in message_lower:
        return "Erode,IN"
    elif "salem" in message_lower:
        return "Salem,IN"
    elif "tiruchengode" in message_lower or "thiruchengode" in message_lower:
        return "Tiruchengode,IN"
    elif "kerala" in message_lower:
        return "Kerala,IN"
    elif "chennai" in message_lower:
        return "Chennai,IN"
    elif "bangalore" in message_lower or "bengaluru" in message_lower:
        return "Bangalore,IN"
    elif "mumbai" in message_lower:
        return "Mumbai,IN"
    elif "delhi" in message_lower:
        return "Delhi,IN"
    elif "hyderabad" in message_lower:
        return "Hyderabad,IN"
    elif "pune" in message_lower:
        return "Pune,IN"
    elif "coimbatore" in message_lower:
        return "Coimbatore,IN"
    elif "madurai" in message_lower:
        return "Madurai,IN"
    elif "trichy" in message_lower or "tiruchirappalli" in message_lower:
        return "Tiruchirappalli,IN"
    else:
        return "Erode,IN"  # Default to Erode instead of "India"

def test_location_extraction():
    """Test cases for the fixed location extraction"""
    test_cases = [
        # Country-level queries (FIXED)
        ("weather in india", "New Delhi,IN"),
        ("india weather", "New Delhi,IN"),
        ("weather today in bharat", "New Delhi,IN"),
        ("hindustan weather", "New Delhi,IN"),
        
        # City-specific queries (should work as before)
        ("weather in erode", "Erode,IN"),
        ("salem weather", "Salem,IN"),
        ("weather in kerala", "Kerala,IN"),
        ("chennai weather today", "Chennai,IN"),
        ("weather in mumbai", "Mumbai,IN"),
        
        # Mixed queries (city mentioned with country)
        ("weather in chennai india", "Chennai,IN"),
        ("mumbai weather in india", "Mumbai,IN"),
        
        # Default fallback
        ("weather today", "Erode,IN"),
        ("what's the temperature", "Erode,IN"),
    ]
    
    print("🧪 Testing Location Extraction Logic")
    print("=" * 50)
    
    all_passed = True
    for query, expected in test_cases:
        result = extract_city(query)
        status = "✅ PASS" if result == expected else "❌ FAIL"
        print(f"{status} | '{query}' → {result}")
        
        if result != expected:
            print(f"     Expected: {expected}")
            all_passed = False
    
    print("=" * 50)
    if all_passed:
        print("🎉 ALL TESTS PASSED! Location extraction logic is fixed.")
    else:
        print("⚠️ Some tests failed. Check the logic above.")
    
    return all_passed

if __name__ == "__main__":
    test_location_extraction()