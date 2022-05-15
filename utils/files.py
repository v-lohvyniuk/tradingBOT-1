import datetime


def get_dated_filename(name):
    return name + "_" + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + ".txt"


def create_file(name):
    f = open(name, "a+")
    return f


def append_to_file(filename, text):
    f = open(filename, "a+")
    f.write(text + "\n")
    f.close()


def append_log(filename, text):
    f = open(filename, "a+")
    f.write(datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + "    " + text + "\n")
    f.close()
