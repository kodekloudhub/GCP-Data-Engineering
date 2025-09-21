#!/usr/bin/env python3
"""
Simple Japanese Gaming Company Transaction Data Generator (No Dependencies)

This script generates 500 realistic transaction records for a Japanese gaming company
without requiring any external dependencies beyond the Python standard library.

Dataset: gaming_transactions
Table: item_transactions
"""

import random
import csv
from datetime import datetime, timedelta

# Set random seed for reproducible results
random.seed(42)

# Gaming-specific data
ITEM_TYPES = [
    'weapon', 'character', 'currency', 'skin', 'boost', 'subscription',
    'bundle', 'consumable', 'equipment', 'accessory'
]

ITEM_NAMES = {
    'weapon': [
        '雷神の剣', '氷の弓', '炎の杖', '風の槍', '闇の短剣',
        '光の大剣', '雷の斧', '氷の魔法書', '炎の盾', '風の投げナイフ'
    ],
    'character': [
        '桜の戦士', '龍の騎士', '魔法使いユキ', '忍者ハヤテ', 'サムライ雷',
        '陰陽師アキラ', '侍カズキ', '忍者シズカ', '戦士タケシ', '魔女ミサキ'
    ],
    'currency': [
        'ゴールド', 'ジェム', 'コイン', 'ポイント', 'トークン'
    ],
    'skin': [
        '桜の衣装', '龍の鎧', '魔法のローブ', '忍者の装束', '侍の着物',
        '陰陽師の道着', '戦士の甲冑', '魔女の帽子', '騎士の兜', '盗賊のマスク'
    ],
    'boost': [
        '経験値ブースト', '攻撃力アップ', '防御力アップ', '速度ブースト', '幸運の護符',
        '魔力回復', '体力回復', 'クリティカル率アップ', 'ドロップ率アップ', 'スキルポイント'
    ],
    'subscription': [
        'プレミアム会員', 'VIP会員', 'プロ会員', 'エリート会員'
    ],
    'bundle': [
        '初心者パック', '戦士セット', '魔法使いセット', '忍者セット', '侍セット',
        '限定コレクション', '特別パック', 'お得セット', '豪華パック', '究極セット'
    ],
    'consumable': [
        '回復ポーション', '魔力ポーション', '体力ポーション', '解毒剤', '復活の石',
        'テレポート巻物', '経験値の書', 'スキルブック', '強化石', '修理キット'
    ],
    'equipment': [
        '勇者の剣', '賢者の杖', '盗賊の短剣', '戦士の盾', '魔法使いの帽子',
        '忍者の手裏剣', '侍の刀', '陰陽師の扇', '騎士の槍', '魔女のほうき'
    ],
    'accessory': [
        '力の指輪', '知恵の首飾り', '速度のブーツ', '防御の腕輪', '魔力の耳飾り',
        '幸運のペンダント', '勇気のバッジ', '知恵の眼鏡', '速度の靴', '防御のベルト'
    ]
}

USER_TIERS = ['free', 'premium', 'vip', 'elite']
REGIONS = ['Tokyo', 'Osaka', 'Kyoto', 'Yokohama', 'Nagoya', 'Sapporo', 'Fukuoka']
PLATFORMS = ['mobile', 'console', 'pc']

def generate_transaction_data(num_records=500):
    """Generate transaction data for Japanese gaming company"""
    
    transactions = []
    
    for i in range(num_records):
        # Generate transaction timestamp (last 6 months)
        start_date = datetime.now() - timedelta(days=180)
        end_date = datetime.now()
        days_diff = (end_date - start_date).days
        random_days = random.randint(0, days_diff)
        transaction_time = start_date + timedelta(days=random_days)
        
        # Select item type and corresponding name
        item_type = random.choice(ITEM_TYPES)
        item_name = random.choice(ITEM_NAMES[item_type])
        
        # Generate user ID (mix of new and returning users)
        user_id = f"user_{random.randint(1000, 9999)}"
        
        # Generate amount based on item type
        if item_type == 'currency':
            amount = random.randint(100, 10000)  # 100-10,000 JPY
        elif item_type == 'subscription':
            amount = random.choice([980, 1980, 2980, 4980])  # Common subscription prices
        elif item_type == 'bundle':
            amount = random.randint(5000, 50000)  # 5,000-50,000 JPY
        else:
            amount = random.randint(100, 5000)  # 100-5,000 JPY
        
        # Add some premium pricing for certain items
        if random.random() < 0.1:  # 10% chance of premium pricing
            amount = int(amount * random.uniform(1.5, 3.0))
        
        # Generate user tier (weighted towards free users)
        user_tier_weights = [0.6, 0.25, 0.1, 0.05]  # free, premium, vip, elite
        user_tier = random.choices(USER_TIERS, weights=user_tier_weights)[0]
        
        # Generate region
        region = random.choice(REGIONS)
        
        # Generate platform
        platform = random.choice(PLATFORMS)
        
        # Create transaction record
        transaction = {
            'transaction_id': f"TXN_{i+1:06d}",
            'user_id': user_id,
            'item_name': item_name,
            'item_type': item_type,
            'amount_jpy': amount,
            'transaction_timestamp': transaction_time.isoformat(),
            'user_tier': user_tier,
            'region': region,
            'platform': platform
        }
        
        transactions.append(transaction)
    
    return transactions

def main():
    """Main function to generate and save transaction data"""
    print("🎮 Generating Japanese Gaming Company Transaction Data...")
    
    # Generate transaction data
    transactions = generate_transaction_data(500)
    
    # Save to CSV
    csv_filename = 'gaming_transactions.csv'
    fieldnames = ['transaction_id', 'user_id', 'item_name', 'item_type', 
                  'amount_jpy', 'transaction_timestamp', 'user_tier', 'region', 'platform']
    
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(transactions)
    
    print(f"✅ Data saved to {csv_filename}")
    
    # Display sample data
    print("\n📊 Sample Data:")
    for i, transaction in enumerate(transactions[:5]):
        print(f"Transaction {i+1}: {transaction}")
    
    # Display data summary
    total_amount = sum(t['amount_jpy'] for t in transactions)
    avg_amount = total_amount / len(transactions)
    
    print(f"\n📈 Data Summary:")
    print(f"Total transactions: {len(transactions)}")
    print(f"Total revenue: {total_amount:,} JPY")
    print(f"Average transaction: {avg_amount:.0f} JPY")
    
    # Count by item type
    item_type_counts = {}
    for transaction in transactions:
        item_type = transaction['item_type']
        item_type_counts[item_type] = item_type_counts.get(item_type, 0) + 1
    
    print(f"\n🎯 Item Type Distribution:")
    for item_type, count in sorted(item_type_counts.items()):
        print(f"{item_type}: {count}")
    
    # Count by user tier
    user_tier_counts = {}
    for transaction in transactions:
        user_tier = transaction['user_tier']
        user_tier_counts[user_tier] = user_tier_counts.get(user_tier, 0) + 1
    
    print(f"\n👥 User Tier Distribution:")
    for user_tier, count in sorted(user_tier_counts.items()):
        print(f"{user_tier}: {count}")
    
    print(f"\n📋 Next Steps:")
    print(f"1. Upload {csv_filename} to BigQuery using the UI")
    print(f"2. Dataset: gaming_transactions")
    print(f"3. Table: item_transactions")

if __name__ == "__main__":
    main()
