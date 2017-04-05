from matplotlib import colors, cm, patches, pyplot
import numpy as np
import math

COLORS = ['#328BD5', '#404B5A', '#3EB642', '#E04341', '#8665D0']


class ColorMap(object):
    """
    Maps arrays to colors
    """
    class LinearSegments(object):
        black_to_blue_dict = {
            'red': ((0.0, 0.0, 0.0),
                    (1.0, 0.0, 0.0)),
            'blue': ((0.0, 0.0, 0.0),
                     (1.0, 1.0, 0.0)),
            'green': ((0.0, 0.0, 0.0),
                      (1.0, 0.0, 0.0))}

        black_to_green_dict = {
            'red': ((0.0, 0.0, 0.0),
                    (1.0, 0.0, 0.0)),
            'blue': ((0.0, 0.0, 0.0),
                     (1.0, 0.0, 0.0)),
            'green': ((0.0, 0.0, 0.0),
                      (1.0, 1.0, 0.0))}

        red_to_green_dict = {
                'red': ((0.0, 1.0, 1.0),
                         (1.0, 0.0, 0.0)),
                 'blue': ((0.0, 0.0, 0.0),
                          (1.0, 0.0, 0.0)),
                 'green': ((0.0, 0.0, 0.0),
                           (1.0, 1.0, 0.0))}

    red_to_green = colors.LinearSegmentedColormap('my_colormap', LinearSegments.red_to_green_dict, 100)
    black_to_blue = colors.LinearSegmentedColormap('my_colormap', LinearSegments.black_to_blue_dict, 100)
    black_to_green = colors.LinearSegmentedColormap('my_colormap', LinearSegments.black_to_green_dict, 100)


    def array_1d_to_color_scale(self,array_1d, colormap):
        mmin, mmax = min(array_1d), max(array_1d)
        norm = colors.Normalize(mmin, mmax)
        scalarMapx = cm.ScalarMappable(norm=norm, cmap=colormap)
        scalarMapx.set_array(array_1d)
        return scalarMapx.to_rgba(array_1d)

def coordinate_gradients_to_1d_colorscale(dx, dy,
                                          x_buffer_prop=.1, y_buffer_prop=.1,
                                          norm='separate'):
    """
    Map x and y gradients to single array of colors based on 2D color scale

    Parameters
    ----------
    dx: array type
        x component of gradient
    dy: array type
        y component of gradient
    x_buffer_prop:
    y_buffer_prop:
    norm: string
        whether to normalize colors based on differences in x and y scales.
        if separate, each component gets its own scaling (default)
        if global, will scale based on global extrema

    Returns
    ----------
    color_array, xmin, xmax, ymin, ymax
    """
    xmin, xmax, xbuffer = build_buffer(dx)
    ymin, ymax, ybuffer = build_buffer(dy)
    global_min = min(xmin, ymin)
    global_max = max(xmax, ymax)
    if norm == 'separate':
        normx = colors.Normalize(xmin, xmax)
        normy = colors.Normalize(ymin, ymax)
    elif norm == 'shared':
        normx = colors.Normalize(global_min, global_max)
        normy = colors.Normalize(global_min, global_max)
    else:
        raise KeyError("keyword norm must be in ('separate', 'shared')")

    scalarMapx = cm.ScalarMappable(norm=normx, cmap=ColorMap.black_to_blue)
    scalarMapy = cm.ScalarMappable(norm=normy, cmap=ColorMap.black_to_green)

    scalarMapx.set_array(dx)
    scalarMapy.set_array(dy)

    colorx = scalarMapx.to_rgba(dx)
    colory = scalarMapy.to_rgba(dy)

    color = np.array(colorx) + np.array(colory)
    color[:, :, 3] = 1.
    return color, xmin+xbuffer, xmax-xbuffer, ymin+ybuffer, ymax-ybuffer

def plot_2d_color_scale(x1_min, x1_max, x2_min, x2_max, plot_point=None,
                        resolution=10, ax=None):
    """
    Return a generic plot of a 2D color scale

    Parameters
    ----------
    x1_min: numeric
        how high x1 should extend the color scale
    x1_max:  numeric
        how high 2 should extend the color scale
    x2_min:  numeric
        how low x2 should extend the color scale
    x2_max: numeric
        how high x2 should extend the color scale
    resolution: int
        how fine grain to make the color scale
    ax: matplotlib.axes._subplots.AxesSubplot
        matplotlib axis to plot on. if none will generate a new one

    Returns
    ----------
    matplotlib.axes._subplots.AxesSubplot
    """
    ax.set_xlim(x1_min, x1_max)
    ax.set_ylim(x2_min, x2_max)
    x1 = np.linspace(x1_min, x1_max, resolution+1)
    x2 = np.linspace(x2_min, x2_max, resolution+1)
    x1_diff = x1[1] - x1[0]
    x2_diff = x2[1] - x2[0]
    x1, x2 = np.meshgrid(x1, x2)
    colors_for_scale, a, b, c, d = coordinate_gradients_to_1d_colorscale(x1, x2)

    if ax is None:
        f, ax = pyplot.subplots(1)
    for i in range(resolution):
        for j in range(resolution):
            xy = (x1[i,j], x2[i,j])
            color = colors_for_scale[i, j]
            rect = patches.Rectangle(
                xy, x1_diff, x2_diff,
                alpha=.8, facecolor=color,zorder=1
            )
            ax.add_patch(rect)
    if plot_point:
        ax.scatter([plot_point[0]], [plot_point[1]], s=75.
                   , color='yellow', alpha=1, zorder=2)
    return ax

def build_buffer(x, buffer_prop=.1):
    xmin, xmax = min(0, np.percentile(x, 3)), max(np.percentile(x, 97), 0)
    buffer = (xmax - xmin) * buffer_prop / 2.
    xmin, xmax = xmin - buffer, xmax + buffer
    return xmin, xmax, buffer
