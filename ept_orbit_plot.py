import datetime as dt

import matplotlib.pyplot as plt
import numpy as np
from etspice import SOLO
from matplotlib import cm
from matplotlib.colors import Normalize
from matplotlib.dates import date2num
from pytz import utc
from scipy.constants import au
from solo_loader.epd import EPDData

from utils.labeling import date_labels, solar_system_grid
from utils.path_transform import PathTranform
from utils.style import set_style, get_foreground_color

fig, ax = plt.subplots(figsize=(6.5, 5.5))
set_style(fig, 'esa')

startdate = utc.localize(dt.datetime(2020, 5, 1))
enddate = utc.localize(dt.datetime(2020, 12, 10))

dates = np.array([startdate + dt.timedelta(seconds=i) for i in np.linspace(0, (enddate - startdate).total_seconds(), 1000)])
trajectory = SOLO.position(dates)
x = trajectory[:, 0] / au * 1e3
y = trajectory[:, 1] / au * 1e3

# plot orbit
ax.plot(x, y, color=get_foreground_color(), linewidth=1, zorder=10)

# load and prepare EPT data
epd = EPDData(startdate, enddate)
ept_electron = epd.ept.science.low_latency('foil', 'time')['sun']
ept_ion = epd.ept.science.low_latency('mag', 'time')['sun']

# note: this is just a summed up countrate from the sun telescope for now, not a flux/intensity/whatever.
data = ept_ion.sum(axis=1).resample('1H').mean()
data = np.log10(data)  # use logarithmic data
data[np.isinf(data)] = np.nan
data += 0.8  # arbitrary shift to get only positive values

data_e = ept_electron.sum(axis=1).resample('1H').mean()
data_e = np.log10(data_e)  # use logarithmic data
data_e[np.isinf(data_e)] = np.nan
data_e += 1.1  # arbitrary shift to get only positive values

cmap = cm.get_cmap('turbo')

# plot ion and electron data
for data, scale in [(data, 0.15), (data_e, -0.15)]:
    barwidth = date2num(data.index[1]) - date2num(data.index[0])
    mask = (dates > data.index[0]) * (dates < data.index[-1])
    norm = Normalize(vmin=data.min(), vmax=data.max())
    transform = PathTranform(x, y, startdate, enddate, scale=scale)

    ax.bar(data.index, data, transform=transform + ax.transData, color=cmap(norm(data)), width=barwidth, zorder=9)

# add labels at start of track
ax.plot([date2num(data.index[0]), date2num(data.index[0])],
        [-0.5, 0.5],
        transform=transform + ax.transData, color=get_foreground_color(), lw=2)
ax.text(date2num(data.index[0]) + 5, 0.35, 'e', transform=transform + ax.transData)
ax.text(date2num(data.index[0]) + 5, -0.9, 'ion', transform=transform + ax.transData)

# add arrows
for date in [dt.datetime(2020, 3, 29), dt.datetime(2020, 5, 27), dt.datetime(2020, 9, 11)]:
    ax.plot([date2num(date - dt.timedelta(days=2)), date2num(date), date2num(date - dt.timedelta(days=2))],
            [-0.2, 0, 0.2], transform=transform + ax.transData, color=get_foreground_color())

# plot grid and date labels
solar_system_grid(ax)
date_labels(ax, startdate, enddate, raiseddates=[
    utc.localize(dt.datetime(2020, 12, 1))
])

plt.axis('equal')
ax.set_ylim([-1.2, 1.2])
ax.set_xlim([-1.55, 1.1])
plt.axis('off')

plt.savefig('ept_orbit_plot.pdf')
plt.savefig('ept_orbit_plot.png', dpi=300)
plt.show()