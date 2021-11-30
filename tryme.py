from tnparser.pipeline import read_pipelines, Pipeline

text1="I have a dog! Let's see what I can do with Silo.ai. :) Can I tokenize it? I think so! Heading: This is the heading And here continues a new sentence and there's no dot."
text2="Some other text, to see we can tokenize more stuff without reloading the model... :)"


# What do we have for English in models_en_ewt?
available_pipelines=read_pipelines("models_fi_tdt_dia/pipelines.yaml")               # {pipeline_name -> its steps}
p=Pipeline(available_pipelines["parse_plaintext"])                                      # launch the pipeline from the steps

for _ in range(1000):
    print(p.parse(text1))
    print(p.parse(text2))
    
