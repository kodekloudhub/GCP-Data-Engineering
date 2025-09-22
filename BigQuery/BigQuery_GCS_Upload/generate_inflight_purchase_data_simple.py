#!/usr/bin/env python3
"""
Simple Passenger Inflight Purchase Data Generator (No Dependencies)

This script generates nested JSON files containing passenger inflight purchase information
for the year 2025 using only Python standard library.

Dataset: airline_purchases
Table: inflight_purchases
"""

import json
import random
from datetime import datetime, timedelta

# Set random seed for reproducible results
random.seed(42)

# Airline and flight data
AIRLINES = [
    "Japan Airlines", "ANA", "United Airlines", "Delta Air Lines", 
    "American Airlines", "Lufthansa", "British Airways", "Air France",
    "Singapore Airlines", "Cathay Pacific", "Qantas", "Emirates"
]

AIRPORTS = [
    "NRT", "HND", "LAX", "JFK", "LHR", "CDG", "FRA", "SIN", 
    "HKG", "SYD", "DXB", "ICN", "BKK", "SFO", "ORD", "DFW"
]

CABIN_CLASSES = ["Economy", "Premium Economy", "Business", "First"]
LOYALTY_TIERS = ["Bronze", "Silver", "Gold", "Platinum", "Diamond"]

PURCHASE_CATEGORIES = [
    "Food & Beverage", "Duty Free", "Entertainment", "WiFi", 
    "Seat Upgrade", "Extra Baggage", "Travel Insurance", "Gift Items"
]

PAYMENT_METHODS = ["Credit Card", "Debit Card", "Mobile Payment", "Miles", "Cash"]

def generate_flight_info():
    """Generate flight information"""
    departure_date = datetime(2025, random.randint(1, 12), random.randint(1, 28))
    flight_duration = random.randint(2, 15)  # hours
    arrival_date = departure_date + timedelta(hours=flight_duration)
    
    return {
        "airline": random.choice(AIRLINES),
        "flight_number": f"{random.randint(100, 9999)}",
        "departure_airport": random.choice(AIRPORTS),
        "arrival_airport": random.choice(AIRPORTS),
        "departure_date": departure_date.isoformat(),
        "arrival_date": arrival_date.isoformat(),
        "cabin_class": random.choice(CABIN_CLASSES),
        "seat_number": f"{random.randint(1, 50)}{random.choice(['A', 'B', 'C', 'D', 'E', 'F'])}",
        "flight_duration_hours": flight_duration
    }

def generate_purchase_history():
    """Generate purchase history for the flight"""
    num_purchases = random.randint(1, 8)
    purchases = []
    
    for _ in range(num_purchases):
        purchase_time = datetime(2025, random.randint(1, 12), random.randint(1, 28), 
                               random.randint(6, 23), random.randint(0, 59))
        
        category = random.choice(PURCHASE_CATEGORIES)
        base_price = random.randint(5, 200)
        
        # Adjust pricing based on category
        if category == "Duty Free":
            base_price = random.randint(50, 500)
        elif category == "Seat Upgrade":
            base_price = random.randint(100, 1000)
        elif category == "Extra Baggage":
            base_price = random.randint(30, 150)
        
        purchase = {
            "purchase_id": f"PUR_{random.randint(100000, 999999)}",
            "category": category,
            "item_name": f"{category} Item {random.randint(1, 100)}",
            "quantity": random.randint(1, 3),
            "unit_price": base_price,
            "total_price": base_price * random.randint(1, 3),
            "purchase_time": purchase_time.isoformat(),
            "currency": "USD",
            "discount_applied": random.choice([True, False]),
            "discount_amount": random.randint(0, 20) if random.choice([True, False]) else 0
        }
        purchases.append(purchase)
    
    return purchases

def generate_personal_info():
    """Generate passenger personal information"""
    first_names = ["Yuki", "Hiroshi", "Sakura", "Takeshi", "Aiko", "Kenji", 
                   "Maya", "Ryo", "Emi", "Kenta", "Naomi", "Daiki"]
    last_names = ["Tanaka", "Sato", "Suzuki", "Takahashi", "Watanabe", 
                  "Ito", "Yamamoto", "Nakamura", "Kobayashi", "Kato"]
    
    return {
        "first_name": random.choice(first_names),
        "last_name": random.choice(last_names),
        "age": random.randint(18, 80),
        "nationality": random.choice(["Japanese", "American", "British", "German", "French", "Australian"]),
        "gender": random.choice(["Male", "Female", "Other"]),
        "email": f"passenger{random.randint(1000, 9999)}@email.com",
        "phone": f"+1-{random.randint(100, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
        "passport_number": f"{random.choice(['A', 'B', 'C'])}{random.randint(100000, 999999)}"
    }

def generate_loyalty_status():
    """Generate loyalty program information"""
    tier = random.choice(LOYALTY_TIERS)
    base_miles = {"Bronze": 1000, "Silver": 5000, "Gold": 15000, "Platinum": 50000, "Diamond": 100000}
    
    return {
        "program_name": random.choice(["Mileage Plus", "AAdvantage", "SkyMiles", "Executive Club", "Miles & More"]),
        "member_id": f"FF{random.randint(100000, 999999)}",
        "tier": tier,
        "miles_balance": base_miles[tier] + random.randint(0, 50000),
        "status_since": f"202{random.randint(0, 5)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
        "lifetime_miles": base_miles[tier] * random.randint(2, 10),
        "next_tier_miles_needed": random.randint(1000, 25000) if tier != "Diamond" else 0
    }

def generate_payment_methods():
    """Generate payment methods"""
    num_methods = random.randint(1, 3)
    methods = []
    
    for _ in range(num_methods):
        method_type = random.choice(PAYMENT_METHODS)
        method = {
            "method_type": method_type,
            "card_number": f"****-****-****-{random.randint(1000, 9999)}" if "Card" in method_type else None,
            "expiry_date": f"202{random.randint(6, 9)}-{random.randint(1, 12):02d}" if "Card" in method_type else None,
            "is_primary": len(methods) == 0,
            "miles_earned": random.randint(0, 1000) if method_type == "Credit Card" else 0
        }
        methods.append(method)
    
    return methods

def generate_preferences():
    """Generate passenger preferences"""
    return {
        "dietary_restrictions": random.choice(["None", "Vegetarian", "Vegan", "Gluten-Free", "Halal", "Kosher"]),
        "seat_preference": random.choice(["Window", "Aisle", "Middle", "No Preference"]),
        "meal_preference": random.choice(["Regular", "Vegetarian", "Vegan", "Asian", "Western", "No Meal"]),
        "entertainment_preference": random.choice(["Movies", "TV Shows", "Music", "Games", "Books", "Sleep"]),
        "language_preference": random.choice(["English", "Japanese", "Spanish", "French", "German", "Chinese"]),
        "newsletter_subscription": random.choice([True, False]),
        "special_assistance": random.choice(["None", "Wheelchair", "Extra Legroom", "Priority Boarding"])
    }

def generate_metadata():
    """Generate metadata about the record"""
    return {
        "record_id": f"REC_{random.randint(100000, 999999)}",
        "created_at": datetime.now().isoformat(),
        "data_source": "Inflight Purchase System",
        "version": "1.0",
        "processing_status": "Completed",
        "quality_score": round(random.uniform(0.8, 1.0), 2),
        "last_updated": datetime.now().isoformat()
    }

def generate_passenger_record():
    """Generate a complete passenger inflight purchase record"""
    return {
        "passenger_id": f"PASS_{random.randint(100000, 999999)}",
        "flight_info": generate_flight_info(),
        "purchase_history": generate_purchase_history(),
        "personal_info": generate_personal_info(),
        "loyalty_status": generate_loyalty_status(),
        "payment_methods": generate_payment_methods(),
        "preferences": generate_preferences(),
        "metadata": generate_metadata()
    }

def main():
    """Main function to generate and save JSON data"""
    print("✈️ Generating Passenger Inflight Purchase Data for 2025...")
    
    # Generate data for two files
    file1_records = []
    file2_records = []
    
    # Generate 250 records for each file
    for i in range(250):
        file1_records.append(generate_passenger_record())
        file2_records.append(generate_passenger_record())
    
    # Save first JSON file
    file1_name = 'inflight_purchases_batch1.json'
    with open(file1_name, 'w', encoding='utf-8') as f:
        json.dump(file1_records, f, indent=2, ensure_ascii=False)
    print(f"✅ Data saved to {file1_name}")
    
    # Save second JSON file
    file2_name = 'inflight_purchases_batch2.json'
    with open(file2_name, 'w', encoding='utf-8') as f:
        json.dump(file2_records, f, indent=2, ensure_ascii=False)
    print(f"✅ Data saved to {file2_name}")
    
    # Display sample data
    print("\n📊 Sample Record Structure:")
    sample_record = file1_records[0]
    print(json.dumps(sample_record, indent=2, ensure_ascii=False)[:1000] + "...")
    
    # Display data summary
    total_records = len(file1_records) + len(file2_records)
    total_purchases = sum(len(record['purchase_history']) for record in file1_records + file2_records)
    total_revenue = sum(
        sum(purchase['total_price'] for purchase in record['purchase_history']) 
        for record in file1_records + file2_records
    )
    
    print(f"\n📈 Data Summary:")
    print(f"Total passenger records: {total_records}")
    print(f"Total purchases: {total_purchases}")
    print(f"Total revenue: ${total_revenue:,}")
    print(f"Average purchases per passenger: {total_purchases/total_records:.1f}")
    print(f"Average revenue per passenger: ${total_revenue/total_records:.2f}")
    
    print(f"\n📋 Next Steps:")
    print(f"1. Upload {file1_name} and {file2_name} to your GCS bucket")
    print(f"2. Create dataset: airline_purchases")
    print(f"3. Create table: inflight_purchases")
    print(f"4. Load data from GCS to BigQuery")
    print(f"5. Practice BigQuery JSON functions with nested data")

if __name__ == "__main__":
    main()
