import json

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
        conllu = f.readlines()
        sent_cnt = 0
        doc_cnt = 0
        annots = {"docs": [], "paragraphs": [], "sentences": [], "tokens": []}

        first_doc, first_par, first_sent, last_token = None, None, None, None
        offset = 0
        curr_text = ""
        for line in conllu:
            line = line.rstrip("\r")

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

            if line is '\n':
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

            if cols[0].isdigit():
                tokens = 1
            else:
                raise Exception(
                    "Internal error: Cannot parse CoNLL-U response")

            if tokens == 1:
                curr_word = cols[1]
                token_start = curr_text.find(curr_word) + offset
                token_end = token_start + len(curr_word)
                curr_text = curr_text[token_end-offset:]
                offset = token_end

                annots["tokens"].append({"start": token_start, "end": token_end, "features": {
                                        "words": [_conllu_parse_word(cols)]}})

                if first_par is None:
                    first_par = token_start
                if first_sent is None:
                    first_sent = token_start
                last_token = token_end

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
