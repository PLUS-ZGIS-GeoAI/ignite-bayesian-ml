import math


def calculate_ffmc(ffmc0, rhum, temp, prcp, wind):

    if rhum > 100.0:
        rhum = 100.0
    if math.isinf(prcp):
        prcp = 0

    mo = (147.2 * (101.0 - ffmc0)) / (59.5 + ffmc0)
    if prcp > 0.5:
        rf = prcp - 0.5
        if mo > 150.0:
            mo = (mo + 42.5 * rf * math.exp(-100.0 / (251.0 - mo)) * (1.0 -
                  math.exp(-6.93 / rf))) + (.0015 * (mo - 150.0) ** 2) * math.sqrt(rf)
        elif mo <= 150.0:
            mo = mo + 42.5 * rf * \
                math.exp(-100.0 / (251.0 - mo)) * (1.0 - math.exp(-6.93 / rf))
        if mo > 250.0:
            mo = 250.0
    ed = .942 * (rhum ** .679) + (11.0 * math.exp((rhum - 100.0) / 10.0)) + \
        0.18 * (21.1 - temp) * (1.0 - 1.0 / math.exp(.1150 * rhum))
    if mo < ed:
        ew = .618 * (rhum ** .753) + (10.0 * math.exp((rhum - 100.0) / 10.0)
                                      ) + .18 * (21.1 - temp) * (1.0 - 1.0 / math.exp(.115 * rhum))
        if mo <= ew:
            kl = .424 * (1.0 - ((100.0 - rhum) / 100.0) ** 1.7) + (.0694 *
                                                                   math.sqrt(wind)) * (1.0 - ((100.0 - rhum) / 100.0) ** 8)
            kw = kl * (.581 * math.exp(.0365 * temp))
            m = ew - (ew - mo) / 10.0 ** kw
        elif mo > ew:
            m = mo
    elif mo == ed:
        m = mo
    elif mo > ed:
        kl = .424 * (1.0 - (rhum / 100.0) ** 1.7) + (.0694 *
                                                     math.sqrt(wind)) * (1.0 - (rhum / 100.0) ** 8)
        kw = kl * (.581 * math.exp(.0365 * temp))
        m = ed + (mo - ed) / 10.0 ** kw
    ffmc = (59.5 * (250.0 - m)) / (147.2 + m)
    if ffmc > 101.0:
        ffmc = 101.0
    if ffmc <= 0.0:
        ffmc = 0.0
    return ffmc
