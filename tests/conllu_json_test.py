import json
import unittest
from utils import ConlluToJson

# pre-setup for loading data to test
## the orignal raw text that was parsed to tnpp parser server
with open('myfile.txt') as f:
    text = f.read()

def load_doc_conllu(conllu_file='single.doc.conllu'):
    """Load single doc parsed CONLL-U and setup some initial metrics to compare such as
    number of docs, number of paragraph, number of senteces and number of tokens"""

    with open(conllu_file, 'r') as f:
        input = f.read()

    num_doc, num_par, num_sent, num_tok = 0, 0, 0, 0
    all_lines = input.split('\n')
    for i, line in enumerate(all_lines):
        line = line.rstrip("\r")
        if line.startswith('#'):
            if 'newdoc' in line:
                num_doc += 1
            if 'newpar' in line:
                num_par += 1
            if 'sent_id' in line:
                num_sent += 1
        if not line:
            if all_lines[i-1].strip() != '':
                num_tok += int(all_lines[i-1].split('\t')[0]) # to get the last count of last token
    output = ConlluToJson().conllu_to_annotation(input)
    print(json.dumps(output, indent=2, ensure_ascii=False))
    return  num_doc, num_par, num_sent, num_tok, output
# print(json.dumps(output, indent=2, ensure_ascii=False))

class TestConlluToJsonInSingleDocumentParse(unittest.TestCase):

    num_doc, num_par, num_sent, num_tok, output = load_doc_conllu('single.doc.conllu')
    par_lst = output['tnpp/paragraphs']
    sent_lst = output['tnpp/sentences']
    tok_lst = output['tnpp/tokens']
    tok_size_lst = [len(tok_obj['features']['words']) for tok_obj in tok_lst] #  has to do this because of multi-word case, ettei -> että ei

    def test_num_paragraph(self):
        """Should return identical number of paragraph as in the original CONLL-U format
        """
        self.assertEqual(len(self.par_lst), self.num_par)

    def test_num_sentence(self):
        """Should return identical number of sentence as in the original CONLL-U format
        """
        self.assertEqual(len(self.sent_lst), self.num_sent)

    def test_num_token(self):
        """Should return identical number of tokens as in the original CONLL-U format
        """
        self.assertEqual(sum(self.tok_size_lst), self.num_tok)

    def test_offset_end_of_paragraph(self):
        """
        Should return the end offset of the paragraph as the length of the orignal text file
        """
        last_par = self.par_lst[-1]
        self.assertEqual(last_par['end'], len(text))

    def test_first_sent_offsets(self):
        sent0 = self.sent_lst[0]
        self.assertEqual(int(sent0['start']), 0)
        self.assertEqual(int(sent0['end']), len(text.split('.')[0]) + 1)

    def test_offset_distance_between_two_senteces(self):
        """
        Two consecutive sentences A andb B, B should have offset_start equal to A's offset's end + 1 
        """
        sentA = self.sent_lst[0]
        sentB = self.sent_lst[1]

        self.assertEqual(int(sentA['end']) + 1, int(sentB['start']))

    def test_first_token_offsets(self):
        """
        First token should have start index as 0 and end index by length of the first word in text
        """
        first_tok = self.tok_lst[0]
        self.assertEqual(int(first_tok['start']), 0)
        self.assertEqual(int(first_tok['end']), len(text.split(' ')[0]))

    def test_last_token_end_offset(self):
        """
        Last token should have end index by the length of text
        """
        last_tok = self.tok_lst[-1]
        self.assertEqual(int(last_tok['end']), len(text))

class TestConlluToJsonInDoubleDocumentParse(unittest.TestCase):

    num_doc, num_par, num_sent, num_tok, output = load_doc_conllu('double.doc.conllu')
    par_lst = output['tnpp/paragraphs']
    sent_lst = output['tnpp/sentences']
    tok_lst = output['tnpp/tokens']
    tok_size_lst = [len(tok_obj['features']['words']) for tok_obj in tok_lst] #  has to do this because of multi-word case, ettei -> että ei

    def test_num_paragraph(self):
        """Should return identical number of paragraph as in the original CONLL-U format
        """
        self.assertEqual(len(self.par_lst), self.num_par)

if __name__ == '__main__':
    unittest.main()