import matplotlib.pyplot as plt


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
