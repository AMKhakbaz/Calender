# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '.')
from jalali import j_to_g, jalali_is_leap, days_in_jmonth
import datetime

PERSIAN_DIGITS = str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹')
def fa_num(n):
    return str(n).translate(PERSIAN_DIGITS)

MONTH_NAMES = ["فروردین","اردیبهشت","خرداد","تیر","مرداد","شهریور",
               "مهر","آبان","آذر","دی","بهمن","اسفند"]
MONTH_NAMES_EN = ["Farvardin","Ordibehesht","Khordad","Tir","Mordad","Shahrivar",
                  "Mehr","Aban","Azar","Dey","Bahman","Esfand"]
PHOTO_FILES = {
    1:"1-Farvardin.jpg", 2:"2-Ordibehesht.jpg", 3:"3-Khordad.jpg", 4:"4-Tir.jpg",
    5:"5-Mordad.jpg", 6:"6-Shahrivar.jpg", 7:"7-Mehr.jpg", 8:"8-Aban.jpg",
    9:"9-Azar.jpg", 10:"10-Dey.jpg", 11:"11-Bahman.jpg", 12:"12-Esfand.jpg"
}

WEEKDAY_FA = ["شنبه","یک‌شنبه","دوشنبه","سه‌شنبه","چهارشنبه","پنج‌شنبه","جمعه"]  # index 0..6, 0=Saturday

# Holidays: day -> label (تعطیل رسمی)
HOLIDAYS = {
 1: {1:"نوروز و عید سعید فطر", 2:"عید نوروز", 3:"عید نوروز", 4:"عید نوروز",
     12:"روز جمهوری اسلامی ایران", 13:"روز طبیعت (سیزده‌به‌در)",
     25:"شهادت امام جعفر صادق (ع)"},
 2: {},
 3: {6:"عید سعید قربان", 14:"عید غدیر خم و رحلت امام خمینی (ره)", 15:"قیام ۱۵ خرداد"},
 4: {3:"تاسوعای حسینی", 4:"عاشورای حسینی"},
 5: {13:"اربعین حسینی", 21:"رحلت رسول اکرم (ص) و شهادت امام حسن مجتبی (ع)",
     22:"شهادت امام رضا (ع)", 30:"شهادت امام حسن عسکری (ع)"},
 6: {8:"میلاد رسول اکرم (ص) و امام جعفر صادق (ع)"},
 7: {},
 8: {22:"شهادت حضرت فاطمه زهرا (س)"},
 9: {},
 10: {2:"ولادت امام علی (ع) - روز پدر", 16:"مبعث رسول اکرم (ص)"},
 11: {4:"ولادت امام زمان (عج) - نیمه شعبان", 22:"پیروزی انقلاب اسلامی ایران"},
 12: {9:"شهادت امام علی (ع)", 19:"عید سعید فطر", 20:"تعطیل به مناسبت عید فطر",
      29:"ملی‌شدن صنعت نفت ایران"},
}

# Notable non-holiday events/occasions: day -> label
EVENTS = {
 1: {6:"زادروز زرتشت پیامبر", 20:"روز ملی فناوری هسته‌ای", 30:"روز دختران"},
 2: {1:"بزرگداشت سعدی - روز نثر فارسی", 10:"روز ملی خلیج فارس", 12:"روز معلم",
     25:"بزرگداشت فردوسی - روز پاسداشت زبان فارسی"},
 3: {3:"سالروز فتح خرمشهر", 26:"آغاز سال نو قمری"},
 4: {7:"روز قوه قضاییه", 14:"روز قلم", 22:"روز ملی فناوری اطلاعات"},
 5: {14:"سالروز صدور فرمان مشروطیت", 17:"روز خبرنگار", 28:"روز جهانی عکاسی"},
 6: {1:"روز پزشک - بزرگداشت ابوعلی‌سینا", 4:"زادروز کوروش بزرگ - جشن شهریورگان"},
 7: {1:"بازگشایی مدارس"},
 8: {1:"بزرگداشت ابوالفضل بیهقی"},
 9: {1:"روز بیمه", 5:"روز بسیج", 16:"روز دانشجو"},
 10: {13:"سالروز شهادت سردار سلیمانی - روز مقاومت جهانی", 11:"آغاز سال نو میلادی"},
 11: {1:"آغاز دهه مبارک فجر"},
 12: {5:"روز مهندسی", 15:"روز درختکاری", 25:"بزرگداشت پروین اعتصامی"},
}

def month_info(m):
    n = days_in_jmonth(1405, m)
    g_first = j_to_g(1405, m, 1)
    wd_first_name, wd_first = None, None
    d = datetime.date(*g_first)
    py_wd = d.weekday()  # Monday=0..Sunday=6
    # convert to persian week index where Saturday=0
    # python Monday=0,...,Saturday=5,Sunday=6
    # persian: Saturday=0, Sunday=1, Monday=2, Tuesday=3, Wed=4, Thu=5, Fri=6
    map_py_to_fa = {5:0, 6:1, 0:2, 1:3, 2:4, 3:5, 4:6}
    start_idx = map_py_to_fa[py_wd]
    g_last = j_to_g(1405, m, n)
    return n, start_idx, g_first, g_last

if __name__ == "__main__":
    for m in range(1,13):
        n, start_idx, gf, gl = month_info(m)
        print(m, MONTH_NAMES[m-1], "days:",n, "start_idx(0=Sat):", start_idx, "greg range:", gf, gl)

def gregorian_of(m, d):
    return j_to_g(1405, m, d)
