from etspice import SOLO
from matplotlib.patches import Circle
from scipy.constants import au
import datetime as dt
import numpy as np

from utils.style import get_foreground_color, get_secondary_color, get_sun_colors


def date_labels(ax, startdate, enddate, raiseddates=None):
    """
    adds date labels at the start of each month

    :param ax: axes to plot on
    :param startdate: starting date
    :param enddate: ending date
    :param raiseddates: dates where the label should be raised a bit more
    """

    labeldates = [(startdate.replace(day=1) + dt.timedelta(days=32)).replace(day=1)]
    while labeldates[-1] < enddate:
        labeldates.append((labeldates[-1].replace(day=1) + dt.timedelta(days=32)).replace(day=1))
    del labeldates[-1]

    firststart = False
    if startdate.day == 1:
        firststart = True
        labeldates.insert(0, startdate)

    for i, date in enumerate(labeldates):
        pos = SOLO.position(date) / au * 1e3

        longi = np.arctan2(pos[1], pos[0])
        ha = 'left' if np.cos(longi) > 0.2 else 'center' if np.cos(longi) > -0.2 else 'right'
        va = 'bottom' if np.sin(longi) > 0.2 else 'center' if np.sin(longi) > -0.2 else 'top'

        f = 1.15
        if raiseddates is not None and date in raiseddates:
            f = 1.4
        ax.text(pos[0] * f, pos[1] * f, '{:%d %b %Y}'.format(date), ha=ha, va=va, fontweight='bold')

        if not (i == 0 and firststart):
            ax.scatter(pos[0], pos[1], facecolor=get_foreground_color(), s=40, zorder=10)


def solar_system_grid(ax):
    """
    Plots the position of the Sun and concentric circular grid lines for 0.2-1 AU

    :param ax: axes to plot on
    """

    # plot position of the Sun
    face, edge = get_sun_colors()
    ax.scatter(0, 0, facecolor=face, edgecolor=edge, s=300)

    # plot grid lines
    for radius in np.arange(0.2, 1.2, 0.2):
        circle = Circle((0, 0), radius, color=get_secondary_color(), linestyle=(0, (5, 5)), fill=False, alpha=0.5,
                        linewidth=0.5)
        ax.add_artist(circle)
        # labels
        angle = 56
        ax.text(- radius * np.cos(np.radians(angle)),
                radius * np.sin(np.radians(angle)),
                '{:.1f} AU'.format(radius),
                color=get_secondary_color(), size='small', rotation_mode='anchor',
                rotation=-angle + 90, ha='center', va='bottom')