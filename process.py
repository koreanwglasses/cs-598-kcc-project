import re
import csv
from glob import glob
from bs4 import BeautifulSoup
from textstat import lexicon_count, sentence_count
from nltk import word_tokenize, pos_tag
from nltk.parse.corenlp import CoreNLPDependencyParser
import nltk
from collections import Counter
import warnings
warnings.filterwarnings("ignore", message=".*looks like a URL.*", module='bs4')

nltk.download('averaged_perceptron_tagger')

dep_parser = CoreNLPDependencyParser(url='http://localhost:9000')
parses = dep_parser.parse('What is the airspeed of an unladen swallow ?'.split())
print([[dep for _, dep, _ in parse.triples()] for parse in parses])

exit(0)

POS_TAGS = [
    "CC",
    "CD",
    "DT",
    "EX",
    "FW",
    "IN",
    "JJ",
    "JJR",
    "JJS",
    "LS",
    "MD",
    "NN",
    "NNS",
    "NNP",
    "NNPS",
    "PDT",
    "POS",
    "PRP",
    "PRP$",
    "RB",
    "RBR",
    "RBS",
    "RP",
    "SYM",
    "TO",
    "UH",
    "VB",
    "VBD",
    "VBG",
    "VBN",
    "VBP",
    "VBZ",
    "WDT",
    "WP",
    "WP$",
    "WRB"
]

PRETERMINALS = [
    "S",
    "SBAR",
    "SBARQ",
    "SINV",
    "SQ",
    "ADJP",
    "ADVP",
    "CONJP",
    "FRAG",
    "INTJ",
    "LST",
    "NAC",
    "NP",
    "NX",
    "PP",
    "PRN",
    "PRT",
    "QP",
    "RRC",
    "UCP",
    "VP",
    "WHADJP",
    "WHADVP",
    "WHNP",
    "WHPP",
    "X"
]

HEADER_OUT = [
    'TEXT',
    'CT1',
    'CT2',
    *['CT3.' + tag for tag in POS_TAGS],
#    *['CT4.' + preterm for preterm in PRETERMINALS],
    'CN1',
    'CN2',
    'U1.SUM',
    'U1.1',
    'U1.2',
    'U2',
    'O1',
    'Y1',
    'Y2',
    'T',
    'S',
    'D'
]


def process_datum(datum):
    # Remove tags
    soup = BeautifulSoup(datum["Content"], features="html.parser")

    clean_soup = BeautifulSoup(datum["Content"], features="html.parser")    
    for elm in clean_soup(["code"]):
        elm.extract()

    body_text = clean_soup.get_text()

    pos_tags = pos_tag(word_tokenize(body_text))

    pos_counts = Counter([tag for word, tag in pos_tags])
    # preterm_counts =

    result = {}
    result['TEXT'] = body_text
    result['CT1'] = lexicon_count(body_text)
    result['CT2'] = sentence_count(body_text)
    for tag in POS_TAGS:
        result['CT3.' + tag] = pos_counts[tag]
    # for preterm in PRETERMINALS:
        # results['CT4.' + preterm] =
    result['CN1'] = len(soup.find_all("code", href=True)) +\
        len(soup.find_all("img", href=True)) +\
        len(soup.findAll("span", {"class": "math-container"}))
    result['CN2'] = len(soup.find_all("a", href=True))
    result['U1.SUM'] = datum['U1.SUM']
    result['U1.1'] = datum['U1.1']
    result['U1.2'] = datum['U1.2']
    result['U2'] = datum['U2']
    result['Y1'] = datum['Y1']
    result['Y2'] = datum['Y2']
    result['T'] = datum['T']
    result['S'] = datum['S']
    result['D'] = datum['D']

    return result


with open("se-1.csv", "w") as out_file:
    writer = csv.writer(out_file)
    writer.writerow(HEADER_OUT)

    processed_rows_count = 0
    for filename in glob("data/*.csv"):

        with open(filename) as in_file:
            header_row = None
            for row in csv.reader(in_file):
                if not header_row:
                    header_row = row
                    continue

                datum = {}
                for key, value in zip(header_row, row):
                    datum[key] = value

                result = process_datum(datum)

                new_row = [result[key]
                           if key in result else None for key in HEADER_OUT]

                writer.writerow(new_row)

                processed_rows_count += 1
                if processed_rows_count % 100 == 0:
                    print(f"\rProcessed {processed_rows_count} rows", end="")


print(f"\rComplete! Processed {processed_rows_count} rows")
