import json
import unittest
import os
from utils.utils import ConlluToJson
import requests

# pre-setup for loading data to test
# the orignal raw text that was parsed to tnpp parser server
with open(os.path.join(os.path.dirname(__file__), 'test.txt'), 'r') as f:
    text = f.read()


def load_doc_conllu(conllu_file='single.doc.conllu'):
    """Load single doc parsed CONLL-U and setup some initial metrics
    to compare such as number of docs, number of paragraph, number
    of senteces and number of tokens"""

    with open(os.path.join(os.path.dirname(__file__), conllu_file), 'r') as f:
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
            if all_lines[i - 1].strip() != '':
                num_tok += int(all_lines[i - 1].split('\t')
                               [0])  # to get the last count of last token
    output = ConlluToJson().conllu_to_annotation(input)
    with open('tests/elg.json', 'w') as f:
        json.dump(output, f, indent=2, ensure_ascii=True)

    return num_doc, num_par, num_sent, num_tok, output


# print(json.dumps(output, indent=2, ensure_ascii=False))


class TestConlluToJsonInSingleDocumentParse(unittest.TestCase):

    num_doc, num_par, num_sent, num_tok, output = load_doc_conllu(
        'single.doc.conllu')
    par_lst = output['udpipe/paragraphs']
    sent_lst = output['udpipe/sentences']
    tok_lst = output['udpipe/tokens']
    tok_size_lst = [
        len(tok_obj['features']['words']) for tok_obj in tok_lst
    ]  #  has to do this because of multi-word case, ettei -> että ei

    def test_num_paragraph(self):
        """Should return identical number of paragraph
        as in the original CONLL-U format
        """
        self.assertEqual(len(self.par_lst), self.num_par)

    def test_num_sentence(self):
        """Should return identical number of sentence
        as in the original CONLL-U format
        """
        self.assertEqual(len(self.sent_lst), self.num_sent)

    def test_num_token(self):
        """Should return identical number of tokens
        as in the original CONLL-U format
        """
        self.assertEqual(sum(self.tok_size_lst), self.num_tok)

    def test_offset_end_of_paragraph(self):
        """
        Should return the end offset of the paragraph
        as the length of the orignal text file
        """
        last_par = self.par_lst[-1]
        self.assertEqual(last_par['end'], len(text))

    def test_first_sent_offsets(self):
        sent0 = self.sent_lst[0]
        self.assertEqual(int(sent0['start']), 0)
        self.assertEqual(int(sent0['end']), len(text.split('.')[0]) + 1)

    def test_offset_distance_between_two_senteces(self):
        """
        Two consecutive sentences A and B, B should
        have offset_start equal to A's offset's end + 1
        """
        sentA = self.sent_lst[0]
        sentB = self.sent_lst[1]

        self.assertEqual(int(sentA['end']) + 1, int(sentB['start']))

    def test_first_token_offsets(self):
        """
        First token should have start index as 0 and end
        index by length of the first word in text
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


class TestResponse(unittest.TestCase):
    base_url = 'http://localhost:8000/process'

    base_text = ["olen iloinen että minulla on söpö koira"]

    payload = json.dumps({"type": "text", "content": base_text[0]})

    headers = {'Content-Type': 'application/json'}

    def test_api_response_status_code(self):
        """Should return status code 200
        """

        status_code = requests.post(self.base_url,
                                    headers=self.headers,
                                    data=self.payload).status_code
        self.assertEqual(status_code, 200)

    def test_valid_api_response(self):
        """Return response should not be empty
        """

        response = requests.post(self.base_url,
                                 headers=self.headers,
                                 data=self.payload).json()['response']
        self.assertNotEqual(response, None)

    def test_api_response_type(self):
        """Should return ELG annotation response type
        """

        response = requests.post(self.base_url,
                                 headers=self.headers,
                                 data=self.payload).json()['response']
        self.assertEqual(response.get('type'), 'annotations')

    def test_api_response_content(self):
        """Should return correct content
        """

        response = requests.post(self.base_url,
                                 headers=self.headers,
                                 data=self.payload).json()['response']

        # test all available properties
        for prop in [
                'udpipe/docs', 'udpipe/paragraphs', 'udpipe/sentences',
                'udpipe/tokens'
        ]:
            self.assertIn(prop, response['annotations'])

    def test_api_response_with_too_large_req(self):
        """Should return Failure with too large request which
        exceeds 15000-char length
        """

        large_text = '. '.join(self.base_text * 1000)
        assert len(large_text) > 15000, 'text is not large enough'

        payload_dict = {"type": "text", "content": large_text}
        payload = json.dumps(payload_dict)
        response = requests.post(self.base_url,
                                 headers=self.headers,
                                 data=payload).json()

        self.assertIn('failure', response)
        self.assertEqual(response['failure']['errors'][0]['code'],
                         'elg.request.too.large')

    def test_api_response_with_empty_request(self):
        """Should return failure response
        """

        payload_dict = {"type": "text", "content": ""}
        payload = json.dumps(payload_dict)
        response = requests.post(self.base_url,
                                 headers=self.headers,
                                 data=payload).json()

        self.assertIn('failure', response)
        self.assertEqual(response['failure']['errors'][0]['code'],
                         'elg.request.invalid')

    def test_api_response_with_large_request(self):
        """Should return correct response when submitting
        a request with nearly 15000-char length.
        """
        large_text = '. '.join(self.base_text * 1000)
        assert len(large_text) >= 15000, 'text is not large enough'

        payload_dict = {"type": "text", "content": large_text[:15000]}
        payload = json.dumps(payload_dict)

        response = requests.post(self.base_url,
                                 headers=self.headers,
                                 data=payload).json()['response']

        self.assertEqual(response.get('type'), 'annotations')
        for prop in [
                'udpipe/docs', 'udpipe/paragraphs', 'udpipe/sentences',
                'udpipe/tokens'
        ]:
            self.assertIn(prop, response['annotations'])
            self.assertNotEqual(response['annotations'][prop], [])

    def test_api_response_with_invalid_params(self):
        """Should return failure response when submitting
        a request with invalid includeConllu paramter.
        """
        payload_dict = {
            "type": "text",
            "content": "Minulla on koira.",
            "params": {
                "includeConllu": 12
            }
        }
        payload = json.dumps(payload_dict)
        response = requests.post(self.base_url,
                                 headers=self.headers,
                                 data=payload).json()

        self.assertIn('failure', response)
        self.assertEqual(response['failure']['errors'][0]['code'],
                         'elg.request.invalid')

    def test_api_response_with_conllu_include(self):
        """Should return correct response with CoNLLU when submitting
        a request with True includeConllu  paramter.
        """
        payload_dict = {
            "type": "text",
            "content": "Minulla on koira.",
            "params": {
                "includeConllu": True
            }
        }
        payload = json.dumps(payload_dict)
        response = requests.post(self.base_url,
                                 headers=self.headers,
                                 data=payload).json()['response']

        self.assertEqual(response.get('type'), 'annotations')
        self.assertIn('udpipe/conllu', response['annotations'])
        self.assertNotEqual(response['annotations']['udpipe/conllu'], [])

    def test_api_response_with_conllu_exclude(self):
        """Should return correct response without CoNLLU when submitting
        a request with False includeConllu  paramter.
        """
        payload_dict = {
            "type": "text",
            "content": "Minulla on koira.",
            "params": {
                "includeConllu": False
            }
        }
        payload = json.dumps(payload_dict)
        response = requests.post(self.base_url,
                                 headers=self.headers,
                                 data=payload).json()['response']

        self.assertEqual(response.get('type'), 'annotations')
        self.assertNotIn('udpipe/conllu', response['annotations'])


if __name__ == '__main__':
    unittest.main()
