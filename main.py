import matplotlib.pyplot as plt
import matplotlib.animation as animation 
from matplotlib.animation import FFMpegWriter
from matplotlib.ticker import FuncFormatter
from matplotlib.font_manager import FontProperties
import numpy as np
import pandas as pd

# Custom Orpheus font
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

for day in range(1, days):
    shock = np.random.normal(loc=daily_drift, scale=daily_volatility)
    stock_price *= np.exp(shock)
    portfolio_value = shares * stock_price
    if portfolio_value < basis:
        basis = portfolio_value
    df.loc[day] = [day, stock_price, portfolio_value, initial_cash, basis, shares * initial_stock_price]

def dollar_format(x, pos):
    return f'${int(x):,.0f}'

# Create the figure and the line that will be animated
fig, ax = plt.subplots()

# Apply custom font to all text elements
for item in ([ax.title, ax.xaxis.label, ax.yaxis.label] + ax.get_xticklabels() + ax.get_yticklabels()):
    item.set_fontproperties(orpheus_font)

line1, = ax.plot([], [], label='Portfolio Value')
line2, = ax.plot([], [], label='Basis with Harvesting')
line3, = ax.plot([], [], label='Basis without Harvesting')

def init():
    line1.set_data([], [])
    line2.set_data([], [])
    line3.set_data([], [])
    return line1, line2, line3,

# The update function for the animation
def update(day):
    line1.set_data(df['Day'][:day], df['Portfolio Value'][:day])
    line2.set_data(df['Day'][:day], df['Basis with Harvesting'][:day])
    line3.set_data(df['Day'][:day], df['Basis without Harvesting'][:day])
    if day > 0 and df['Basis with Harvesting'][day] < df['Basis with Harvesting'][day - 1]:
        loss_amount = df['Basis with Harvesting'][day - 1] - df['Basis with Harvesting'][day]
        normalized_loss = loss_amount / df['Portfolio Value'][day]
        ax.scatter(day, df['Portfolio Value'][day], s=normalized_loss * 15000, color='green', label='Harvested Loss' if day == 1 else "")
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=3, frameon=False, prop=orpheus_font)  # Fixed the legend
    return line1, line2, line3,

ax.set_xlim(0, days)
ax.set_ylim(0, max(df['Portfolio Value']) + 10000)
ax.set_xlabel('Day')
ax.set_ylabel('Value ($)')
ax.yaxis.set_major_formatter(FuncFormatter(dollar_format))
ani = animation.FuncAnimation(fig, update, frames=range(days), init_func=init, blit=True)

# Save the animation using FFMpegWriter
writer = FFMpegWriter(fps=20, metadata=dict(artist='Me'), bitrate=1800)
ani.save('animation.mp4', writer=writer)