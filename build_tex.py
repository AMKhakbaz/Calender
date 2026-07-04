# -*- coding: utf-8 -*-
"""
Generates main.tex for the Solar Hijri (Jalali) 1405 wall calendar.
"""
import sys
from pathlib import Path
from string import Template
sys.path.insert(0, '.')
from jalali import j_to_g
from gen_data import (fa_num, MONTH_NAMES, MONTH_NAMES_EN, PHOTO_FILES,
                       WEEKDAY_FA, HOLIDAYS, EVENTS, month_info)

GREG_MONTHS_EN = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

# Layout and typography live here so main.tex remains a generated artifact.
TEXT_FONT = "FreeSerif"
LATIN_TEXT_FONT = "FreeSerif"
TITLE_FONT = "FreeSerif"
PAGE_MARGIN = "5mm"
PAGE_TOP_MARGIN = "0mm"
HERO_HEIGHT = "11cm"
HERO_TO_GRID_SPACE = "11.2cm"
HERO_BANNER_HEIGHT = "2.15cm"
HERO_SIDE_PADDING = "9mm"
MONTH_GRID_ARRAYSTRETCH = "1.15"
MONTH_GRID_TABCOLSEP = "2pt"
MONTH_GRID_ROW_GAP = "1mm"
FOOTER_TOP_SPACE = "2.2mm"

def rtl(text):
    """Return Persian text for xepersian-managed RTL rendering."""
    return text

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
        rows_tex.append(" & ".join(cells) + rf" \\[{MONTH_GRID_ROW_GAP}]")

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
    event_list = "\n".join(event_items) if event_items else r"{\small\color{gray!60}---}"

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
\vspace{""" + FOOTER_TOP_SPACE + r"""}
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


PREAMBLE = Template(r"""
% این فایل به‌صورت خودکار توسط build_tex.py تولید شده است؛ تغییرات قالب را در همان فایل اعمال کنید.
\documentclass[10pt]{article}
\usepackage{fontspec}
\usepackage{xepersian}
\settextfont{$text_font}
\setlatintextfont{$latin_text_font}
\newfontfamily\titlefont{$title_font}
\usepackage[a4paper,margin=$page_margin,top=$page_top_margin,headheight=0mm]{geometry}
\usepackage{tikz}
\usepackage[table]{xcolor}
\usepackage{graphicx}
\usepackage{tabularx}
\usepackage{array}
\usepackage[most]{tcolorbox}
\usetikzlibrary{calc}

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
  \begin{tikzpicture}[remember picture,overlay]
    \def\heroheight{$hero_height}
    \coordinate (heroNW) at (current page.north west);
    \coordinate (heroNE) at (current page.north east);
    \coordinate (heroSW) at ([yshift=-\heroheight]current page.north west);
    \coordinate (heroSE) at ([yshift=-\heroheight]current page.north east);
    \path[clip] (heroNW) rectangle (heroSE);
    \node[anchor=center,inner sep=0] at ([yshift=-0.5\heroheight]current page.north) {\includegraphics[width=\paperwidth,height=\heroheight,keepaspectratio]{photos/#1}};
    \fill[bannerDark,opacity=0.68] (heroSW) rectangle ([yshift=$hero_banner_height]heroSE);
    \draw[accentGold,line width=0.9pt] ([yshift=$hero_banner_height]heroSW) -- ([yshift=$hero_banner_height]heroSE);
    \node[anchor=south west,text=white,inner sep=0] at ([xshift=$hero_side_padding,yshift=0.68cm]heroSW) {\titlefont\fontsize{36}{40}\selectfont #2};
    \node[anchor=south east,text=accentGold,inner sep=0] at ([xshift=-$hero_side_padding,yshift=0.78cm]heroSE) {\fontsize{12}{14}\selectfont #4};
    \node[anchor=north west,text=accentGold,inner sep=0] at ([xshift=$hero_side_padding,yshift=-5mm]heroNW) {\fontsize{14}{16}\selectfont تقویم سال ۱۴۰۵};
  \end{tikzpicture}%
  \vspace*{$hero_to_grid_space}
}{%
}

\newcommand{\headercell}[1]{\multicolumn{1}{c}{\cellcolor{headerBg}\textcolor{white}{\small #1}}}
\newcommand{\normalcell}[2]{\begin{tabular}{@{}c@{}}\daynumcolor{#1}\\[-0.7mm]{\tiny\color{gray!70}#2}\end{tabular}}
\newcommand{\fridaycell}[2]{\begin{tabular}{@{}c@{}}\textcolor{fridayText}{\bfseries #1}\\[-0.7mm]{\tiny\color{fridayText!70}#2}\end{tabular}}
\newcommand{\holidaycell}[2]{\cellcolor{holidayBg}\begin{tabular}{@{}c@{}}\textcolor{holidayText}{\bfseries #1}\\[-0.7mm]{\tiny\color{holidayText!80}#2}\end{tabular}}
\newcommand{\emptycell}{\phantom{0}}
\newcommand{\daynumcolor}[1]{\textcolor{normalText}{#1}}

\newenvironment{monthgrid}{%
  \renewcommand{\arraystretch}{$month_grid_arraystretch}
  \setlength{\tabcolsep}{$month_grid_tabcolsep}
  \begin{tabularx}{\linewidth}{|*{7}{>{\centering\arraybackslash}X|}}
  \hline
}{%
  \hline
  \end{tabularx}
}

\newcommand{\holidayitem}[1]{{\small\textcolor{holidayText}{\textbullet}\ \textcolor{normalText}{\small #1}}\par\vspace{0.6mm}}
\newcommand{\eventitem}[1]{{\small\textcolor{accentGold}{\textbullet}\ \textcolor{normalText}{\small #1}}\par\vspace{0.6mm}}
\newcommand{\noholidaynote}[1]{{\small\color{gray} این ماه فاقد تعطیلی رسمی است.}}

\begin{document}
""").substitute(
    text_font=TEXT_FONT,
    latin_text_font=LATIN_TEXT_FONT,
    title_font=TITLE_FONT,
    page_margin=PAGE_MARGIN,
    page_top_margin=PAGE_TOP_MARGIN,
    hero_height=HERO_HEIGHT,
    hero_to_grid_space=HERO_TO_GRID_SPACE,
    hero_banner_height=HERO_BANNER_HEIGHT,
    hero_side_padding=HERO_SIDE_PADDING,
    month_grid_arraystretch=MONTH_GRID_ARRAYSTRETCH,
    month_grid_tabcolsep=MONTH_GRID_TABCOLSEP,
)

POSTAMBLE = r"""
\end{document}
"""

def main():
    parts = [PREAMBLE]
    for m in range(1, 13):
        parts.append(build_month_page(m))
    parts.append(POSTAMBLE)
    root = Path(__file__).resolve().parent
    output = root / "main.tex"
    with output.open("w", encoding="utf-8") as f:
        f.write("\n".join(parts))

if __name__ == "__main__":
    main()
    print("done")
