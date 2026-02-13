import numpy


def format_float(number, precision=6):
    if number == 0:
        return "0.0"
    else:
        return numpy.format_float_scientific(number, precision=precision, unique=False)
