#!/usr/bin/env python
import requests
import tarfile
import io

import argparse
from transformers import AutoTokenizer, AutoModelForMaskedLM

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='grab models')
    parser.add_argument('--to',
                        default=".",
                        help="Where to download? Default:%(default)s")
    parser.add_argument('modelname', help='which model to grab')
    args = parser.parse_args()

    zip_file_url = "http://dl.turkunlp.org/turku-parser-models/models_{}.tgz".format(
        args.modelname)

    print("Downloading from {} and unpacking".format(args.modelname))

    r = requests.get(zip_file_url, stream=True)

    z = tarfile.open(mode="r|gz", fileobj=io.BytesIO(r.content))
    z.extractall(path=args.to)

    tokenizer = AutoTokenizer.from_pretrained(
        "TurkuNLP/bert-base-finnish-cased-v1")

    model = AutoModelForMaskedLM.from_pretrained(
        "TurkuNLP/bert-base-finnish-cased-v1")

    tokenizer.save_pretrained('TurkuNLP/bert-base-finnish-cased-v1')
    model.save_pretrained('TurkuNLP/bert-base-finnish-cased-v1')
