import requests
import json
import pdb
import os
from git import Repo

builds = range(58431, 73380)
for build_number in builds:
    if os.path.exists(f'./rails_test_runs/{build_number}'):
        print('already got data')
        continue

    if not os.path.exists('./rails_test_runs'):
        os.mkdir(f'./rails_test_runs')

    response = requests.get(f'https://buildkite.com/rails/rails/builds/{build_number}.json')

    if response.status_code == 403:
        print('skipped')
        continue

    print(f'running! {build_number}')
    buildkite_json = response.json()

    commit_id = buildkite_json['commit_id']
    jobs = buildkite_json['jobs']
    commit_url = buildkite_json['commit_url']

    if not os.path.exists(f'./rails_test_runs/{build_number}'):
        os.mkdir(f'./rails_test_runs/{build_number}')

    results_file = open(f'./rails_test_runs/{build_number}/results.json', "w+")
    results_file.write(json.dumps(buildkite_json))
    results_file.close()

    diff_response = requests.get(f'{commit_url}.diff')

    diff_file = open(f'./rails_test_runs/{build_number}/diff.json', "w+")
    diff_file.write(diff_response.text)
    diff_file.close()

    if not os.path.exists(f'./rails_test_runs/{build_number}/artifacts'):
        os.mkdir(f'./rails_test_runs/{build_number}/artifacts')

    def get_values_from_job(job):
        job_id = job['id']
        job_passed = job['passed']
        artifacts_response = requests.get(f'https://buildkite.com/organizations/rails/pipelines/rails/builds/58431/jobs/{job_id}/artifacts.json')
        artifacts = artifacts_response.json()
        f = open(f'./rails_test_runs/{build_number}/artifacts/{job_id}.json', "w+")
        f.write(json.dumps(artifacts))
        f.close()

        return {'job_id': job_id, 'job_passed': job_passed, 'artifacts': json.dumps(artifacts)}

    artifacts_for_jobs = list(map(get_values_from_job, jobs))
