import pandas as pd

"""
Pandas is an open-source Python Library providing high-performance data manipulation and analysis tool using its powerful data structures. The name Pandas is derived from the word Panel Data – an Econometrics from Multidimensional data.
Key features:

-Fast and efficient DataFrame object with default and customized indexing.
-Tools for loading data into in-memory data objects from different file formats.
-Data alignment and integrated handling of missing data.
-Reshaping and pivoting of date sets.
-Label-based slicing, indexing and subsetting of large data sets.
-Columns from a data structure can be deleted or inserted.
-Group by data for aggregation and transformations.
-High performance merging and joining of data.
-Time Series functionality.

"""


import codecs
import os
import sys

df = pd.read_csv('file_signatures.csv')

num_of_extensions = df.shape[0]

description = df['Description']

extension = []
for ext in df['Extension']:
    extension.append(ext.lower().replace(' ', ''))

header = []
for sign in df['Header']:
    header.append(sign.lower().replace(' ', ''))

footer = []
for foot in df['Footer']:
    if str(foot) == 'nan':
        footer.append('')
    else:
        footer.append(foot)

offset = df['Offset']

folder = df['Folder']

recovered_files_directory = ''
dd_image_name = ''
files_count = []


def make_recovery_directory(directory):
    global files_count
    global recovered_files_directory
    recovered_files_directory = directory
    if os.path.isdir(recovered_files_directory):
        print('The specified directory already exists. Create a new one.')
        exit()
    os.makedirs(recovered_files_directory)
    files_count = {}
    for fold in folder:
        if not os.path.isdir(os.path.join(recovered_files_directory, fold)):
            os.makedirs(os.path.join(recovered_files_directory, fold))
            files_count[fold] = 1


def find_header(data):
    data = data[0:20]
    found_signatures = []
    for i in range(num_of_extensions):
        if data.find(header[i]) > -1:
            print('Found file header: {}, extension: {}, offset: {}'.format(header[i], extension[i], offset[i]))
            found_signatures.append(i)
    return(found_signatures)


def find_footer(data):
    if data[-10:] == '0000000000':
        print('recovered the above file')
        return True


def recover_files(dd_image, start_sector, end_sector, signatures_index):
    dd_image.seek(start_sector * 512)
    size = (end_sector - start_sector + 1) * 512
    data = dd_image.read(size)
    for i in signatures_index:
        with open(os.path.join(recovered_files_directory, folder[i], f'{extension[i]}{files_count[folder[i]]}.{extension[i]}'), 'wb') as f:
            files_count[folder[i]] += 1
            f.write(data)



def scan():
    global dd_image
    with open(dd_image_name, 'rb') as dd_image:
        num_of_sectors = 0
        previous_found_signatures_index = []

        while True:

            dd_image.seek(num_of_sectors * 512)
            dd_image_contents = dd_image.read(512)
            dd_image_contents = codecs.encode(dd_image_contents, "hex_codec")
            raw_bytes = dd_image_contents.decode("utf-8")

            if not raw_bytes:
                print('Scanned {} kilobytes'.format((num_of_sectors * 512) / 1024))
                # plot_zeros()
                break

            found_signatures_index = find_header(raw_bytes)
            if found_signatures_index:
                if previous_found_signatures_index:
                    recover_files(dd_image, found_signatures_at_sector, num_of_sectors - 1, previous_found_signatures_index)

                previous_found_signatures_index = found_signatures_index
                found_signatures_at_sector = num_of_sectors

            elif previous_found_signatures_index:
                if find_footer(raw_bytes):
                    recover_files(dd_image, found_signatures_at_sector, num_of_sectors, previous_found_signatures_index)
                    previous_found_signatures_index = []

            num_of_sectors += 1


def main(drive, save):
    global dd_image_name
    dd_image_name = drive
    make_recovery_directory(save)
    scan()


# if __name__ == '__main__':
#     main(drive, save)
