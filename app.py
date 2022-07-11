#!/usr/bin/env python
import os

from tnparser.pipeline import Pipeline, read_pipelines

from elg import FlaskService
from elg.model import TextRequest
from elg.model.base import StandardMessages
from elg.model import Failure
from elg.model import AnnotationsResponse

from utils.utils import ConlluToJson

model = "models_fi_tdt_dia/pipelines.yaml"
if not os.path.isfile(model):
    raise FileNotFoundError('Cannot find model setting file')
pipeline = "parse_plaintext"
MAX_CHAR = 15000
available_pipelines = read_pipelines(model)

tnpp = Pipeline(available_pipelines[pipeline])


class TurkuNeuralParser(FlaskService, ConlluToJson):

    def conllu_to_annotation(self, conllu, includeConllu):
        try:
            annots = super().conllu_to_annotation(conllu, includeConllu)
            return AnnotationsResponse(annotations=annots)
        except Exception:
            internalErrorMessage = StandardMessages.\
                generate_elg_service_internalerror(params=['Parsing CONLLU failed'])
            return Failure(errors=[internalErrorMessage])

    def process_text(self, request: TextRequest):
        content = request.content

        params = request.params
        includeConllu = False
        if params and "includeConllu" in params:
            includeConllu = params.get("includeConllu")
            if not isinstance(includeConllu, bool):
                invalid_param_msg = 'includeConllu parameter requires boolean type'
                error = StandardMessages.\
                        generate_elg_request_invalid(
                            detail={'params': invalid_param_msg})
                return Failure(errors=[error])

        if len(content.strip()) > MAX_CHAR:
            tooLargeMessage = StandardMessages.generate_elg_request_too_large()
            return Failure(errors=[tooLargeMessage])
        elif len(content.strip()) < 5:
            tooShortMessage = StandardMessages.generate_elg_request_invalid(
                detail={'text': 'lower limit is 5 characters in length'})
            return Failure(errors=[tooShortMessage])
        else:
            output = tnpp.parse(content)
            if output is False:
                internalErrorMessage = StandardMessages.\
                        generate_elg_service_internalerror(params=[
                            'The service is busy, please request it later.'
                        ])
                return Failure(errors=[internalErrorMessage])
            return self.conllu_to_annotation(conllu=output,
                                             includeConllu=includeConllu)


tnpp_service = TurkuNeuralParser("turku-neural-parser")
app = tnpp_service.app
