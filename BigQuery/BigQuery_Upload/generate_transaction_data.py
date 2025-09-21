#!/usr/bin/env python3
"""
Japanese Gaming Company Transaction Data Generator

This script generates 500 realistic transaction records for a Japanese gaming company,
including various item types, user demographics, and transaction patterns.

Dataset: gaming_transactions
Table: item_transactions
"""

import pandas as pd
import random
from faker import Faker
from datetime import datetime, timedelta
import os

# Initialize Faker with Japanese locale
fake = Faker('ja_JP')

# Set random seed for reproducible results
random.seed(42)
Faker.seed(42)

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
        transaction_time = fake.date_time_between(start_date=start_date, end_date=end_date)
        
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
    
    # Create DataFrame
    df = pd.DataFrame(transactions)
    
    # Convert timestamp to proper format
    df['transaction_timestamp'] = pd.to_datetime(df['transaction_timestamp'])
    
    # Save to CSV
    csv_filename = 'gaming_transactions.csv'
    df.to_csv(csv_filename, index=False)
    print(f"✅ Data saved to {csv_filename}")
    
    
    # Display sample data
    print("\n📊 Sample Data:")
    print(df.head(10).to_string(index=False))
    
    # Display data summary
    print(f"\n📈 Data Summary:")
    print(f"Total transactions: {len(df)}")
    print(f"Date range: {df['transaction_timestamp'].min()} to {df['transaction_timestamp'].max()}")
    print(f"Total revenue: {df['amount_jpy'].sum():,} JPY")
    print(f"Average transaction: {df['amount_jpy'].mean():.0f} JPY")
    
    print(f"\n🎯 Item Type Distribution:")
    print(df['item_type'].value_counts().to_string())
    
    print(f"\n👥 User Tier Distribution:")
    print(df['user_tier'].value_counts().to_string())
    
    print(f"\n🌏 Region Distribution:")
    print(df['region'].value_counts().to_string())
    
    print(f"\n💻 Platform Distribution:")
    print(df['platform'].value_counts().to_string())
    
    print(f"\n📋 Next Steps:")
    print(f"1. Upload {csv_filename} to BigQuery using the UI")
    print(f"2. Dataset: gaming_transactions")
    print(f"3. Table: item_transactions")

if __name__ == "__main__":
    main()
