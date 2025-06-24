import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.animation import PillowWriter
import matplotlib.cm as cm

# 1. Read your Excel, using the second row as the header (zero-based header=1)
# IMPORTANT: Ensure 'Data.xlsx' exists in the same directory as this script.
try:
    df = pd.read_excel("Data.xlsx", header=1)
except FileNotFoundError:
    print("Error: Data.xlsx not found. Please ensure the Excel file is in the same directory as the script.")
    exit()
except Exception as e:
    print(f"An error occurred while reading the Excel file: {e}")
    exit()

# 2. Clean up any empty “Unnamed” columns and give the glacier column a short name
df = df.loc[:, ~df.columns.str.startswith("Unnamed")]
df = df.rename(columns={"World Glacier Monitoring Service": "MassBalance"})

# 3. Quick check: what are your columns?
print("Columns in DataFrame:", list(df.columns))

# 4. Assign your data series
# Ensure these column names match exactly what's in your Excel file after header handling.
try:
    years = df["year"]
    temps = df[[
        "Berkeley Earth", "ERA5", "GISTEMP",
        "HadCRUT5", "JRA-3Q", "NOAAGlobalTemp"
    ]]
    mass = df["MassBalance"]
except KeyError as e:
    print(f"Error: Missing expected column in Data.xlsx: {e}. Please check your column names.")
    exit()

# 5. Set up the figure with twin y-axes
fig, ax1 = plt.subplots(figsize=(9, 5))
ax2 = ax1.twinx()

# --- Removed: Suggestion 2 (Fade Out Glacier Line in the Background) ---
# The faded background line for glacier mass balance is no longer plotted here.

# 6. Create empty Line2D objects for each series
cmap_temp = plt.colormaps.get_cmap('tab10')
# Removed linestyles as we want straight lines for temperature.
# linestyles = ['-', '--', ':', '-.', (0, (3, 5, 1, 5)), (0, (3, 1, 1, 1, 1, 1))]

lines_temp = [
    ax1.plot([], [], label=name, color=cmap_temp(i),
             # Removed linestyle: lines are now solid by default
             markersize=4)[0]
    for i, name in enumerate(temps.columns)
]
# This line_mass will be the animated part for the glacier data
line_mass = ax2.plot([], [], label="World Glacier Monitoring Service",
                     linestyle="--", color="k")[0]

# --- Suggestion 1: Add a Dynamic Current Year Label ---
# Initialize the text object for the current year and average temperature. Position it carefully.
# We will update its content in the update function.
current_year_text = ax1.text(0.98, 0.02, '', transform=ax1.transAxes,
                             fontsize=12, color='gray', ha='right', va='bottom',
                             bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="none", alpha=0.7))


# 7. Labeling & legend
# --- Suggestion 4: Enhance Axis Labels and Title Font ---
ax1.set_xlabel("Years", fontfamily='arial', fontweight='bold', fontsize=16)
ax1.set_ylabel("Global Mean Temperature (°C)", fontfamily='arial', fontweight='bold', fontsize=16)
ax2.set_ylabel("Glacier Cumulative Mass Balance (m w.e.)", fontfamily='arial', fontweight='bold', fontsize=16)

##fig.suptitle("Global Temperature Anomalies and Glacier Mass Balance Over Time",
##             fontsize=16, fontfamily='serif', fontweight='bold')

all_lines = lines_temp + [line_mass]
ax1.legend(all_lines, [l.get_label() for l in all_lines],
           loc="upper right",
           fontsize='small',
           frameon=True,
           edgecolor='gray',
           ncol=1)

# 8. Add dashed grid lines to both axes
ax1.grid(True, linestyle='--', alpha=0.6, color='lightgray', linewidth=0.7)
ax2.grid(True, linestyle='--', alpha=0.6, color='lightgray', linewidth=0.7)

# 9. Initialization function
def init():
    ax1.set_xlim(years.min(), years.max())

    # Dynamically adjust y-axis limits for temperature based on data range
    # Added some padding to min/max to prevent lines from touching the plot edges
    ax1.set_ylim(temps.min().min() - (temps.max().max() - temps.min().min()) * 0.1,
                 temps.max().max() + (temps.max().max() - temps.min().min()) * 0.1)

    # Dynamically adjust y-axis limits for mass balance
    ax2.set_ylim(mass.min() - (mass.max() - mass.min()) * 0.1,
                 mass.max() + (mass.max() - mass.min()) * 0.1)

    ticks = list(range(int(years.min()), int(years.max()) + 1, 10))
    if int(years.max()) not in ticks:
        ticks.append(int(years.max()))
    ax1.set_xticks(ticks)
    ax1.set_xticklabels(ticks, rotation=45)

    ax1.tick_params(axis='x', labelsize=9)
    ax1.tick_params(axis='y', labelsize=9)
    ax2.tick_params(axis='y', labelsize=9)
    ax1.minorticks_on()
    ax2.minorticks_on()

    for ln in all_lines:
        ln.set_data([], [])

    # Initialize current year and average temperature text
    current_year_text.set_text('') # Set initial text to empty

    # Return all artists that will be animated, including the year text
    return all_lines + [current_year_text]

# 10. Update function
def update(frame):
    if frame >= len(df):
        return all_lines + [current_year_text]

    x = years.iloc[:frame+1]
    for ln, col in zip(lines_temp, temps.columns):
        ln.set_data(x, temps[col].iloc[:frame+1])
    line_mass.set_data(x, mass.iloc[:frame+1])

    # Calculate the average temperature for the current year
    # This takes the mean across all temperature sources for the 'frame' (current year) row
    avg_temp_current_year = temps.iloc[frame].mean()

    # --- Update the Dynamic Current Year Label with average temperature ---
    current_year_text.set_text(f'Year: {int(years.iloc[frame])}\nAvg. Temp. Rise: {avg_temp_current_year:.2f}°C')

    # Return all artists that were modified, including the year text
    return all_lines + [current_year_text]

# 11. Build the animation
ani = FuncAnimation(
    fig, update, frames=len(df),
    init_func=init, blit=True, interval=100
)

plt.tight_layout()
plt.show()

# 12. Create the PillowWriter, matching your desired FPS
writer = PillowWriter(fps=5)

# 13. Save out the GIF (it’ll land in your working folder)
print("Saving animation... This might take a moment.")
ani.save("temperature_massbalance.gif", writer=writer, dpi=300)

print("✅ Saved animation as temperature_massbalance.gif")
