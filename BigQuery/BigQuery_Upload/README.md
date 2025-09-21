# BigQuery Data Upload

This folder contains a script to generate Japanese gaming company transaction data for BigQuery practice.

## Dataset and Table Information

- **Dataset Name**: `gaming_transactions`
- **Table Name**: `item_transactions`

## Setup Instructions

### 1. Virtual Environment Setup

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows

# Upgrade pip and install wheel
pip install --upgrade pip wheel

# Install dependencies (using pre-compiled wheels)
pip install --only-binary=all -r requirements.txt

# If the above fails, try installing without binary dependencies:
# pip install --no-binary=pandas -r requirements.txt
```

### 2. Run the Data Generation Script

**Option A: With Dependencies (if installation works)**
```bash
python generate_transaction_data.py
```

**Option B: No Dependencies (recommended if you have issues)**
```bash
python generate_transaction_data_simple.py
```

Both scripts will generate a `gaming_transactions.csv` file with 500 transaction records.

## Data Fields

- `transaction_id`: Unique transaction identifier
- `user_id`: User identifier
- `item_name`: Name of the purchased item (Japanese names)
- `item_type`: Category of item (weapon, character, currency, etc.)
- `amount_jpy`: Transaction amount in Japanese Yen
- `transaction_timestamp`: When the transaction occurred
- `user_tier`: User subscription tier (free, premium, vip, elite)
- `region`: User's region (Japanese cities)
- `platform`: Gaming platform (mobile, console, PC)

## Next Steps

1. Upload the generated CSV to BigQuery using the UI
2. Create dataset: `gaming_transactions`
3. Create table: `item_transactions`
4. Practice BigQuery queries with the data
