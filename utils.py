import json
import re


def _conllu_parse_word(cols):
    result = {"form": cols[1]}
    if cols[2] != "_" or cols[1] == "_":
        result["lemma"] = cols[2]
    if cols[3] != "_":
        result["upos"] = cols[3]
    if cols[4] != "_":
        result["xpos"] = cols[4]
    if cols[5] != "_":
        result["feats"] = cols[5]
    if cols[6] != "_":
        result["head"] = int(cols[6])
    if cols[7] != "_":
        result["deprel"] = cols[7]
    return result


def conllu2json(fname='myfile.conllu'):

    with open(fname, 'r') as f:
        origin_conllu = f.read()
        conllu = origin_conllu.split("\n")
        sent_cnt = 0
        doc_cnt = 0
        annots = {"conllu":origin_conllu, "docs": [], "paragraphs": [], "sentences": [], "tokens": []}

        first_doc, first_par, first_sent, last_token, in_mwt = None, None, None, None, 0
        offset = 0
        curr_text = ""
        for i,line in enumerate(conllu):
            line = line.rstrip("\r")

            # Handle continuing multi-word projects
            if in_mwt:
                cols = line.split("\t")
                if len(cols) != 10 or not cols[0].isdigit():
                    raise Exception(
                        "Internal error: Cannot parse CoNLL-U response")
                annots["tokens"][-1]["features"]["words"].append(
                    _conllu_parse_word(cols))
                in_mwt -= 1
                continue

            if line.startswith("#"):
                # Check end of document
                if "newdoc" in line:
                    doc_cnt += 1
                    if first_doc is not None:
                        annots["docs"].append({"doc_id": doc_cnt})
                    continue

                # Check end of paragraph
                if "newpar" in line:
                    if first_par is not None and last_token is not None:
                        annots["paragraphs"].append(
                            {"start": first_par, "end": last_token, "features": {}})
                    first_par = None
                    continue

                if "sent_id" in line:
                    sent_cnt += 1
                    continue

                if "text" in line:
                    curr_text = line.split('=')[-1].strip()
                    continue

            if not line:
                # Check end of sentence
                if first_sent is not None and last_token is not None:
                    annots["sentences"].append(
                        {"start": first_sent, "end": last_token, "features": {}})
                first_sent = None
                offset += 1
                continue

            # Start parsing text content
            cols = line.split("\t")
            if len(cols) != 10:
                raise Exception(
                    "Internal error: Cannot parse CoNLL-U response")

            # Ignore enhanced UD nodes
            if "." in cols[0]:
                continue

            tokens = None
            # check for mwt
            match = re.match(r"(\d+)-(\d+)$", cols[0])
            if match:
                # Muli-word token
                first, last = int(match.group(1)), int(match.group(2))
                tokens = last - first + 1
            elif cols[0].isdigit():
                tokens = 1
            else:
                raise Exception(
                    "Internal error: Cannot parse CoNLL-U response")

            # Parse token start,end from current word since we don't have TokenRange in CONLLU
            curr_word = cols[1]
            token_start = curr_text.find(curr_word) + offset
            token_end = token_start + len(curr_word)
            curr_text = curr_text[token_end-offset:]
            offset = token_end

            if first_par is None:
                first_par = token_start
            if first_sent is None:
                first_sent = token_start
            last_token = token_end

            annots["tokens"].append({"start": token_start, "end": token_end, "features": {
                                    "words": []}})
            if tokens == 1:
                annots["tokens"][-1]["features"]["words"].append(
                    _conllu_parse_word(cols))
            else:
                in_mwt = tokens

        if first_par is not None and last_token is not None:
            annots["paragraphs"].append(
                {"start": first_par, "end": last_token, "features": {}})

        if first_sent is not None and last_token is not None:
            annots["sentences"].append(
                {"start": first_sent, "end": last_token, "features": {}})

        if first_par is not None and first_sent is not None:
            annots["docs"].append({"doc_id": doc_cnt})

    print(json.dumps(annots, indent=2, sort_keys=False, ensure_ascii=False))


conllu2json()
