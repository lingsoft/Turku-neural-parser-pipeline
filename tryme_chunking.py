from tnparser.pipeline import read_pipelines, Pipeline

text1='. '.join(["Minulla on söpö koira"]*5000)


available_pipelines=read_pipelines("models_fi_tdt_dia/pipelines.yaml")               # {pipeline_name -> its steps}
p=Pipeline(available_pipelines["parse_plaintext"])                                      # launch the pipeline from the steps

job_id = p.parse_large_txt(text1)
while True:
    print(p.report_large_job(job_id))



