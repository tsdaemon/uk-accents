import os
import requests
from tqdm import tqdm
import sqlite3
import re


vowel_regex = re.compile('[АЕЄИІЇОУЮЯаеєиіїоуюя]')


def download(url, dirpath):
    filename = url.split('/')[-1]
    filepath = os.path.join(dirpath, filename)
    try:
        u = requests.get(url)
    except:
        print("URL %s failed to open" %url)
        raise Exception
    try:
        f = open(filepath, 'wb')
    except:
        print("Cannot write %s" %filepath)
        raise Exception

    downloaded = 0
    for buf in tqdm(u.iter_content(100000)):
        if not buf:
            break
        downloaded += len(buf)
        f.write(buf)
    f.close()
    return filepath


def generate_accents_for_normal_words(conn, f):
    query = 'SELECT COUNT(*) ' + \
            'FROM (SELECT DISTINCT n.reestr, f.flex, instr(n.reestr, \'"\')-2 AS accent_position FROM nom AS n ' + \
            'LEFT JOIN flexes AS f ON f.type = n.type ' + \
            'WHERE n.accent = 0 AND accent_position != -2)'
    count = next(conn.execute(query))[0]

    query = 'SELECT DISTINCT ' + \
            'CASE ' + \
            'WHEN f.flex IS NOT NULL THEN substr(replace(n.reestr, \'"\', \'\'), 1, length(replace(n.reestr, \'"\', \'\'))-i.indent) || f.flex ' + \
            'ELSE n.reestr ' + \
            'END, ' + \
            'instr(n.reestr, \'"\')-2 AS accent_position ' + \
            'FROM nom AS n ' + \
            'INNER JOIN indents AS i ON i.type = n.type ' + \
            'LEFT JOIN flexes AS f ON f.type = n.type ' + \
            'WHERE n.accent = 0 AND accent_position != -2'
    for word, accent_position in tqdm(conn.execute(query), total=count):
        word = word.replace('"', '').replace('%', '').replace('*', '').replace('^', '').replace(
            'empty_', '')
        f.write('{} {}\n'.format(word, accent_position))

    return count


def generate_accents_for_single_vowel_words(conn, f):
    query = 'SELECT COUNT(*) ' + \
            'FROM (SELECT DISTINCT n.reestr, f.flex, instr(n.reestr, \'"\')-2 AS accent_position FROM nom AS n ' + \
            'LEFT JOIN flexes AS f ON f.type = n.type ' + \
            'WHERE n.accent = 0 AND accent_position = -2)'
    count = next(conn.execute(query))[0]

    query = 'SELECT DISTINCT ' + \
            'CASE ' + \
            'WHEN f.flex IS NOT NULL THEN substr(n.reestr, 1, length(n.reestr)-i.indent) || f.flex ' + \
            'ELSE n.reestr ' + \
            'END, ' + \
            'instr(n.reestr, \'"\')-2 AS accent_position ' + \
            'FROM nom AS n ' + \
            'INNER JOIN indents AS i ON i.type = n.type ' + \
            'LEFT JOIN flexes AS f ON f.type = n.type ' + \
            'WHERE n.accent = 0 AND accent_position = -2'

    for word, accent_position in tqdm(conn.execute(query), total=count):
        word = word.replace('"', '').replace('%', '').replace('*', '').replace('^', '').replace(
            'empty_', '')
        vowel = vowel_regex.search(word)
        if vowel is not None:
            f.write('{} {}\n'.format(word, vowel.start()))

    return count


def generate_accents_for_not_normal_words(conn, f):
    query = 'SELECT COUNT(*) ' + \
            'FROM (SELECT DISTINCT n.reestr, f.flex FROM nom AS n ' + \
            'LEFT JOIN flexes AS f ON f.type = n.type ' + \
            'WHERE n.accent != 0)'
    count = next(conn.execute(query))[0]

    query = 'SELECT DISTINCT n.reestr, ' + \
            'CASE ' + \
            'WHEN f.flex IS NOT NULL THEN substr(replace(n.reestr, \'"\', \'\'), 1, length(replace(n.reestr, \'"\', \'\'))-i.indent) || f.flex ' + \
            'ELSE n.reestr ' + \
            'END, ' + \
            'instr(n.reestr, \'"\')-2 AS accent_position, ' + \
            'a.indent1 ' + \
            'FROM nom AS n ' + \
            'INNER JOIN indents AS i ON i.type = n.type ' + \
            'LEFT JOIN flexes AS f ON f.type = n.type ' + \
            'LEFT JOIN accent as a ON a.gram = f.field2 AND a.accent_type = n.accent ' + \
            'WHERE n.accent != 0'

    for original, word, accent, indent in tqdm(conn.execute(query), total=count):
        word = word.replace('"', '').replace('%', '').replace('*', '').replace('^', '').replace(
            'empty_', '')
        indent = 0 if indent is None else indent
        if accent == -2:
            vowel = vowel_regex.search(word)
            if vowel is not None:
                f.write('{} {}\n'.format(word, vowel.start() + indent))
            else:
                continue
        else:
            f.write('{} {}\n'.format(word, accent + indent))

    return count


if __name__ == "__main__":
    data_dir = './data'
    if not os.path.isdir(data_dir):
        os.mkdir(data_dir)

    print('Downloading UA lexical database...')
    database_name = os.path.join(data_dir, 'mph_ua.db')
    db_url = 'https://github.com/LinguisticAndInformationSystems/mphdict/raw/master' \
             '/src/data/mph_ua.db'
    if not os.path.exists(database_name):
        download(db_url, data_dir)

    out_name = os.path.join(data_dir, 'accents.csv')
    f = open(out_name, mode='w')
    conn = sqlite3.connect(database_name)
    count = 0

    print('Extracting accents for multi-vowel normal form lexems...')
    count += generate_accents_for_normal_words(conn, f)

    print('Extracting accents for single-vowel normal form lexems...')
    count += generate_accents_for_single_vowel_words(conn, f)

    print('Extracting accents for not normal form lexems...')
    count += generate_accents_for_not_normal_words(conn, f)

    print('Done. Total lexical forms: {}'.format(count))



