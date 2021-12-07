import re
import time
from tnparser.pipeline import read_pipelines, Pipeline
from elg.model import AnnotationsResponse

text1='. '.join(["Minulla on söpö koira"]*2000)


available_pipelines=read_pipelines("models_fi_tdt_dia/pipelines.yaml")               # {pipeline_name -> its steps}
p=Pipeline(available_pipelines["parse_plaintext"])                                      # launch the pipeline from the steps
time.sleep(10)
#

job_id = p.parse_large_txt(text1)
while True:
    is_done, res = p.report_large_job(job_id)
    if is_done:
        print(res)
        break
    time.sleep(5)




