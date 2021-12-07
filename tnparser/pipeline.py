import asyncio
from multiprocessing import Process,Queue
import multiprocessing as multiprocessing
import importlib
import hashlib
import random
import time
import os
import yaml
from signal import signal, SIGCHLD
import sys


def read_pipelines(fname):
    absdir=os.path.dirname(os.path.abspath(fname))
    with open(fname) as f:
        pipelines=yaml.load(f, Loader=yaml.BaseLoader)
    for pipeline_name,component_list in pipelines.items():
        new_component_list=[c.format(thisdir=absdir) for c in component_list]
        pipelines[pipeline_name]=new_component_list
    return pipelines


class Pipeline:

    def __init__(self, steps, extra_args=None):
        """ """
        self.ctx=multiprocessing.get_context()
        self.job_counter=0
        self.done_jobs={}
        self.max_q_size=5
        self.q_in=self.ctx.Queue(self.max_q_size) #where to send data to the whole pipeline
        self.q_out=self.q_in #where to receive data from the whole pipeline
        self.modules = []
        self.processes=[]
        self.large_jobs = []

        for mod_name_and_params in steps:
            self.add_step(mod_name_and_params, extra_args)
        try:
            signal(SIGCHLD, self.handle_sigchld)
        except ValueError:
            print(
                "Warning: could not install SIGCHLD handler. "
                "Pipeline will not terminate if children exit abnormally."
            )

    def handle_sigchld(self, signum, frame):
        while 1:
            pid, exitno = os.waitpid(0, os.WNOHANG)
            if pid == 0:
                return
            if exitno == 0:
                continue
            for module, process in zip(self.modules, self.processes):
                if process.pid != pid:
                    continue
                print(
                    f"Error: pipeline stage died with exit code {exitno}: {module}",
                    file=sys.stderr,
                    flush=True
                )
                sys.exit(-64)

    def join(self):
        for p in self.processes:
            p.join()

    def is_alive(self):
        for p in self.processes:
            if not p.is_alive():
                return False
        return True

    def add_step(self,module_name_and_params, extra_args):
        config=module_name_and_params.split()
        module_name=config[0]
        params=config[1:]

        # collect extra arguments from command line meant for this particular module
        if extra_args is not None: 
            for _name, _value in extra_args.__dict__.items():
                if _name.startswith(module_name):
                    _modname,_argname=_name.split(".",1) # for example lemmatizer_mod.gpu
                    params.append("--"+_argname)
                    params.append(str(_value))

        mod=importlib.import_module("tnparser."+module_name)
        step_in=self.q_out
        self.q_out=self.ctx.Queue(self.max_q_size) #new pipeline end
        args=mod.argparser.parse_args(params)
        process=self.ctx.Process(target=mod.launch,args=(args,step_in,self.q_out))
        process.daemon=True
        process.start()
        self.modules.append(module_name_and_params)
        self.processes.append(process)

    def send_final(self):
        self.q_in.put(("FINAL",""))
        
    def put(self,txt, final=False):
        """Start parsing a job, return id which can be used to retrieve the result"""
        batch_id=hashlib.md5((str(random.random())+txt).encode("utf-8")).hexdigest()
        self.q_in.put((batch_id,txt)) #first job of 1 total
        self.job_counter+=1
        if final:
            self.q_in.put(("FINAL",""))
        return batch_id

    def get(self,batch_id):
        if batch_id is None: #get any next batch, don't care about batch_id
            _,finished=self.q_out.get()
            self.job_counter-=1
            return finished
        elif batch_id in self.done_jobs:
            self.job_counter-=1
            return self.done_jobs.pop(batch_id)
        else:
            #get the next job, maybe it's the one?
            finished_id,finished=self.q_out.get()
            if finished_id==batch_id:
                self.job_counter-=1
                return finished
            else: #something got done, but it's not the right one
                self.done_jobs[finished_id]=finished
                return None #whoever asked will have to ask again

    def empty_q_out(self):
        try:
            while True:
                # get all the nowait jobs and set as finished
                finished_id, finished = self.q_out.get_nowait()
                self.done_jobs[finished_id] = finished
        except:
            pass

    def parse(self,txt):
        """
        return res if queue is not full, else return False
        """
        # Make sure that the request will not be blocked for a long time
        # Ongoing jobs + 1 should less than 5, or return False
        if self.job_counter + 1 - len(self.done_jobs) > 5:
            self.empty_q_out()
            return False

        job_id=self.put(txt)
        while True:
            res=self.get(job_id)
            if res is None:
                time.sleep(0.1)
            else:
                break
        return res

    def chunk_plain_text(self, txt, max_char=15000):
        '''
        Divide large plain text into chunks
        '''
        ck_num = int(len(txt) / max_char)
        # list of chunks
        chunks = []
        # offsets of chunks
        offsets = [[0, 0]]
        for i in range(ck_num):
            # reverse the chunk and find the index of end of sentence/word
            tmp_str = txt[offsets[i][0]:(i + 1) * max_char][::-1]
            eos_index = tmp_str.index('.') if '.' in tmp_str else tmp_str.index(' ')
            offsets[i][1] = len(tmp_str) - eos_index + offsets[i][0]
            # the eos_index is the start index of the next
            offsets.append([offsets[i][1], offsets[i][1]])
        # add the remaining words to the last chunk
        if offsets[ck_num][0] != len(txt):
            offsets[ck_num - 1][1] = len(txt)
        # split the txt using the offsets list
        for offset in offsets[:-1]:
            chunks.append(txt[offset[0]:offset[1]].strip())
        return chunks

    def parse_large_txt(self, large_txt):
        """
        The function divide the txt into small chunks and add chunks to the job queue
        large_txt: string object but a large one
        return: Job id if queue not full, False if queue is full
        """
        chunks = self.chunk_plain_text(large_txt)

        # Make sure that the request will not be blocked for a long time
        # Ongoing jobs + potential jobs should less than 8, or return False
        if len(chunks) + self.job_counter - len(self.done_jobs) > 8:
            self.empty_q_out()
            return False

        job_ids = []
        for chunk in chunks:
            job_ids.append(self.put(chunk))
        large_job_id = '%'.join(job_ids)
        self.large_jobs.append(large_job_id)
        return large_job_id

    def report_large_job(self, job_id):
        """
        Given a job_id, this function can return its progress,
        if done, return the result,
        if doesn't find the job_id, return False
        """
        self.empty_q_out()
        # Either wrong job_id or already retrieved the result
        if job_id not in self.large_jobs:
            return [False]
        # get job_ids from the large_job_id
        job_ids = self.large_jobs[self.large_jobs.index(job_id)].split('%')
        ct = 0
        # get progress report
        for idx in job_ids:
            if idx in self.done_jobs: ct += 1
        # all jobs are done
        if ct == len(job_ids):
            res = []
            for idx in job_ids:
                res.append(self.done_jobs.pop(idx))
                self.job_counter-=1
            self.large_jobs.remove(job_id)
            # TODO Meta data in return, i.e, wrong sent_id
            return [True, res]
        else:
            return [False, "Progress: %d percent"%(100*ct/len(job_ids))]

    def parse_batched(self,inp,):
        """inp: is a file-like object with input data
           yield_res: 
           """
        pass
           

