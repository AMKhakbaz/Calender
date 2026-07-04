# -*- coding: utf-8 -*-
"""
Generates main.tex for the Solar Hijri (Jalali) 1405 wall calendar.
"""
import sys, datetime
sys.path.insert(0, '.')
from jalali import j_to_g, days_in_jmonth
from gen_data import (fa_num, MONTH_NAMES, MONTH_NAMES_EN, PHOTO_FILES,
                       WEEKDAY_FA, HOLIDAYS, EVENTS, month_info)

GREG_MONTHS_FA_ABBR = ["مارس","آوریل","مه","ژوئن","ژوئیه","اوت",
                       "سپتامبر","اکتبر","نوامبر","دسامبر","ژانویه","فوریه"]
GREG_MONTHS_EN = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

def rtl(text):
    """Wrap a Persian phrase for correct bidi rendering."""
    return r"\beginR " + text + r"\endR "

def greg_range_str(gf, gl):
    def fmt(g):
        y, m, d = g
        return f"{d} {GREG_MONTHS_EN[m-1]} {y}"
    return f"{fmt(gf)} \\textendash\\ {fmt(gl)}"

def build_month_page(m):
    name_fa = MONTH_NAMES[m-1]
    photo = PHOTO_FILES[m]
    n_days, start_idx, gf, gl = month_info(m)
    holidays = HOLIDAYS.get(m, {})
    events = EVENTS.get(m, {})

    # Build grid: columns are Fri,Thu,Wed,Tue,Mon,Sun,Sat (left->right) so Saturday ends on the right (RTL week)
    # our weekday index: 0=Sat,1=Sun,2=Mon,3=Tue,4=Wed,5=Thu,6=Fri
    col_order = [6,5,4,3,2,1,0]  # left to right column content = index into WEEKDAY_FA
    header_cells = []
    for idx in col_order:
        header_cells.append(r"\headercell{" + rtl(WEEKDAY_FA[idx]) + "}")
    header_row = " & ".join(header_cells) + r" \\ \hline"

    # Build day->column position matrix
    total_slots = start_idx + n_days
    n_rows = (total_slots + 6) // 7
    grid = [["" for _ in range(7)] for _ in range(n_rows)]
    day = 1
    for slot in range(total_slots):
        row = slot // 7
        col_fa_idx = slot % 7  # 0=Sat ... 6=Fri (position within a Sat-first week)
        if slot < start_idx:
            continue
        grid[row][col_fa_idx] = day
        day += 1

    rows_tex = []
    for row in grid:
        cells = []
        for idx in col_order:  # idx is the Sat..Fri index, but col visual order left->right = Fri..Sat
            val = row[idx]
            if val == "":
                cells.append(r"\emptycell{}")
            else:
                is_friday = (idx == 6)
                is_holiday = val in holidays
                gday = j_to_g(1405, m, val)
                gd_str = f"{gday[2]}"
                if is_holiday:
                    cells.append(r"\holidaycell{" + fa_num(val) + "}{" + gd_str + "}")
                elif is_friday:
                    cells.append(r"\fridaycell{" + fa_num(val) + "}{" + gd_str + "}")
                else:
                    cells.append(r"\normalcell{" + fa_num(val) + "}{" + gd_str + "}")
        rows_tex.append(" & ".join(cells) + r" \\[1mm]")

    grid_body = "\n".join(rows_tex)

    # Footer: holidays + events list, two short columns
    def entries_sorted(d):
        return sorted(d.items(), key=lambda kv: kv[0])

    holiday_items = []
    for dday, label in entries_sorted(holidays):
        full = f"{fa_num(dday)} {name_fa} \u2014 {label}"
        holiday_items.append(r"\holidayitem{" + rtl(full) + "}")
    event_items = []
    for dday, label in entries_sorted(events):
        full = f"{fa_num(dday)} {name_fa} \u2014 {label}"
        event_items.append(r"\eventitem{" + rtl(full) + "}")

    holiday_list = "\n".join(holiday_items) if holiday_items else (r"\noholidaynote{}")
    event_list = "\n".join(event_items) if event_items else r"{\small\color{gray!60}\beginR ---\endR}"

    greg_range = greg_range_str(gf, gl)

    page = r"""
%%============================================================
%% """ + MONTH_NAMES_EN[m-1] + r"""
%%============================================================
\begin{calendarpage}{""" + photo + r"""}{""" + rtl(name_fa) + r"""}{""" + fa_num(m) + r"""}{""" + greg_range + r"""}
\begin{monthgrid}
""" + header_row + r"""
""" + grid_body + r"""
\end{monthgrid}
\vspace{2.2mm}
\begin{tcolorbox}[colback=footerBg,colframe=footerBg,boxrule=0pt,arc=2pt,left=3mm,right=3mm,top=2mm,bottom=2mm,width=\linewidth]
\begin{minipage}[t]{0.48\linewidth}
{\small\bfseries\color{holidayText}""" + rtl("تعطیلات رسمی") + r"""}\par\vspace{1mm}
""" + holiday_list + r"""
\end{minipage}\hfill
\begin{minipage}[t]{0.48\linewidth}
{\small\bfseries\color{accentGold}""" + rtl("رویدادها و مناسبت‌ها") + r"""}\par\vspace{1mm}
""" + event_list + r"""
\end{minipage}
\end{tcolorbox}
\end{calendarpage}
"""
    return page


PREAMBLE = r"""
\documentclass[10pt]{article}
\usepackage{fontspec}
\usepackage[a4paper,margin=9mm,top=0mm,headheight=0mm]{geometry}
\usepackage{tikz}
\usepackage[table]{xcolor}
\usepackage{graphicx}
\usepackage{tabularx}
\usepackage{array}
\usepackage[most]{tcolorbox}
\usetikzlibrary{calc}

\setmainfont{FreeSerif}
\newfontfamily\titlefont{FreeSerif}
\TeXXeTstate=1

\definecolor{holidayBg}{RGB}{255,214,222}
\definecolor{holidayText}{RGB}{176,32,60}
\definecolor{fridayText}{RGB}{198,60,80}
\definecolor{normalText}{RGB}{45,45,50}
\definecolor{gridLine}{RGB}{225,225,228}
\definecolor{bannerDark}{RGB}{20,22,30}
\definecolor{accentGold}{RGB}{182,148,84}
\definecolor{footerBg}{RGB}{247,246,243}
\definecolor{headerBg}{RGB}{35,38,48}

\pagestyle{empty}
\setlength{\parindent}{0pt}

% ---------- Calendar page environment ----------
% #1 photo filename  #2 persian month name (rtl-wrapped)  #3 persian numeral of month  #4 gregorian range
\newenvironment{calendarpage}[4]{%
  \clearpage
  \noindent
  \begin{tikzpicture}[remember picture]
    \useasboundingbox (0,0) rectangle (\linewidth,7.6cm);
    \clip (0,0) rectangle (\linewidth,7.6cm);
    \node[anchor=center,inner sep=0] at ($(\linewidth/2,3.8cm)$) {\includegraphics[width=\linewidth]{photos/#1}};
    \fill[bannerDark,opacity=0.68] (0,0) rectangle (\linewidth,1.85cm);
    \draw[accentGold,line width=0.9pt] (0,1.85cm) -- (\linewidth,1.85cm);
    \node[anchor=south west,text=white,inner sep=0] at (0.35cm,0.55cm) {\titlefont\fontsize{30}{34}\selectfont #2};
    \node[anchor=south east,text=accentGold,inner sep=0] at ($(\linewidth-0.35cm,0.62cm)$) {\fontsize{11}{13}\selectfont #4};
    \node[anchor=north west,text=accentGold,inner sep=0] at (0.35cm,7.35cm) {\fontsize{13}{15}\selectfont \beginR تقویم سال ۱۴۰۵\endR};
  \end{tikzpicture}\\[2mm]
}{%
}

\newcommand{\headercell}[1]{\multicolumn{1}{c}{\cellcolor{headerBg}\textcolor{white}{\small #1}}}
\newcommand{\normalcell}[2]{\begin{tabular}{@{}c@{}}\daynumcolor{#1}\\[-0.7mm]{\tiny\color{gray!70}#2}\end{tabular}}
\newcommand{\fridaycell}[2]{\begin{tabular}{@{}c@{}}\textcolor{fridayText}{\bfseries #1}\\[-0.7mm]{\tiny\color{fridayText!70}#2}\end{tabular}}
\newcommand{\holidaycell}[2]{\cellcolor{holidayBg}\begin{tabular}{@{}c@{}}\textcolor{holidayText}{\bfseries #1}\\[-0.7mm]{\tiny\color{holidayText!80}#2}\end{tabular}}
\newcommand{\emptycell}{\phantom{0}}
\newcommand{\daynumcolor}[1]{\textcolor{normalText}{#1}}

\newenvironment{monthgrid}{%
  \renewcommand{\arraystretch}{1.15}
  \setlength{\tabcolsep}{2pt}
  \begin{tabular}{|*{7}{>{\centering\arraybackslash}p{2.52cm}|}}
  \hline
}{%
  \hline
  \end{tabular}
}

\newcommand{\holidayitem}[1]{{\small\textcolor{holidayText}{\textbullet}\ \textcolor{normalText}{\small #1}}\par\vspace{0.6mm}}
\newcommand{\eventitem}[1]{{\small\textcolor{accentGold}{\textbullet}\ \textcolor{normalText}{\small #1}}\par\vspace{0.6mm}}
\newcommand{\noholidaynote}[1]{{\small\color{gray} }\beginR این ماه فاقد تعطیلی رسمی است.\endR }

\begin{document}
"""

POSTAMBLE = r"""
\end{document}
"""

def main():
    parts = [PREAMBLE]
    for m in range(1, 13):
        parts.append(build_month_page(m))
    parts.append(POSTAMBLE)
    with open('/home/claude/work/calendar1405/main.tex', 'w', encoding='utf-8') as f:
        f.write("\n".join(parts))

if __name__ == "__main__":
    main()
    print("done")
