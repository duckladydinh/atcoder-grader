import argparse
import json
import os
import subprocess
from typing import List

import requests
from loguru import logger

ATCODER_TESTS_HOME = 'https://www.dropbox.com/sh/arnpe0ef5wds8cv/AAAk_SECQ2Nc6SVGii3rHX6Fa?dl=0'

DROPBOX_API_LIST_FOLDER = 'https://api.dropboxapi.com/2/files/list_folder'

DROPBOX_API_GET_SHARED_LINK_FILE = 'https://content.dropboxapi.com/2/sharing/get_shared_link_file'

DROPBOX_AUTH_TOKEN = '<No Access Token Provided>'


def get_test_names(contest: str, problem: str) -> List[str]:
    input_path = '/{}/{}/in'.format(contest, problem)

    header = {
        'Authorization': 'Bearer {}'.format(DROPBOX_AUTH_TOKEN),
        'Content-Type': 'application/json'
    }

    payload = {
        'path': input_path,
        'shared_link': {
            'url': ATCODER_TESTS_HOME
        }
    }

    res = requests.post(DROPBOX_API_LIST_FOLDER, headers=header, json=payload).json()
    entries = res['entries']
    test_names = []

    for entry in entries:
        name: str = entry['name']
        if name.endswith('.txt'):
            test_names.append(name)

    return test_names


def get_test_data_bytes(contest: str, problem: str, test_name: str, is_input: bool) -> bytes:
    input_path = '/{}/{}/{}/{}'.format(contest, problem, 'in' if is_input else 'out', test_name)

    header = {
        'Authorization': 'Bearer {}'.format(DROPBOX_AUTH_TOKEN),
        'Dropbox-API-Arg': json.dumps({
            'url': ATCODER_TESTS_HOME,
            'path': input_path
        })
    }

    res = requests.post(DROPBOX_API_GET_SHARED_LINK_FILE, headers=header)
    return res.content


def download_data(location, contest, problem, is_input):
    test_names = get_test_names(contest, problem)
    for name in test_names:
        with open('{}/{}'.format(location, name), 'wb') as f:
            data = get_test_data_bytes(contest, problem, name, is_input)
            f.write(data)
            f.close()


def prepare_data(contest, problem):
    for typ in ['in', 'out']:
        home = '/tmp/atcoder/{}/{}/{}'.format(contest, problem, typ)
        is_input = typ == 'in'

        if not os.path.exists(home):
            os.makedirs(home)

            logger.info('Downloading data into {}.'.format(home))
            download_data(home, contest, problem, is_input)
            logger.info('Data downloaded into {}.'.format(home))
        else:
            logger.info('{} exists. Consider deleting this folder if fresh data is necessary!'.format(home))


def run_command(cmd: str) -> str:
    return subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read().decode()


def grade(program, contest, problem):
    test_names = get_test_names(contest, problem)
    prepare_data(contest, problem)

    tot = len(test_names)
    cnt = 0

    for i, name in enumerate(test_names):
        res = run_command(
            'python {0} < /tmp/atcoder/{1}/{2}/in/{3}'.format(program, contest, problem, name))
        res = ''.join([line.strip() for line in res.split('\n')])
        with open('/tmp/atcoder/{0}/{1}/out/{2}'.format(contest, problem, name)) as f:
            ans = ''.join([line.strip() for line in f.readlines()])
            f.close()

        equivalent = res.strip() == ans.strip()
        cnt += equivalent

        logger.info(
            'Test {} ({}) is {}. Total = {}/{}'.format(i + 1, name, 'correct' if equivalent else 'incorrect', cnt, tot))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--program', required=True)
    parser.add_argument('--contest', required=True)
    parser.add_argument('--problem', required=True)
    parser.add_argument('--token', required=True)

    args = parser.parse_args()

    DROPBOX_AUTH_TOKEN = args.token
    print(DROPBOX_AUTH_TOKEN)

    grade(program=args.program, contest=args.contest, problem=args.problem)
