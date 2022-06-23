#!/usr/bin/python
import argparse
import math
from pathlib import Path

import svgwrite


# LICENSE
#
# Written 2022 by Christian Vogel <vogelchr@vogel.cx>.
# To the extent possible under law, I, the author, waive all copyright and related or
# neighboring rights to this program. This work is publiched from Germany.

def add_vect(*vects):
    return tuple(map(sum, zip(*vects)))


def mult_vect(factor, vect):
    return tuple([factor * v for v in vect])


def xy_angle_r(angle, r):
    xy_norm = (math.sin(angle * math.pi / 180), -math.cos(angle * math.pi / 180))
    v = mult_vect(r, xy_norm)
    return v


parser = argparse.ArgumentParser()
parser.add_argument('-R', '--outer-radius', metavar='mm',
                    default=30.0, help='Outer radius [%(default).1f mm]')
parser.add_argument('-r', '--inner-radius', metavar='mm',
                    default=20.0, help='Inner radius [%(default).1f mm]')
parser.add_argument('-y', '--start-year', default=20, type=int, metavar='YEAR',
                    help='Start year.')
parser.add_argument('-Y', '--year-inverse', action='store_true',
                    help='Print the year light on dark.')
parser.add_argument('-t', '--center-text', help='Center Text')

parser.add_argument('svgfile', type=Path)
args = parser.parse_args()

# width of document in mm, we add 5mm around to account for thickness of lines etc...
whalf = args.outer_radius + 5.0
w = whalf * 2.0

dwg = svgwrite.Drawing(args.svgfile, size=[f'{w}mm', f'{w}mm'])
dwg.viewbox(-whalf, -whalf, w, w)

lineattrs = {'fill': 'none', 'stroke': 'rgb(0,0,0)', 'stroke_width': 0.15}

# draw outer circle
dwg.add(
    dwg.circle(center=(0.0, 0.0), r=args.outer_radius, **lineattrs)
)

n_spokes = 18

# if the year is inverse, draw the black arc below, over which the
# year letters will be placed
if args.year_inverse:
    a = xy_angle_r(360.0 * 6 / 18, args.inner_radius)
    b = xy_angle_r(360.0 * 6 / 18, args.outer_radius)
    c = xy_angle_r(360.0 * 12 / 18, args.outer_radius)
    d = xy_angle_r(360.0 * 12 / 18, args.inner_radius)

    path = svgwrite.path.Path()
    path.push('M', (a[0], a[1]))
    path.push('L', (b[0], b[1]))
    path.push('A', (args.outer_radius, args.outer_radius, 0, 0, 1, c[0], c[1]))
    path.push('L', (d[0], d[1]))
    path.push('A', (args.inner_radius, args.inner_radius, 0, 0, 0, a[0], a[1]))

    dwg.add(path)

for spoke in range(n_spokes):
    angle_line = 360.0 * spoke / n_spokes
    angle_text = 360.0 * (2 * spoke + 1) / (2 * n_spokes)

    # if the year is inverted, then
    #    we skip the spokes around the years (6..12)
    #    we invert the spokes between the years (7..11)
    attrs = lineattrs.copy()
    if args.year_inverse:
        # skip the spokes between years/months
        if spoke == 6 or spoke == 12:
            attrs = None  # skip
        elif spoke > 6 and spoke < 12:
            attrs['stroke'] = 'rgb(255,255,255)'
        else:
            attrs['stroke'] = 'rgb(0,0,0)'

    if attrs:
        dwg.add(
            dwg.line(start=xy_angle_r(angle_line, args.inner_radius),
                     end=xy_angle_r(angle_line, args.outer_radius),
                     **attrs)
        )

    # Months
    if spoke <= 5 or spoke >= 12:
        # Month string
        if spoke <= 5:
            txt = f'{spoke + 7}'  # Spokes 0..7 => July to December
        else:
            txt = f'{spoke - 11}'  # Spokes 12 .. 17 => January to June
        style = 'font-size:5px; font-family:sans-serif'
        r = 0.6 * args.inner_radius + 0.4 * args.outer_radius
        fill = 'rgb(0, 0, 0)'
        angle_letters = angle_text
    # Years
    else:
        # Year String
        # spokes 11..6 => start_year .. start_year + 6
        txt = f'{11 - spoke + args.start_year}'
        style = 'font-size:5px; font-family:sans-serif; font-weight:bold'

        r = 0.3 * args.inner_radius + 0.7 * args.outer_radius

        if args.year_inverse:
            fill = 'rgb(255, 255, 255)'
        else:
            fill = 'rgb(0, 0, 0)'

        # years are readable "the right way around", so flip by 180deg
        angle_letters = 180.0 + angle_text
        if angle_letters > 360.0:
            angle_letters -= 360.0

    t = dwg.text(txt, style=style, text_anchor='middle', fill=fill)
    t.translate(xy_angle_r(angle_text, r))
    t.rotate(angle_letters)
    dwg.add(t)

if args.center_text:
    dwg.add(dwg.text(args.center_text, style='font-size:5px; font-family:sans-serif; font-weight:bold',
                     text_anchor='middle'))

dwg.save()
