# Jalali <-> Gregorian conversion (standard algorithm)
def is_leap_jalali(jy):
    # 33-year cycle algorithm
    breaks = [ -61, 9, 38, 199, 426, 686, 756, 818, 1111, 1181, 1210,
               1635, 2060, 2097, 2192, 2262, 2324, 2394, 2456, 3178]
    gy = jy + 1595
    leap = -14
    jp = breaks[0]
    for i in range(1, len(breaks)):
        jm = breaks[i]
        jump = jm - jp
        if jy < jm:
            n = jy - jp
            leap = leap + (n // 33) * 8 + ((n % 33) + 3) // 4
            if (jump % 33) == 4 and (jump - n) == 4:
                leap += 1
            break
        leap += (jump // 33) * 8 + (jump % 33) // 4
        jp = jm
    n = 20 + leap - jy  # not used further; use direct method instead
    # Direct simpler well tested implementation below (from common jdatetime impl)
    return None

# Use a well-tested direct implementation instead
def j_to_g(jy, jm, jd):
    d_4 = (jy + 1) % 4
    if d_4 == 0:
        pass
    # Using the classic algorithm from "Calendrical Calculations" / jdatetime source
    jy = jy - 979
    jm = jm - 1
    jd = jd - 1

    j_day_no = 365 * jy + (jy // 33) * 8 + ((jy % 33) + 3) // 4
    for i in range(jm):
        j_day_no += 31 if i < 6 else 30
    j_day_no += jd

    g_day_no = j_day_no + 79

    gy = 1600 + 400 * (g_day_no // 146097)
    g_day_no = g_day_no % 146097

    leap = True
    if g_day_no >= 36525:
        g_day_no -= 1
        gy += 100 * (g_day_no // 36524)
        g_day_no = g_day_no % 36524
        if g_day_no >= 365:
            g_day_no += 1
        else:
            leap = False

    gy += 4 * (g_day_no // 1461)
    g_day_no %= 1461

    if g_day_no >= 366:
        leap = False
        g_day_no -= 1
        gy += g_day_no // 365
        g_day_no = g_day_no % 365

    g_days_in_month = [31, 29 if (gy%4==0 and (gy%100!=0 or gy%400==0)) else 28, 31,30,31,30,31,31,30,31,30,31]
    gm = 0
    while g_day_no >= g_days_in_month[gm]:
        g_day_no -= g_days_in_month[gm]
        gm += 1
    gd = g_day_no + 1
    return gy, gm+1, gd

def jalali_is_leap(jy):
    # remainder-based 33-year cycle rule (accurate enough for our range ~1404-1406)
    r = jy % 33
    leap_remainders = {1,5,9,13,17,22,26,30}
    return r in leap_remainders

def days_in_jmonth(jy, jm):
    if jm <= 6:
        return 31
    if jm <= 11:
        return 30
    return 29 + (1 if jalali_is_leap(jy) else 0)

import datetime
def weekday_name_fa(gy,gm,gd):
    # python weekday: Monday=0 ... Sunday=6
    wd = datetime.date(gy,gm,gd).weekday()
    # Persian week starts Saturday
    names = ["دوشنبه","سه‌شنبه","چهارشنبه","پنجشنبه","جمعه","شنبه","یکشنبه"]
    return names[wd], wd

if __name__ == "__main__":
    # sanity check: 1 Farvardin 1405 should be 2026-03-21 (Saturday)
    print(j_to_g(1405,1,1))
    print(weekday_name_fa(*j_to_g(1405,1,1)))
    print(j_to_g(1405,12,29))
    print(jalali_is_leap(1405), days_in_jmonth(1405,12))
