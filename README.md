# Turku-neural-parser-pipeline
A new take on the trusty old Finnish-dep-parser with pretrained models for more than 50 languages. The current pipeline is fully neural and has a substantially better accuracy in all layers of prediction (segmentation, morphological tagging, syntax, lemmatization).


Documentation: https://turkunlp.github.io/Turku-neural-parser-pipeline/

# ELG service
## Run it locally
```shell
gunicorn tnpp_serve_elg:app -b 0.0.0.0:8080 -t 90
```
## Run it with docker
Suppose model and pipeline is downloaded and is placed under `models_fi_tdt_dia`folder.
```shell
python fetch_models.py fi_tdt_dia
```
```shell
docker build . -f Dockerfile.server.elg -t tnpp-elg
docker run --rm -p 8080:8000 tnpp-elg
```
## Send a POST request to the server:
```shell
curl -d '{"type":"text", "content": "Minä rakastan sinua!"}' -H "Content-Type: application/json" -X POST http://localhost:8080/process
```
Response should be:
There is orignal CONLLU format included under tnpp/conllu keys of annotations object.
```json
{
  "response": {
    "type": "annotations",
    "annotations": {
      "tnpp/docs": [
        {
          "start": 0,
          "end": 20,
          "features": {
            "doc_id": 1
          }
        }
      ],
      "tnpp/paragraphs": [
        {
          "start": 0,
          "end": 20,
          "features": {
            "par_id": 1
          }
        }
      ],
      "tnpp/sentences": [
        {
          "start": 0,
          "end": 20,
          "features": {
            "sent_id": 1
          }
        }
      ],
      "tnpp/tokens": [
        {
          "start": 0,
          "end": 4,
          "features": {
            "words": [
              {
                "form": "Minä",
                "lemma": "minä",
                "upos": "PRON",
                "feats": "Case=Nom|Number=Sing|Person=1|PronType=Prs",
                "head": 2,
                "deprel": "nsubj"
              }
            ]
          }
        },
        {
          "start": 5,
          "end": 13,
          "features": {
            "words": [
              {
                "form": "rakastan",
                "lemma": "rakastaa",
                "upos": "VERB",
                "feats": "Mood=Ind|Number=Sing|Person=1|Tense=Pres|VerbForm=Fin|Voice=Act",
                "head": 0,
                "deprel": "root"
              }
            ]
          }
        },
        {
          "start": 14,
          "end": 19,
          "features": {
            "words": [
              {
                "form": "sinua",
                "lemma": "sinä",
                "upos": "PRON",
                "feats": "Case=Par|Number=Sing|Person=2|PronType=Prs",
                "head": 2,
                "deprel": "obj"
              }
            ]
          }
        },
        {
          "start": 19,
          "end": 20,
          "features": {
            "words": [
              {
                "form": "!",
                "lemma": "!",
                "upos": "PUNCT",
                "head": 2,
                "deprel": "punct"
              }
            ]
          }
        }
      ],
      "tnpp/conllu": [
        {
          "start": 0,
          "end": 20,
          "features": {
            "conllu_format": "# newdoc\n# newpar\n# sent_id = 1\n# text = Minä rakastan sinua!\n1\tMinä\tminä\tPRON\t_\tCase=Nom|Number=Sing|Person=1|PronType=Prs\t2\tnsubj\t_\t_\n2\trakastan\trakastaa\tVERB\t_\tMood=Ind|Number=Sing|Person=1|Tense=Pres|VerbForm=Fin|Voice=Act\t0\troot\t_\t_\n3\tsinua\tsinä\tPRON\t_\tCase=Par|Number=Sing|Person=2|PronType=Prs\t2\tobj\t_\tSpaceAfter=No\n4\t!\t!\tPUNCT\t_\t_\t2\tpunct\t_\tSpacesAfter=\\n\n\n"
          }
        }
      ]
    }
  }
}
````



