import datetime as dt

import matplotlib.pyplot as plt
import numpy as np
from etspice import SOLO
from matplotlib.dates import date2num
from pytz import utc
from scipy.constants import au
from solo_loader.mag import MAGData

from utils.labeling import date_labels, solar_system_grid
from utils.path_transform import PathTranform
from utils.style import set_style, get_foreground_color

fig, ax = plt.subplots(figsize=(6.5, 5.5))
set_style(fig, 'esa')

startdate = utc.localize(dt.datetime(2020, 6, 1))
enddate = utc.localize(dt.datetime(2020, 12, 10))

dates = np.array([startdate + dt.timedelta(seconds=i) for i in np.linspace(0, (enddate - startdate).total_seconds(), 5000)])
trajectory = SOLO.position(dates)
x = trajectory[:, 0] / au * 1e3
y = trajectory[:, 1] / au * 1e3

# plot orbit
ax.plot(x, y, color=get_foreground_color(), linewidth=1, zorder=10)

# load and prepare MAG data
mag = MAGData(startdate, enddate).best_available('rtn', False)
mag = mag.resample('5H').mean().iloc[1:-1]
# TODO: for some reason, time resolution higher than 5H does not work
b_tot = np.sqrt((mag ** 2).sum(axis=1))
mag.insert(0, '|B|', b_tot)

# plot MAG data
transform = PathTranform(x, y, startdate, enddate, scale=0.01)
for component in mag:
    ax.plot(mag.index, mag[component], transform=transform + ax.transData, zorder=9, linewidth=0.5)

# add labels at start of track
transform = PathTranform(x, y, startdate, enddate, scale=0.15)
ax.plot([date2num(mag.index[0]), date2num(mag.index[0])],
        [-0.5, 0.5],
        transform=transform + ax.transData, color=get_foreground_color(), lw=2, zorder=9)

# add arrows
for date in [dt.datetime(2020, 9, 13)]:
    ax.plot([date2num(date - dt.timedelta(days=2)), date2num(date), date2num(date - dt.timedelta(days=2))],
            [-0.2, 0, 0.2], transform=transform + ax.transData, color=get_foreground_color())

# plot grid and date labels
solar_system_grid(ax)
date_labels(ax, startdate, enddate, distance=1.2)

plt.axis('equal')
ax.set_ylim([-1.2, 1.2])
ax.set_xlim([-1.55, 1.1])
plt.axis('off')

plt.title('Solar Orbiter MAG magnetic field — first orbit', color=get_foreground_color())
plt.text(1.05, -1.15, 'Data: Solar Orbiter/MAG (ESA & NASA) | Plot: Johan von Forstner, CAU Kiel',
         ha='right', va='bottom', size='x-small')

plt.savefig('mag_orbit_plot.pdf', bbox_inches='tight')
plt.savefig('mag_orbit_plot.png', dpi=300, bbox_inches='tight')
plt.show()