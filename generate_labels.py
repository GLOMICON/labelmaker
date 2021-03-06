#!/usr/bin/env python

import click
import os
import numpy as np
import pandas as pd
import qrcode
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 

template_head = 'labelsheet_template_LCRY1700_head.tex'
template_tail = 'labelsheet_template_LCRY1700_tail.tex'
template_cols = 5

def create_directory(project):

    # create directory for project labels
    newdir = 'labels_%s' % project
    if not os.path.exists(newdir):
        os.makedirs(newdir)

def make_label(project, contact, sample_type, date, sample, replicate, label_width, label_height):

    # generate text code and qr code
    # longcode = '%s_%s_%s_%s_%s_r%01d' % (project, contact, sample_type, date, sample, replicate)
    code = '%s_%s_r%01d' % (project, sample, replicate)
    string = 'Project:%s\nContact:%s\nType:%s\nDate:%s\nSampleID:%s\nReplicate:r%01d' % (
        project, contact, sample_type, date, sample, replicate)

    # make qr code
    qr = qrcode.QRCode(
        #version=1, # set fit=True below to make this automatic
        error_correction=qrcode.constants.ERROR_CORRECT_L, # default is ERROR_CORRECT_M
        box_size=6, # number of pixels per box
        border=20, # larger border yields smaller qr code
    )
    qr.add_data(code)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # make label from qr code and string
    label = Image.new('RGB', (int(img.height*label_width/label_height), img.height), color='white')
    label.paste(img, (0,0))
    draw = ImageDraw.Draw(label)
    font = ImageFont.truetype('Monaco.dfont', 32)
    draw.text(((img.height*0.85), int(img.height*0.18)), string, (0,0,0), font=font)
    label.save('labels_%s/label_%s_r%01d.png' % (project, sample, replicate))

@click.command()
@click.option('--project', '-p', required=True, type=str,
              help="Short project name. Must not contain spaces.")
@click.option('--contact', '-c', required=True, type=str,
              help="Last name of point of contact. Must not contain spaces.")
@click.option('--sample_type', '-t', required=True, type=str,
              help="Type of sample (eg DNA.2um). Must not contain spaces.")
@click.option('--date', '-d', required=True, type=int,
              help="Date as YYMMDD or YYMM.")
@click.option('--sample_list', '-l', required=False, type=click.Path(exists=True),
              help="List of samples. If none is provided, samples will be numbered 1 to num_samples.")
@click.option('--num_samples', '-s', required=False, type=int, default=5,
              help="Number of unique samples. [default=5]")
@click.option('--num_replicates', '-r', required=False, type=int, default=1,
              help="Number of replicates per sample. [default=1]")
@click.option('--label_width', '-w', required=False, type=float, default=1.05,
              help="Width of label in inches. 1.05 works for 1.28in labels. [default=1.05]")
@click.option('--label_height', '-h', required=False, type=float, default=0.5,
              help="Height of label in inches. 0.5 works for 0.5in labels. [default=0.05]")

def main(project, contact, sample_type, date, sample_list, num_samples, num_replicates, label_width, label_height):

    create_directory(project)

    # read sample list or number from 1 to num_samples
    if (sample_list):
        with open(sample_list, 'r') as f:
            samples = [line.rstrip() for line in f.readlines()]
    else:
        samples = np.arange(num_samples)+1

    # make labels and latex table, iterating over sample numbers and replicates
    tex_table = ''
    tex_counter = 0
    for sample in samples:
        for replicate in np.arange(num_replicates)+1:
            make_label(project, contact, sample_type, date, sample, replicate, label_width, label_height)
            tex_table += '\\includegraphics[width=\\w]{label_%s_r1} & ' % sample
            tex_counter += 1
            if ((tex_counter % template_cols) == 0):
                tex_table = tex_table[:-2]
                tex_table += '\\\\\n'

    # make labelsheet latex file
    with open(template_head, 'r') as f:
        head = f.read()
    with open(template_tail, 'r') as f:
        tail = f.read()
    with open(f'labels_{project}/labelsheet_{project}_LCRY1700.tex', 'w') as t:
        t.write(head)
        t.write(tex_table) 
        t.write(tail)

if __name__ == "__main__":
    main()
