#!/usr/bin/env python
from config import user, branches
import sys
from collections import defaultdict
from pycircleci.api import Api, CIRCLE_TOKEN, CIRCLE_API_URL

basename = sys.argv[1]

alias = {'pre-commit_tests': 'j8',
         'java11_pre-commit_tests': 'j11',
         'java8_pre-commit_tests': 'j8'}

def mk_branches(name):
    for b in branches:
        yield '{}-{}'.format(name, b)

circle = Api(token=CIRCLE_TOKEN, url=CIRCLE_API_URL)
cassandra = circle.get_project_pipelines(user, "cassandra")
wanted_flows = defaultdict(list)

for pipe in cassandra:
    if pipe['vcs']['branch'] in mk_branches(basename):
        flows = circle.get_pipeline_workflow(pipe['id'])
        if pipe['vcs']['branch'] in wanted_flows:
            # if more than one 'set' of flows for a branch, tiebreak on number for the newest
            if wanted_flows[pipe['vcs']['branch']][0]['pipeline_number'] > flows[0]['pipeline_number']:
                continue
        for flow in flows:
            if 'pre-commit' in flow['name']:
                    wanted_flows[pipe['vcs']['branch']].append(flow)
                    #print(pipe['vcs']['branch'], flow)

for branch, flows in sorted(wanted_flows.items()):
    bid = branch.removeprefix(basename+'-')
    print(bid)
    for i, flow in enumerate(reversed(flows)): # reversing is a hack to get j8 first
        name = alias[flow['name']]
        print('\t', name, '\t', 'https://app.circleci.com/pipelines/github/{}/cassandra/{}/workflows/{}'.format(user, flow['pipeline_number'], flow['id']))
        print('\t\t', flow['status'])
