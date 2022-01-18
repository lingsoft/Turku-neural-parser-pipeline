#!/usr/bin/env python
import os
from tnparser.pipeline import Pipeline, read_pipelines
from tests.utils import ConlluToJson

model=os.environ.get("TNPP_MODEL","models_fi_tdt/pipelines.yaml")
pipeline=os.environ.get("TNPP_PIPELINE","parse_plaintext")
max_char=int(os.environ.get("TNPP_MAX_CHARS",15000))
available_pipelines=read_pipelines(model)
p=Pipeline(available_pipelines[pipeline])

            
from elg import FlaskService
from elg.model import AnnotationsResponse


class TurkuNeuralParser(FlaskService, ConlluToJson):

    tnpp = Pipeline(available_pipelines[pipeline])

    def conllu_to_annotation(self, conllu):
        annots = super().conllu_to_annotation(conllu)
        try:
            return AnnotationsResponse(annotations=annots)
        except Exception as e:
            # print(annots)
            raise e

    def conllu_list_to_annotation(self, conllus):
        res = [self.conllu_to_annotation(conllu).annotations for conllu in conllus]
        offsets = {"tnpp/docs": [], "tnpp/paragraphs": [], "tnpp/sentences": [], "tnpp/tokens": [], "tnpp/conllu": []}
        annots = {"tnpp/docs": [], "tnpp/paragraphs": [], "tnpp/sentences": [], "tnpp/tokens": [], "tnpp/conllu": []}
        for item in res:
            for k in annots.keys():
                annots[k].extend(item[k])
                offsets[k].append(len(item[k]))
        return AnnotationsResponse(annotations=annots, features=offsets)

    def process_text(self, request):
        params = request.params
        if params:
            # Request with job_id
            if 'job_id' in params:
                job_id = params['job_id']
                # Get job status
                report = self.tnpp.report_large_job(job_id)
                assert len(report) != 1, 'Job not exists or already retreived the result.'
                is_done,res = report
                # is_done then return the result
                if is_done:
                    return self.conllu_list_to_annotation(res)
                # else return the progress
                else:
                    return AnnotationsResponse(features={'progress_report': res})
        # large request return job_id
        if len(request.content) > max_char:
            job_id = self.tnpp.parse_large_txt(request.content)
            assert job_id is not False, 'The service is busy or your request is too large, please request it later.'
            return AnnotationsResponse(features={'job_id': job_id})
        # empty request return empty response
        elif len(request.content) == 0:
            return AnnotationsResponse(annotations={"tnpp/docs": [], "tnpp/paragraphs": [], "tnpp/sentences": [], "tnpp/tokens": [], "tnpp/conllu": []})
        else:
            output = self.tnpp.parse(request.content)
            assert output is not False, 'The service is busy, please request it later.'
            return self.conllu_to_annotation(output)


tnpp_service = TurkuNeuralParser("turku-neural-parser")
app = tnpp_service.app
