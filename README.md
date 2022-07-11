# Turku-neural-parser-pipeline

A new take on the trusty old Finnish-dep-parser with pretrained models for more than 50 languages. The current pipeline is fully neural and has a substantially better accuracy in all layers of prediction (segmentation, morphological tagging, syntax, lemmatization).

Documentation: https://turkunlp.github.io/Turku-neural-parser-pipeline/

# ELG API for Turku Neural Parser Pipeline

This branch contains [ELG compatible](https://european-language-grid.readthedocs.io/en/stable/all/A3_API/LTInternalAPI.html) Flask based REST API for the Turku Neural Parser Pipeline. The API supports Finnish language and plain-text input.

This ELG API was developed in EU's CEF project: [Microservices at your service](https://www.lingsoft.fi/en/microservices-at-your-service-bridging-gap-between-nlp-research-and-industry).

## Local development

Setup virtualenv with dependencies
```
python3 -m venv tnpp-elg-venv
source tnpp-elg-venv/bin/activate
python3 -m pip install -r requirements.txt
```

Download a model and all of its supporting pipelines
```
python3 fetch_models.py fi_tdt_dia
```
The script downloads and unzips the Finnish TDT latest (v2.8) model and pipelines into `models_fi_tdt_dia` directory.

Run the development mode flask app
```
FLASK_ENV=development flask run --host 0.0.0.0 --port 8000
```

## Running tests
The `tests/test.py` tests the CoNLL-U - ELG JSON conversion and the response of the API

```
python3 -m unittest tests/test.py  -v
```

## Building the docker image

```
docker build -t turku-neural-parser .
```

Or pull directly ready-made image `docker pull lingsoft/turku-neural-parser:tagname`.

## Deploying the service

```
docker run -d -p <port>:8000 --init turku-neural-parser
```

## REST API

### Call pattern

#### URL

```
http://<host>:<port>/process
```

Replace `<host>` and `<port>` with the host name and port where the
service is running.

#### HEADERS

```
Content-type : application/json
```

#### BODY

```json
{
  "type":"text",
  "content": "text to be parsed",
  "params": {
    "includeConllu": true
  }
}
```

The API supports text content with the maximum of 15000-character length. 
In addtion, there is a boolean parameter `includeConllu` which can control 
the API in outputting the original ConLL-U format from the parser. 
The parameter has a default value of `false`

### Example call

```
curl -d '{"type":"text","content":"Se näytti, ettei väkivahvakaan tulos aina riitä.", "params": {"includeConllu":true}}' -H "Content-Type: application/json" -X POST http://localhost:8000/process
```

### Response should be

```json
{
  "response": {
    "type": "annotations",
    "annotations": {
      "udpipe/docs": [
        {
          "start": 0,
          "end": 48,
          "features": {
            "doc_id": 1
          }
        }
      ],
      "udpipe/paragraphs": [
        {
          "start": 0,
          "end": 48,
          "features": {
            "par_id": 1
          }
        }
      ],
      "udpipe/sentences": [
        {
          "start": 0,
          "end": 48,
          "features": {
            "sent_id": 1
          }
        }
      ],
      "udpipe/tokens": [
        {
          "start": 0,
          "end": 2,
          "features": {
            "words": [
              {
                "id": "1",
                "form": "Se",
                "lemma": "se",
                "upos": "PRON",
                "feats": "Case=Nom|Number=Sing|PronType=Dem",
                "head": 2,
                "deprel": "nsubj",
                "misc": "TokenRange=0:2"
              }
            ]
          }
        },
        {
          "start": 3,
          "end": 9,
          "features": {
            "words": [
              {
                "id": "2",
                "form": "n\u00e4ytti",
                "lemma": "n\u00e4ytt\u00e4\u00e4",
                "upos": "VERB",
                "feats": "Mood=Ind|Number=Sing|Person=3|Tense=Past|VerbForm=Fin|Voice=Act",
                "head": 0,
                "deprel": "root",
                "misc": "SpaceAfter=No|TokenRange=3:9"
              }
            ]
          }
        },
        {
          "start": 9,
          "end": 10,
          "features": {
            "words": [
              {
                "id": "3",
                "form": ",",
                "lemma": ",",
                "upos": "PUNCT",
                "head": 9,
                "deprel": "punct",
                "misc": "TokenRange=9:10"
              }
            ]
          }
        },
        {
          "start": 11,
          "end": 16,
          "features": {
            "words": [
              {
                "id": "4",
                "form": "ett\u00e4",
                "lemma": "ett\u00e4",
                "upos": "SCONJ",
                "head": 9,
                "deprel": "mark"
              },
              {
                "id": "5",
                "form": "ei",
                "lemma": "ei",
                "upos": "AUX",
                "feats": "Number=Sing|Person=3|Polarity=Neg|VerbForm=Fin|Voice=Act",
                "head": 9,
                "deprel": "aux"
              }
            ]
          }
        },
        {
          "start": 17,
          "end": 30,
          "features": {
            "words": [
              {
                "id": "6",
                "form": "v\u00e4kivahvakaan",
                "lemma": "v\u00e4ki#vahvaka",
                "upos": "ADJ",
                "feats": "Case=Nom|Clitic=Kin|Degree=Pos|Number=Sing",
                "head": 7,
                "deprel": "amod",
                "misc": "TokenRange=17:30"
              }
            ]
          }
        },
        {
          "start": 31,
          "end": 36,
          "features": {
            "words": [
              {
                "id": "7",
                "form": "tulos",
                "lemma": "tulos",
                "upos": "NOUN",
                "feats": "Case=Nom|Number=Sing",
                "head": 9,
                "deprel": "nsubj",
                "misc": "TokenRange=31:36"
              }
            ]
          }
        },
        {
          "start": 37,
          "end": 41,
          "features": {
            "words": [
              {
                "id": "8",
                "form": "aina",
                "lemma": "aina",
                "upos": "ADV",
                "head": 9,
                "deprel": "advmod",
                "misc": "TokenRange=37:41"
              }
            ]
          }
        },
        {
          "start": 42,
          "end": 47,
          "features": {
            "words": [
              {
                "id": "9",
                "form": "riit\u00e4",
                "lemma": "riitt\u00e4\u00e4",
                "upos": "VERB",
                "feats": "Connegative=Yes|Mood=Ind|Tense=Pres|VerbForm=Fin",
                "head": 2,
                "deprel": "ccomp",
                "misc": "SpaceAfter=No|TokenRange=42:47"
              }
            ]
          }
        },
        {
          "start": 47,
          "end": 48,
          "features": {
            "words": [
              {
                "id": "10",
                "form": ".",
                "lemma": ".",
                "upos": "PUNCT",
                "head": 2,
                "deprel": "punct",
                "misc": "SpacesAfter=\\n|TokenRange=47:48"
              }
            ]
          }
        }
      ],
      "udpipe/conllu": [
        {
          "start": 0,
          "end": 48,
          "features": {
            "conllu_format": "# newdoc\n# newpar\n# sent_id = 1\n# text = Se n\u00e4ytti, ettei v\u00e4kivahvakaan tulos aina riit\u00e4.\n1\tSe\tse\tPRON\t_\tCase=Nom|Number=Sing|PronType=Dem\t2\tnsubj\t_\tTokenRange=0:2\n2\tn\u00e4ytti\tn\u00e4ytt\u00e4\u00e4\tVERB\t_\tMood=Ind|Number=Sing|Person=3|Tense=Past|VerbForm=Fin|Voice=Act\t0\troot\t_\tSpaceAfter=No|TokenRange=3:9\n3\t,\t,\tPUNCT\t_\t_\t9\tpunct\t_\tTokenRange=9:10\n4-5\tettei\t_\t_\t_\t_\t_\t_\t_\tTokenRange=11:16\n4\tett\u00e4\tett\u00e4\tSCONJ\t_\t_\t9\tmark\t_\t_\n5\tei\tei\tAUX\t_\tNumber=Sing|Person=3|Polarity=Neg|VerbForm=Fin|Voice=Act\t9\taux\t_\t_\n6\tv\u00e4kivahvakaan\tv\u00e4ki#vahvaka\tADJ\t_\tCase=Nom|Clitic=Kin|Degree=Pos|Number=Sing\t7\tamod\t_\tTokenRange=17:30\n7\ttulos\ttulos\tNOUN\t_\tCase=Nom|Number=Sing\t9\tnsubj\t_\tTokenRange=31:36\n8\taina\taina\tADV\t_\t_\t9\tadvmod\t_\tTokenRange=37:41\n9\triit\u00e4\triitt\u00e4\u00e4\tVERB\t_\tConnegative=Yes|Mood=Ind|Tense=Pres|VerbForm=Fin\t2\tccomp\t_\tSpaceAfter=No|TokenRange=42:47\n10\t.\t.\tPUNCT\t_\t_\t2\tpunct\t_\tSpacesAfter=\\n|TokenRange=47:48\n\n"
          }
        }
      ]
    }
  }
}
```

### Response structure

- `start` and `end` (int)
  - the indices of the token from the text in the send request.
- `doc_id`, `par_id`, `sent_id` (int)
  - the indices of the document, paragraph, and sentence.
- `words` (list)
  - list of objects that contains common supported fields of CONLLU.
- `conllu_format` (str)
  - string contains CoNLL-U results from the pipeline. 

### Local ELG GUI

Use ELG-compatible service from GUI locally

```
cd elg_local && docker-compose up
```

The GUI is accessible on `http://localhost:5080`. See more
[instructions](https://european-language-grid.readthedocs.io/en/stable/all/A1_PythonSDK/DeployServicesLocally.html#deploy-elg-compatible-service-from-its-docker-image).
