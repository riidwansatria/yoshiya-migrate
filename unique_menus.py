import pandas as pd

# Read source data
df = pd.read_csv("data/source_data.csv", encoding='utf-8-sig')

# Extract all unique menu names from columns 90, 102, 114, 126, 138
meal_indices = [90, 102, 114, 126, 138]
all_menus = []

for idx in meal_indices:
    if idx < len(df.columns):
        all_menus.extend(df.iloc[:, idx].dropna().unique())

# Get unique, sorted list
unique_menus = sorted(set(all_menus))

# Save to file for review
with open('data/unique_menu_names.txt', 'w', encoding='utf-8') as f:
    for menu in unique_menus:
        f.write(f"{menu}\n")

print(f"Found {len(unique_menus)} unique menu names")
print("\nFirst 20:")
for menu in unique_menus[:20]:
    print(menu)