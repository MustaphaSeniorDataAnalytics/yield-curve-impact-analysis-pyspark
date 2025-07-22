import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV file with semicolon delimiter
re_simulation_path = 'Export Resemulation.csv'
re_simulation_df = pd.read_csv(re_simulation_path, delimiter=';')

# Clean column names by removing extra quotation marks and whitespace
re_simulation_df.columns = re_simulation_df.columns.str.replace('"', '').str.strip()

# Convert WEEKLY_REPRICING_DATE to datetime
re_simulation_df['WEEKLY_REPRICING_DATE'] = pd.to_datetime(re_simulation_df['WEEKLY_REPRICING_DATE'], format='%d/%m/%Y')

# Function to parse yield curve data with error handling
def parse_yield_curve(yield_curve_str):
    yield_curve_pairs = yield_curve_str.split()
    yield_curve_dict = {}
    for pair in yield_curve_pairs:
        if ':' not in pair:
            continue
        term, value = pair.split(':')
        try:
            term = int(term.strip().replace('"', '').replace("'", ""))
            value = float(value.strip().replace('"', '').replace("'", ""))
            yield_curve_dict[term] = value
        except ValueError:
            continue
    return yield_curve_dict

# Apply the parsing function and handle missing data
re_simulation_df['Parsed_Yield_Curve'] = re_simulation_df['YIELD_CURVE'].apply(parse_yield_curve)
parsed_yield_curves_df = pd.DataFrame(re_simulation_df['Parsed_Yield_Curve'].tolist(), index=re_simulation_df.index)

# Convert day terms to weekly terms
def convert_to_weekly(yield_curve_dict):
    weekly_curve = {}
    for day, value in yield_curve_dict.items():
        week = round(day / 7)
        if week not in weekly_curve:
            weekly_curve[week] = []
        weekly_curve[week].append(value)
    # Average the values for each week
    for week in weekly_curve:
        weekly_curve[week] = sum(weekly_curve[week]) / len(weekly_curve[week])
    return weekly_curve

re_simulation_df['Weekly_Yield_Curve'] = re_simulation_df['Parsed_Yield_Curve'].apply(convert_to_weekly)
weekly_yield_curves_df = pd.DataFrame(re_simulation_df['Weekly_Yield_Curve'].tolist(), index=re_simulation_df.index)

# Aggregate data by week
weekly_yield_curves_df = weekly_yield_curves_df.groupby(re_simulation_df['WEEKLY_REPRICING_DATE']).mean()

# Convert necessary columns to numeric for UWR calculation
columns_to_convert = ['EXP_PREMIUM', 'DISCOUNTED_EXTERNAL_EXPENSES', 'DISCOUNTED_EXP_LOSS', 'DISCOUNTED_EXP_PREMIUM']
for col in columns_to_convert:
    re_simulation_df[col] = pd.to_numeric(re_simulation_df[col].str.replace(',', '.'))

# Calculate the discounted UWR
re_simulation_df['Discounted_UWR'] = (
    re_simulation_df['DISCOUNTED_EXTERNAL_EXPENSES'] +
    re_simulation_df['DISCOUNTED_EXP_LOSS'] +
    re_simulation_df['EXP_PREMIUM'] -
    re_simulation_df['DISCOUNTED_EXP_PREMIUM']
) / re_simulation_df['EXP_PREMIUM']

# Aggregate Discounted UWR by week
discounted_uwr_df = re_simulation_df.groupby('WEEKLY_REPRICING_DATE')['Discounted_UWR'].mean()
discounted_uwr_df = discounted_uwr_df.reindex(weekly_yield_curves_df.index, method='bfill')


print (discounted_uwr_df)
# Plot the yield curves and Discounted UWR
fig, ax1 = plt.subplots(figsize=(14, 8))
lines = []
for term in weekly_yield_curves_df.columns:
    line, = ax1.plot(weekly_yield_curves_df.index, weekly_yield_curves_df[term], marker='o', label=f'{term} Weeks')
    lines.append(line)

# Add Discounted UWR to the plot
ax2 = ax1.twinx()
line_uwr, = ax2.plot(discounted_uwr_df.index, discounted_uwr_df, marker='x', color='red', label='Discounted UWR')

plt.title('Yield Curves and Discounted UWR Over Time')
ax1.set_xlabel('Date')
ax1.set_ylabel('Yield')
ax2.set_ylabel('Discounted UWR')

# Adjust layout to prevent label overlap
fig.tight_layout(rect=[0, 0, 0.85, 1])

# Create combined legend
lines_labels = [ax.get_legend_handles_labels() for ax in [ax1, ax2]]
lines, labels = [sum(lol, []) for lol in zip(*lines_labels)]
ax1.legend(lines, labels, loc='center left', bbox_to_anchor=(1.05, 0.5), ncol=1)

ax1.grid(True)

# Add interactive hover annotations for yield curves
annot = ax1.annotate("", xy=(0,0), xytext=(20,20), textcoords="offset points",
                    bbox=dict(boxstyle="round", fc="w"),
                    arrowprops=dict(arrowstyle="->"))
annot.set_visible(False)

def update_annot(line, ind):
    x, y = line.get_data()
    annot.xy = (x[ind], y[ind])
    text = f"Date: {weekly_yield_curves_df.index[ind].strftime('%Y-%m-%d')}\nYield: {y[ind]:.4f}"
    annot.set_text(text)
    annot.get_bbox_patch().set_alpha(0.4)

def hover(event):
    vis = annot.get_visible()
    if event.inaxes == ax1:
        for line in lines:
            cont, ind = line.contains(event)
            if cont:
                update_annot(line, ind["ind"][0])
                annot.set_visible(True)
                fig.canvas.draw_idle()
                return
    if vis:
        annot.set_visible(False)
        fig.canvas.draw_idle()

fig.canvas.mpl_connect("motion_notify_event", hover)

# Add interactive hover annotations for Discounted UWR
annot_uwr = ax2.annotate("", xy=(0,0), xytext=(20,20), textcoords="offset points",
                    bbox=dict(boxstyle="round", fc="w"),
                    arrowprops=dict(arrowstyle="->"))
annot_uwr.set_visible(False)

def update_annot_uwr(line, ind):
    x, y = line.get_data()
    annot_uwr.xy = (x[ind], y[ind])
    text = f"Date: {discounted_uwr_df.index[ind].strftime('%Y-%m-%d')}\nDiscounted UWR: {y[ind]:.4f}"
    annot_uwr.set_text(text)
    annot_uwr.get_bbox_patch().set_alpha(0.4)

def hover_uwr(event):
    vis = annot_uwr.get_visible()
    if event.inaxes == ax2:
        cont, ind = line_uwr.contains(event)
        if cont:
            update_annot_uwr(line_uwr, ind["ind"][0])
            annot_uwr.set_visible(True)
            fig.canvas.draw_idle()
            return
    if vis:
        annot_uwr.set_visible(False)
        fig.canvas.draw_idle()

fig.canvas.mpl_connect("motion_notify_event", hover_uwr)

plt.show()
