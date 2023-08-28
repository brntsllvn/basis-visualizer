import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.animation import FFMpegWriter
from matplotlib.ticker import FuncFormatter
from matplotlib.font_manager import FontProperties
import numpy as np
import pandas as pd

# Font
plt.rcParams.update({'font.size': 16})
orpheus_font = FontProperties(fname='./fonts/orpheus-regular.ttf')

# Existing logic for generating data
initial_stock_price = 100  
initial_cash = 100000  
days = 100  
drift = 0.05  
volatility = 0.30  
daily_drift = drift / 252  
daily_volatility = volatility / np.sqrt(252)  

stock_price = initial_stock_price
cash = initial_cash
shares = initial_cash // initial_stock_price
basis = shares * initial_stock_price

df = pd.DataFrame(columns=['Day', 'Stock Price', 'Portfolio Value', 'Cash Deposited', 'Basis with Harvesting', 'Basis without Harvesting'])
df.loc[0] = [0, initial_stock_price, shares * initial_stock_price, initial_cash, basis, basis]
df['Cumulative Harvested Losses'] = 0  # Initialize with zeros

cumulative_loss = 0
for day in range(1, days):
    shock = np.random.normal(loc=daily_drift, scale=daily_volatility)
    stock_price *= np.exp(shock)
    portfolio_value = shares * stock_price
    if portfolio_value < basis:
        loss_amount = basis - portfolio_value
        cumulative_loss += loss_amount
        basis = portfolio_value
    df.loc[day] = [day, stock_price, portfolio_value, initial_cash, basis, shares * initial_stock_price, cumulative_loss]

def dollar_format(x, pos):
    return f'${int(x):,.0f}'

# Initialize figure and axis
fig, ax = plt.subplots(figsize=(12, 6.28))
plt.subplots_adjust(top=0.80)
fig.patch.set_facecolor('#E5DFF5')  # Set background color for entire figure

# Apply custom font to all text elements
for item in ([ax.title, ax.xaxis.label, ax.yaxis.label] + ax.get_xticklabels() + ax.get_yticklabels()):
    item.set_fontproperties(orpheus_font)

line1, = ax.plot([], [], 'k-', label='Portfolio Value', linewidth=1)  # Black solid
line2, = ax.plot([], [], 'b--', label='Basis with Harvesting', linewidth=1)  # Blue dashed
line3, = ax.plot([], [], 'r--', label='Basis without Harvesting', linewidth=1)  # Red dashed

def init():
    line1.set_data([], [])
    line2.set_data([], [])
    line3.set_data([], [])
    # Dummy scatter for the legend to get a green dot
    dummy_scatter = ax.scatter([], [], s=100, color='green', label='Harvested Loss')
    # Dummy area fill for legend
    cumulative_harvest = ax.fill_between([], [], color='lightgreen', alpha=0.6, label='Cumulative Harvested Losses')
    legend_labels = [line1, line2, line3, dummy_scatter, cumulative_harvest]
    ax.legend(handles=legend_labels, labels=['Portfolio Value', 'Basis with Harvesting', 'Basis without Harvesting', 'Harvested Loss', 'Cumulative Harvested Losses'], loc='lower left', ncol=1, frameon=False, prop=orpheus_font)
    
    # Main Title
    ax.annotate('Scenario # 1: No Wash Sale Rule', xy=(0.5, 1), xycoords='axes fraction', fontsize=32, 
                xytext=(0, 40), textcoords='offset points',
                ha='center', va='baseline', fontproperties=orpheus_font)
    
    # Subtitle
    ax.annotate('Tax-Loss Harvesting Case Studies', xy=(0.5, 1), xycoords='axes fraction', fontsize=18, 
                xytext=(0, 15), textcoords='offset points',
                ha='center', va='baseline', fontproperties=orpheus_font)
    
    # ax.set_title('Tax-Loss Harvesting Illustrated', fontproperties=orpheus_font, pad=10, fontsize=32)
    # ax.text(0.5, 1.00, 'Scenario # 1: No Wash Sale Rule', transform=ax.transAxes, ha='center', va='center', fontsize=18, fontproperties=orpheus_font)
    
    # Add watermark text
    x_center = days / 2
    y_center = max(df['Portfolio Value']) / 2
    ax.text(x_center, y_center, 'The Tax Alpha Insider', 
            fontsize=28, ha='center', va='center', alpha=0.5, 
            color='#363E21', fontproperties=orpheus_font, zorder=0)
    ax.text(x_center, y_center - 0.10 * max(df['Portfolio Value']), '© 2023', 
        fontsize=12, ha='center', va='center', alpha=0.5, 
        color='#363E21', fontproperties=orpheus_font, zorder=0)
    return line1, line2, line3,

# The update function for the animation
def update(day):
    line1.set_data(df['Day'][:day], df['Portfolio Value'][:day])
    line2.set_data(df['Day'][:day], df['Basis with Harvesting'][:day])
    line3.set_data(df['Day'][:day], df['Basis without Harvesting'][:day])
        
    if day > 0 and df['Basis with Harvesting'][day] < df['Basis with Harvesting'][day - 1]:
        loss_amount = df['Basis with Harvesting'][day - 1] - df['Basis with Harvesting'][day]
        normalized_loss = loss_amount / df['Portfolio Value'][day]
        ax.scatter(day, df['Portfolio Value'][day], s=normalized_loss * 10000, color='green', label='Harvested Loss' if day == 1 else "")
    
    ax.fill_between(df['Day'][:day], 0, df['Cumulative Harvested Losses'][:day], 
        color='lightgreen', alpha=0.6, label='Cumulative Harvested Losses' if day==1 else "")
    
    return line1, line2, line3,

ax.set_xlim(0, days)
ax.set_ylim(0, max(df['Portfolio Value']) + 10000)
ax.set_xlabel('Day')
ax.yaxis.set_major_formatter(FuncFormatter(dollar_format))
ani = animation.FuncAnimation(fig, update, frames=range(days), init_func=init, blit=False)

writer = FFMpegWriter(fps=25, metadata=dict(artist='Me'), bitrate=1800)
ani.save('animation.mp4', writer=writer)
