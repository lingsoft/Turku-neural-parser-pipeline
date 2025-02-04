import json
import re


class ConlluToJson:
    def _conllu_parse_word(self, cols):
        result = {"id": cols[0], "form": cols[1]}
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
        if cols[8] != "_":
            result["deps"] = cols[8]
        if cols[9] != "_":
            result["misc"] = cols[9]

        return result

    def conllu_to_annotation(self, conllu, includeConllu=False):
        """Convert CONLLU format to annotation objects (Dict object)"""
        """Modifed from https://gitlab.com/european-language-grid/cuni/srv-udpipe/-/blob/master/elg_adapter/udpipe_elg_rest_server.py#L127"""
        """CONLLU:
            # new doc
            # new par
            # sent_id = 1
            # text = Tämä on testilause
            1	Tämä	tämä	PRON	_	Case=Nom|Number=Sing|PronType=Dem	3	nsubj:cop	_	_
            2	on	olla	AUX	_	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin|Voice=Act	3	cop	__
            3	testilause	testi#lause	NOUN	_	Case=Nom|Number=Sing	0	root	_	SpacesAfter=\n
            """
        sent_cnt = 0
        doc_cnt = 0
        par_cnt = 0
        annots = {
            "udpipe/docs": [],
            "udpipe/paragraphs": [],
            "udpipe/sentences": [],
            "udpipe/tokens": []
        }

        first_doc, first_par, first_sent, last_token, in_mwt = None, None, None, None, 0
        offset = 0
        curr_text = ""
        conllu_split = conllu.split("\n")
        for i, line in enumerate(conllu_split):
            line = line.rstrip("\r")

            # Handle continuing multi-word projects
            if in_mwt:
                cols = line.split("\t")
                if len(cols) != 10 or not cols[0].isdigit():
                    raise Exception(
                        "Internal error: Cannot parse CoNLL-U response")
                annots["udpipe/tokens"][-1]["features"]["words"].append(
                    self._conllu_parse_word(cols))
                in_mwt -= 1
                continue

            if line.startswith("#"):
                # Check end of document
                if "newdoc" in line:
                    if first_doc is not None and last_token is not None:
                        doc_cnt += 1
                        annots["udpipe/docs"].append({
                            "start": first_doc,
                            "end": last_token,
                            "features": {
                                "doc_id": doc_cnt
                            }
                        })
                    first_doc = None
                    continue

                # Check end of paragraph
                if "newpar" in line:
                    if first_par is not None and last_token is not None:
                        par_cnt += 1
                        annots["udpipe/paragraphs"].append({
                            "start": first_par,
                            "end": last_token,
                            "features": {
                                "par_id": par_cnt
                            }
                        })
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
                    annots["udpipe/sentences"].append({
                        "start": first_sent,
                        "end": last_token,
                        "features": {
                            "sent_id": sent_cnt
                        }
                    })
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

            # Now Tokenrange is in CONLLU
            match = re.search(r"TokenRange=(\d+):(\d+)", cols[9])
            if not match:
                raise Exception(
                    "Internal error: Cannot parse CoNLL-U response")
            token_start, token_end = int(match.group(1)), int(match.group(2))

            if first_par is None:
                first_par = token_start
            if first_sent is None:
                first_sent = token_start
            if first_doc is None:
                first_doc = token_start
            last_token = token_end

            annots["udpipe/tokens"].append({
                "start": token_start,
                "end": token_end,
                "features": {
                    "words": []
                }
            })
            if tokens == 1:
                annots["udpipe/tokens"][-1]["features"]["words"].append(
                    self._conllu_parse_word(cols))
            else:
                in_mwt = tokens

        if first_par is not None and last_token is not None:
            par_cnt += 1
            annots["udpipe/paragraphs"].append({
                "start": first_par,
                "end": last_token,
                "features": {
                    "par_id": par_cnt
                }
            })

        if first_sent is not None and last_token is not None:
            sent_cnt += 1
            annots["udpipe/sentences"].append({
                "start": first_sent,
                "end": last_token,
                "features": {
                    "sent_id": sent_cnt
                }
            })

        if first_doc is not None and last_token is not None:
            doc_cnt += 1
            annots["udpipe/docs"].append({
                "start": first_doc,
                "end": last_token,
                "features": {
                    "doc_id": doc_cnt
                }
            })
        if includeConllu:
            annots["udpipe/conllu"] = list()
            annots["udpipe/conllu"].append({
                "start": 0,
                "end": last_token,
                "features": {
                    "conllu_format": conllu
                }
            })
        return annots
