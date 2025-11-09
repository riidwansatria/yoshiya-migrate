import pandas as pd
from datetime import datetime

def transform_csv(input_file, output_file, mapping_file="data/menu_mapping.csv"):
    """
    Transform CSV with proper column ordering for meals and menu name mapping
    """
    df = pd.read_csv(input_file, encoding='utf-8-sig')
    
    # Load menu mapping
    try:
        menu_map_df = pd.read_csv(mapping_file, encoding='utf-8-sig')
        # Create dictionary: old_name -> new_name
        menu_mapping = dict(zip(menu_map_df['old_name'].fillna(''), menu_map_df['new_name']))
        # Remove empty key if exists
        menu_mapping.pop('', None)
        print(f"Loaded {len(menu_mapping)} menu mappings from {mapping_file}")
    except FileNotFoundError:
        print(f"Warning: {mapping_file} not found. Proceeding without menu mapping.")
        menu_mapping = {}
    
    # Helper function to safely get column
    def safe_get(col_name, default=''):
        return df[col_name] if col_name in df.columns else default
    
    # Helper function to map menu names
    def map_menu_name(old_name):
        if pd.isna(old_name) or old_name == '':
            return ''
        old_name_str = str(old_name).strip()
        return menu_mapping.get(old_name_str, old_name_str)
    
    # Helper function to get and map meal column
    def get_mapped_meal_column(idx):
        if idx < len(df.columns):
            col_data = df.iloc[:, idx]
            return col_data.apply(map_menu_name) if menu_mapping else col_data
        return ''
    
    # Find all repeating meal columns
    col_names = df.columns.tolist()
    
    print(f"Total columns: {len(col_names)}")
    
    # The meal blocks start at columns: 86, 98, 110, 122, 134
    # 食事名 is at position +4 from each start, so: 90, 102, 114, 126, 138
    
    meal_name_indices = [90, 102, 114, 126, 138]
    
    # Verify they exist in the dataframe
    meal_name_indices = [idx for idx in meal_name_indices if idx < len(col_names)]
    
    print(f"Using hardcoded meal positions: {meal_name_indices}")
    print(f"Found {len(meal_name_indices)} meal sets")
    
    # Create ordered dictionary to maintain column order
    from collections import OrderedDict
    data = OrderedDict()
    
    # Basic columns first
    data['ステータス'] = ''
    data['注意'] = ''
    data['確認'] = ''
    data['予約日'] = safe_get('予約日')
    data['部屋'] = safe_get('食事場所')
    data['団体名（お客様名）'] = safe_get('団体名')
    data['予約時間'] = safe_get('到着時刻')
    
    # First meal info (special position) - WITH MAPPING APPLIED
    if len(meal_name_indices) > 0:
        idx = meal_name_indices[0]
        data['お料理名１'] = get_mapped_meal_column(idx)
        data['お客様人数'] = safe_get('来店人数')
        data['単価１'] = df.iloc[:, idx + 1] if (idx + 1) < len(df.columns) else ''
    else:
        data['お料理名１'] = ''
        data['お客様人数'] = safe_get('来店人数')
        data['単価１'] = ''
    
    data['ご予算(メニューが未定の場合はご記入ください）'] = ''
    data['法人名（旅行会社名）'] = safe_get('業者名')
    data['ご要望欄(注意事項等）'] = safe_get('備考')
    data['担当者名'] = safe_get('業者担当者')
    data['メールアドレス'] = ''
    data['電話番号'] = safe_get('業者電話番号')
    data['手配者名'] = safe_get('業者手配者')
    data['添乗員人数'] = safe_get('添乗員数')
    data['乗務員人数'] = safe_get('乗務員数')
    data['Column 52'] = ''
    
    # Now add meal 1 details
    if len(meal_name_indices) > 0:
        idx = meal_name_indices[0]
        data['料理備考１'] = df.iloc[:, idx + 7] if (idx + 7) < len(df.columns) else ''
        data['料理１の数量'] = df.iloc[:, idx - 3] if (idx - 3) >= 0 else ''
    else:
        data['料理備考１'] = ''
        data['料理１の数量'] = ''
    
    # Add meals 2-6 in correct order: お料理名, 料理備考, 料理数量, 単価 - WITH MAPPING APPLIED
    for meal_num in range(2, 7):
        if meal_num <= len(meal_name_indices):
            idx = meal_name_indices[meal_num - 1]
            data[f'お料理名{meal_num}'] = get_mapped_meal_column(idx)
            data[f'料理備考{meal_num}'] = df.iloc[:, idx + 7] if (idx + 7) < len(df.columns) else ''
            data[f'料理{meal_num}の数量'] = df.iloc[:, idx - 3] if (idx - 3) >= 0 else ''
            data[f'単価{meal_num}'] = df.iloc[:, idx + 1] if (idx + 1) < len(df.columns) else ''
        else:
            data[f'お料理名{meal_num}'] = ''
            data[f'料理備考{meal_num}'] = ''
            data[f'料理{meal_num}の数量'] = ''
            data[f'単価{meal_num}'] = ''
    
    # Final columns
    data['Column 49'] = ''
    data['郵便番号'] = safe_get('業者郵便番号')
    data['住所'] = safe_get('業者住所')
    data['支店名'] = ''
    data['FAX'] = safe_get('業者ＦＡＸ番号')
    data['メールアドレス(確認のためもう一度入力してください）'] = ''
    data['Column 51'] = ''
    data['タイムスタンプ'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Generate Increment in YYYYMMDDNNNN format
    today = datetime.now().strftime('%Y%m%d')
    data['Increment'] = [f"{today}{str(i).zfill(4)}" for i in range(1, len(df) + 1)]
    
    # Convert to DataFrame
    target_df = pd.DataFrame(data)
    
    # Replace all NaN values with empty strings
    target_df = target_df.fillna('')
    
    # Remove leading "+" from all 料理備考 columns
    for col in target_df.columns:
        if col.startswith('料理備考'):
            target_df[col] = target_df[col].astype(str).str.lstrip('+')
    
    # Remove trailing spaces from all string columns
    for col in target_df.columns:
        if target_df[col].dtype == 'object':  # String columns
            target_df[col] = target_df[col].astype(str).str.rstrip()
    
    # Save to output file
    target_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"Transformation complete! Output saved to: {output_file}")
    print(f"Processed {len(target_df)} rows with {len(meal_name_indices)} meal sets")
    
    return target_df

# Usage example
if __name__ == "__main__":
    input_file = "data/source_data.csv"
    output_file = "data/transformed_data.csv"
    mapping_file = "data/menu_mapping.csv"
    
    # Transform with multiple meals support and menu mapping
    result = transform_csv(input_file, output_file, mapping_file)
    
    print("\nFirst few rows of output:")
    print(result.head())