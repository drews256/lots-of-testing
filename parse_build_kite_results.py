import requests
import json
import pdb
import os
import csv
from git import Repo
import spacy
from spacy.matcher import Matcher
import re
# feature generation
#  1. Size of diff
#  2. Churn, we should figure out churn rate of change so files that are more recently churning more often need wide coverage
#  3. code ownership information, how many commits does this author have?
#  4. History of recent test runs (has this file been changed recently with a failing/passed test suite?)
#  5. Topology of test run -> just map test names for now?
#  6. Were specific tests modified for this specific change?

# Size of Diff
builds = range(58436, 58441) # 73380)

testing_csv = open('rails_testing.csv', 'w', newline='')
testwriter = csv.writer(testing_csv, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
testwriter.writerow(['file_name', 'additions', 'deletions', 'sha', 'test_run_id', 'test_state', 'result', 'issue_with_test'])

repo = Repo('.')
the_git = repo.git
available_git_files = the_git.ls_files()
files_list = available_git_files.split('\n')
all_patterns = []
for file_name in files_list:
    all_patterns.append({"LOWER": file_name.split('/')[-1]})
    all_patterns.append({"LOWER": file_name.split('/')[-1] + ":"})
    all_patterns.append({"LOWER": '/' + file_name.split('/')[-1]})
    all_patterns.append({"LOWER": file_name.split('/')[-1] + '/'})
    all_patterns.append({"LOWER": '/' + file_name.split('/')[-1] + '/'})
    all_patterns.append({"LOWER": '"' + file_name.split('/')[-1]})
    all_patterns.append({"LOWER": file_name.split('/')[-1] + '"'})
    all_patterns.append({"LOWER": '"' + file_name.split('/')[-1] + '"'})
    all_patterns.append({"LOWER": '\'' + file_name.split('/')[-1]})
    all_patterns.append({"LOWER": file_name.split('/')[-1] + '\''})
    all_patterns.append({"LOWER": '\'' + file_name.split('/')[-1] + '\''})

nlp = spacy.load("en_core_web_sm", disable=['ner', 'parser', 'tagger', 'textcat'])

def failed_jobs_failed_tests(job):
    artifacts_file = open(f'../aspen/rails_test_runs/{build_number}/artifacts/{job[2]}.json')
    art_file_json = artifacts_file.read()
    artifacts_json = json.loads(art_file_json)
    if len(artifacts_json) == 0:
        next
        artifacts_file.close()
    else:
        failed_paths = list(map(lambda failed_job_info : { 'url': failed_job_info['url'], 'file_size': failed_job_info['file_size']}, artifacts_json))
        artifacts_file.close()
        for path in failed_paths:
            if path['file_size'] == '0 Bytes':
                continue

            response = requests.get(f'https://buildkite.com{path["url"]}')
            test_results = response.text
            #  print(test_results)

            if len(test_results) == 0:
                continue


            matcher = Matcher(nlp.vocab)
            #  Add match ID "HelloWorld" with no callback and one pattern
            for pattern in all_patterns:
                matcher.add(pattern["LOWER"], None, [pattern])

            print('nlp start')
            print(nlp.pipe_names)
            doc = nlp(test_results, disable=['ner', 'parser', 'tagger', 'textcat'])
            matches = matcher(doc)
            print('>>>>>>>>>>>>> matches <<<<<<<<<<<<<<')
            text_values = []
            for match_id, start, end in matches:
                string_id = nlp.vocab.strings[match_id]  # Get string representation
                span = doc[start:end]  # The matched span
                text_values.append(span.text)

            return list(filter(lambda text_value : re.search('_test.rb', text_value), set(text_values)))


for build_number in builds:
    print(f'Build -------------------------> {build_number} -----------------------')
    try:
        results_file = open(f'../aspen/rails_test_runs/{build_number}/results.json', "r")
        results = results_file.read()
        results_file.close()
        result_json = json.loads(results)

        commit_id = result_json['commit_id']
        state = result_json['state']
        test_run_id = result_json['id']

        jobs = result_json['jobs']

        job_state = list(map(lambda job : [job['state'], job['passed'], job['id']], jobs))

        failed_jobs = list(filter(lambda job_state : job_state[1] == False, job_state))

        repo = Repo('.')
        the_git = repo.git
        log = the_git.diff(f'{commit_id}', f'{commit_id}~1', '--numstat')
        strings = str.splitlines(log)
        individual_split_strings = list(map(lambda string_to_split : string_to_split.split('\t'), strings))

        for failed_job in failed_jobs:
            found_test_files = failed_jobs_failed_tests(failed_job)
            if found_test_files:
                for results in individual_split_strings:
                    for test_file_name in found_test_files:
                        testwriter.writerow([results[2], results[0], results[1], commit_id, test_run_id, state, test_file_name])

    except Exception as e:
        print(e)
        continue
