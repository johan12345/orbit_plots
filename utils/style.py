import matplotlib as mpl
import matplotlib.pyplot as plt


def set_style(fig, style):
    if style == 'esa':
        plt.style.use('dark_background')
        mpl.rcParams.update({
            'font.family': 'sans-serif',
            'font.sans-serif': 'NotesEsa',
            'savefig.facecolor': '#003247',
            'savefig.edgecolor': '#003247',
        })
        fig.set_facecolor('#003247')
        fig.set_edgecolor('#003247')
    elif style == 'plain':
        mpl.rcParams.update(mpl.rcParamsDefault)
    else:
        raise ValueError(f'unknown style: {style}')


def get_foreground_color():
    if mpl.rcParams['lines.color'] == 'white':
        return 'white'
    else:
        return 'black'


def get_secondary_color():
    if mpl.rcParams['lines.color'] == 'white':
        return 'white'
    else:
        return 'gray'


def get_sun_colors():
    if mpl.rcParams['lines.color'] == 'white':
        return '#fffd7a', '#ffffba'
    else:
        return '#ffff00', 'k'


def get_datelabel_font():
    if mpl.rcParams['lines.color'] == 'white':
        return 'bold'
    else:
        return 'regular'


def get_title_font():
    if mpl.rcParams['lines.color'] == 'white':
        return 'regular'
    else:
        return 'bold'
