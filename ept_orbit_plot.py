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

from utils.labeling import date_labels, solar_system_grid, get_textalign
from utils.path_transform import PathTranform
from utils.style import set_style, get_foreground_color, get_title_font


def combine_bins(df):
    """
    Combines all energy bins of a flux DataFrame
    """
    return ((df * df.columns.length).sum(axis=1) / df.columns.length.to_series().sum())

fig, ax = plt.subplots(figsize=(6.5, 5.5))
set_style(fig, 'esa')

orbit_number = 1

if orbit_number == 1:
    title = 'first orbit'
    startdate = utc.localize(dt.datetime(2020, 2, 28))
    enddate = utc.localize(dt.datetime(2020, 10, 1))
    angle = 33
elif orbit_number == 2:
    title = 'second orbit'
    startdate = utc.localize(dt.datetime(2020, 10, 1))
    enddate = utc.localize(dt.datetime(2021, 3, 1))
    angle = 65
else:
    raise ValueError(f'orbit {orbit_number} not yet defined')

dates = np.array([startdate + dt.timedelta(seconds=i) for i in np.linspace(0, (enddate - startdate).total_seconds(), 5000)])
trajectory = SOLO.position(dates)
x = trajectory[:, 0] / au * 1e3
y = trajectory[:, 1] / au * 1e3

# plot orbit
ax.plot(x, y, color=get_foreground_color(), linewidth=1, zorder=10)

# load and prepare EPT data
epd = EPDData(startdate, enddate)
ept_electron = epd.ept.science.low_latency('foil', 'time')['sun'].to_flux(edges=True)
ept_ion = epd.ept.science.low_latency('mag', 'time')['sun'].to_flux(edges=True)

# calculate mean flux over all bins
data = combine_bins(ept_ion).resample('1H').mean().iloc[1:-1]
data = np.log10(data)  # use logarithmic data
data[np.isinf(data)] = np.nan
data -= data.resample('3H').mean().min()  # arbitrary shift to get only positive values

data_e = combine_bins(ept_electron).resample('1H').mean().iloc[1:-1]
data_e = np.log10(data_e)  # use logarithmic data
data_e[np.isinf(data_e)] = np.nan
data_e -= data_e.resample('3H').mean().min()  # arbitrary shift to get only positive values

cmap = cm.get_cmap('turbo')

# plot ion and electron data
for data, scale, label in [(data, 0.15, 'ion'), (data_e, -0.15, 'e')]:
    barwidth = date2num(data.index[1]) - date2num(data.index[0])
    norm = Normalize(vmin=data.min(), vmax=data.max())
    transform = PathTranform(x, y, startdate, enddate, scale=scale)

    ax.bar(data.index, data, transform=transform + ax.transData, color=cmap(norm(data)), width=barwidth, zorder=9)

    # add label at start of track
    ha, va = get_textalign((x[0], y[0]), outer=scale > 0)  # proper text alignment on outer and inner side
    ax.text(date2num(data.index[0]) + 7, 0.35, label, transform=transform + ax.transData, ha=ha, va=va)

# add labels at start of track
ax.plot([date2num(data.index[0]), date2num(data.index[0])],
        [-0.5, 0.5],
        transform=transform + ax.transData, color=get_foreground_color(), lw=2, zorder=9)

# add arrows
for date in [dt.datetime(2020, 3, 29), dt.datetime(2020, 5, 27), dt.datetime(2020, 9, 11)]:
    ax.plot([date2num(date - dt.timedelta(days=2)), date2num(date), date2num(date - dt.timedelta(days=2))],
            [-0.2, 0, 0.2], transform=transform + ax.transData, color=get_foreground_color())

# plot grid and date labels
solar_system_grid(ax, angle=angle)
date_labels(ax, startdate, enddate, raiseddates=[
    utc.localize(dt.datetime(2020, 12, 1))
])

plt.axis('equal')
ax.set_ylim([-1.2, 1.2])
ax.set_xlim([-1.55, 1.1])
plt.axis('off')

plt.title(f'Solar Orbiter EPD/EPT energetic particles — {title}', color=get_foreground_color(),
          fontweight=get_title_font())
plt.text(1.05, -1.15, 'Data: Solar Orbiter/EPD/EPT | Plot: J. von Forstner, CAU Kiel',
         ha='right', va='bottom', size='x-small')

plt.savefig('ept_orbit_plot.pdf', bbox_inches='tight')
plt.savefig('ept_orbit_plot.png', dpi=300, bbox_inches='tight')
plt.show()