import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV files with semicolon delimiter
original_pricing_path = 'Export original pricing.csv'
re_simulation_path = 'Export Resemulation.csv'

original_pricing_df = pd.read_csv(original_pricing_path, delimiter=';')
re_simulation_df = pd.read_csv(re_simulation_path, delimiter=';')

# Function to clean and convert columns to numeric
def clean_and_convert(df, columns):
    for col in columns:
        df[col] = df[col].str.replace(',', '.').astype(float)
    return df

# List of columns to clean and convert
columns_to_convert = [
    'EXP_PREMIUM', 'EXP_LOSS', 'EXTERNAL_EXPENSES', 
    'DISCOUNTED_EXP_PREMIUM', 'DISCOUNTED_EXP_LOSS', 'DISCOUNTED_EXTERNAL_EXPENSES'
]

# Clean column names by removing extra quotation marks and whitespace
original_pricing_df.columns = original_pricing_df.columns.str.replace('"', '').str.strip()
re_simulation_df.columns = re_simulation_df.columns.str.replace('"', '').str.strip()

# Clean and convert the columns in both dataframes
original_pricing_df = clean_and_convert(original_pricing_df, columns_to_convert)
re_simulation_df = clean_and_convert(re_simulation_df, columns_to_convert)

# Calculate the discounted UWR for both dataframes
original_pricing_df['Discounted_UWR'] = (
    original_pricing_df['DISCOUNTED_EXTERNAL_EXPENSES'] +
    original_pricing_df['DISCOUNTED_EXP_LOSS'] +
    original_pricing_df['EXP_PREMIUM'] -
    original_pricing_df['DISCOUNTED_EXP_PREMIUM']
) / original_pricing_df['EXP_PREMIUM']

re_simulation_df['Discounted_UWR'] = (
    re_simulation_df['DISCOUNTED_EXTERNAL_EXPENSES'] +
    re_simulation_df['DISCOUNTED_EXP_LOSS'] +
    re_simulation_df['EXP_PREMIUM'] -
    re_simulation_df['DISCOUNTED_EXP_PREMIUM']
) / re_simulation_df['EXP_PREMIUM']


# Merge the results to compare the original and re-simulation UWR
merged_df = original_pricing_df[['CONTRACT_ID', 'Discounted_UWR']].merge(
    re_simulation_df[['CONTRACT_ID', 'Discounted_UWR', 'WEEKLY_REPRICING_DATE']], 
    on='CONTRACT_ID', suffixes=('_Original', '_ReSim')
)

print (merged_df.head(10))
# Calculate the impact
merged_df['UWR_Impact'] = merged_df['Discounted_UWR_ReSim'] - merged_df['Discounted_UWR_Original']

# Convert WEEKLY_REPRICING_DATE to datetime
merged_df['WEEKLY_REPRICING_DATE'] = pd.to_datetime(merged_df['WEEKLY_REPRICING_DATE'], format='%d/%m/%Y')

# Plotting
plt.figure(figsize=(14, 10))

# Histogram of UWR Impact
plt.subplot(2, 2, 1)
plt.hist(merged_df['UWR_Impact'], bins=30, color='skyblue', edgecolor='black')
plt.title('Histogram of UWR Impact')
plt.xlabel('UWR Impact')
plt.ylabel('Frequency')

# Boxplot of UWR Impact
plt.subplot(2, 2, 2)
plt.boxplot(merged_df['UWR_Impact'], vert=False)
plt.title('Boxplot of UWR Impact')
plt.xlabel('UWR Impact')

# Scatter Plot of Original vs. Re-simulated UWR
plt.subplot(2, 1, 2)
plt.scatter(merged_df['Discounted_UWR_Original'], merged_df['Discounted_UWR_ReSim'], alpha=0.5, color='blue')
plt.title('Scatter Plot of Original vs. Re-simulated UWR')
plt.xlabel('Original Discounted UWR')
plt.ylabel('Re-simulated Discounted UWR')
plt.plot([merged_df['Discounted_UWR_Original'].min(), merged_df['Discounted_UWR_Original'].max()], 
         [merged_df['Discounted_UWR_Original'].min(), merged_df['Discounted_UWR_Original'].max()], 
         color='red', linestyle='--')

plt.tight_layout()
plt.show()
