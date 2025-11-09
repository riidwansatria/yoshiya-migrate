import pandas as pd
from datetime import datetime

def transform_csv(input_file, output_file):
    """
    Advanced version that handles multiple meal entries from repeating columns
    """
    df = pd.read_csv(input_file, encoding='utf-8-sig')
    target_df = pd.DataFrame()
    
    # Helper function to safely get column
    def safe_get(col_name, default=''):
        return df[col_name] if col_name in df.columns else default
    
    # Basic mapping
    target_df['ステータス'] = ''
    target_df['注意確認'] = ''
    target_df['予約日'] = safe_get('予約日')
    target_df['部屋'] = ''
    target_df['団体名（お客様名）'] = safe_get('団体名')
    target_df['予約時間'] = safe_get('到着時刻')
    
    # Map multiple meal sets (if they exist in source)
    meal_sets = []
    col_names = df.columns.tolist()
    
    # Find all 食事名 columns
    for i, col in enumerate(col_names):
        if col == '食事名':
            meal_sets.append(i)
    
    # Map first meal
    if len(meal_sets) > 0:
        base_idx = meal_sets[0]
        target_df['お料理名１'] = df.iloc[:, base_idx] if base_idx < len(df.columns) else ''
        target_df['お客様人数'] = safe_get('食事人数')
        target_df['単価１'] = df.iloc[:, base_idx + 1] if (base_idx + 1) < len(df.columns) else ''
        target_df['料理備考１'] = df.iloc[:, base_idx + 6] if (base_idx + 6) < len(df.columns) else ''
        target_df['料理１の数量'] = df.iloc[:, base_idx - 2] if (base_idx - 2) >= 0 else ''
    else:
        target_df['お料理名１'] = ''
        target_df['お客様人数'] = safe_get('食事人数', 0)
        target_df['単価１'] = ''
        target_df['料理備考１'] = ''
        target_df['料理１の数量'] = ''
    
    target_df['ご予算(メニューが未定の場合はご記入ください）'] = ''
    target_df['法人名（旅行会社名）'] = safe_get('業者名')
    target_df['ご要望欄(注意事項等）'] = safe_get('備考')
    target_df['担当者名'] = safe_get('業者担当者')
    target_df['メールアドレス'] = ''
    target_df['電話番号'] = safe_get('業者電話番号')
    target_df['手配者名'] = safe_get('業者手配者')
    target_df['添乗員人数'] = safe_get('添乗員数')
    target_df['乗務員人数'] = safe_get('乗務員数')
    
    # Map additional meals (2-6)
    for meal_num in range(2, 7):
        if len(meal_sets) >= meal_num:
            idx = meal_sets[meal_num - 1]
            target_df[f'お料理名{meal_num}'] = df.iloc[:, idx] if idx < len(df.columns) else ''
            target_df[f'料理備考{meal_num}'] = df.iloc[:, idx + 6] if (idx + 6) < len(df.columns) else ''
            target_df[f'料理{meal_num}の数量'] = df.iloc[:, idx - 2] if (idx - 2) >= 0 else ''
            target_df[f'単価{meal_num}'] = df.iloc[:, idx + 1] if (idx + 1) < len(df.columns) else ''
        else:
            target_df[f'お料理名{meal_num}'] = ''
            target_df[f'料理備考{meal_num}'] = ''
            target_df[f'料理{meal_num}の数量'] = ''
            target_df[f'単価{meal_num}'] = ''
    
    target_df['郵便番号'] = safe_get('業者郵便番号')
    target_df['住所'] = safe_get('業者住所')
    target_df['支店名'] = ''
    target_df['FAX'] = safe_get('業者FAX番号')
    target_df['メールアドレス(確認のためもう一度入力してください）'] = ''
    target_df['タイムスタンプ'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    target_df['Increment'] = range(1, len(target_df) + 1)
    
    target_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"Advanced transformation complete! Output saved to: {output_file}")
    print(f"Processed {len(target_df)} rows with {len(meal_sets)} meal sets")
    
    return target_df


# Usage example
if __name__ == "__main__":
    input_file = "data/source_data.csv"
    output_file = "data/transformed_data.csv"
    
    # Use the basic version
    result = transform_csv(input_file, output_file)
    
    print("\nFirst few rows of output:")
    print(result.head())