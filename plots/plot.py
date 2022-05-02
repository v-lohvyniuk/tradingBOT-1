import matplotlib.pyplot as plt


def __annotate__(plot, coords, text, color):
    plot.annotate(
        text,
        xy=coords, xycoords='data',
        xytext=(-40, 30), textcoords='offset points',
        bbox=dict(boxstyle="round", fc="0.9", color=color),
        arrowprops=dict(arrowstyle="->",
                        connectionstyle="angle,angleA=0,angleB=90,rad=20"))


def build_plot(x_axis, y_axis, xlabel="X", ylabel="Y", title="Title"):
    plt.plot(x_axis, y_axis)

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)

    plt.show()


def build_2plots(x_axis, y_axis, x2_axis, y2_axis, xlabel="X", ylabel="Y", title="Title"):
    fig, (sub1, sub2) = plt.subplots(2, gridspec_kw={'height_ratios': [3, 1]})
    sub1.plot(x_axis, y_axis)
    sub2.plot(x2_axis, y2_axis)

    sub2.hlines(y=30.0, xmin=x2_axis[0], xmax=x2_axis[-1], linewidth=1, color='r', linestyles='dashed')
    sub2.hlines(y=70.0, xmin=x2_axis[0], xmax=x2_axis[-1], linewidth=1, color='r', linestyles='dashed')

    plt.subplots_adjust(hspace=.0)
    plt.show()


def build_2plots_with_buy_sell_markers(x_axis, y_axis, x2_axis, y2_axis, buy_markers, sell_markers, xlabel="X",
                                       ylabel="Y", title="Title"):
    fig, (sub1, sub2) = plt.subplots(2, sharex=True, gridspec_kw={'height_ratios': [3, 1]})
    sub1.plot(x_axis, y_axis)

    for x, y in buy_markers:
        __annotate__(sub1, (x, y), "BUY", color='green')

    for x, y in sell_markers:
        __annotate__(sub1, (x, y), "SELL", color='red')

    sub2.plot(x2_axis, y2_axis)

    sub2.hlines(y=30.0, xmin=x2_axis[0], xmax=x2_axis[-1], linewidth=1, color='r', linestyles='dashed')
    sub2.hlines(y=70.0, xmin=x2_axis[0], xmax=x2_axis[-1], linewidth=1, color='r', linestyles='dashed')

    plt.subplots_adjust(hspace=.0)
    plt.show()
    pass
