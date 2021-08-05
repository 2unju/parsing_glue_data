import csv
import sys
import argparse

TASKS = ["CoLA", "SST-2", "QQP", "MNLI", "STS-B", "QNLI", "RTE", "WNLI"]
# TASKS = ["SST-2", "QQP", "MNLI", "QNLI"]
COLINTASK = {
    "CoLA": ['source', 'label', 'author', 'sentence'],
    "MNLI": ['index', 'promptID', 'pairID', 'genre', 'sentence1_binary_parse', 'sentence2_binary_parse', 'sentence1_parse', 'sentence2_parse', 'sentence1', 'sentence2', 'label1', 'label2', 'label3', 'label4', 'label5', 'label'],
    "QNLI": ['index', 'sentence1', 'sentence2', 'label'],
    "QQP": ['id', 'qid1', 'qid2', 'sentence1', 'sentence2', 'label'],
    "RTE": ['index', 'sentence1', 'sentence2', 'label'],
    "SST-2": ['sentence', 'label'],
    "STS-B": ['index', 'genre', 'filename', 'year', 'old_index', 'source1', 'source2', 'sentence1', 'sentence2', 'label'],
    "WNLI": ['index', 'sentence1', 'sentence2', 'label']
}
LABEL = {
    'entailment': '0',
    'not_entailment': '1',
    'neutral': '1',
    'contradiction': '2'
}

def single_quote(task, before, after):
    idx = COLINTASK[task].index('sentence')
    labelidx = COLINTASK[task].index('label')

    for i in range(len(after)):
        try:
            a = after[i].split('\t')
            b = before[i].split('\t')
        except:
            print('Split Error')
            continue

        try:
            if b[idx] != a[0]:
                print('{} : {} / {}'.format(i, b[idx], a[0]))
                return False
            elif b[labelidx] != a[1]:
                print('{} : {} / {}'.format(i, b[labelidx], a[1]))
                return False
        except:
            print(a, end=' ')
            print(b)

    return True

def double_quote(task, file, before, after):
    idx1 = COLINTASK[task].index('sentence1')
    idx2 = COLINTASK[task].index('sentence2')
    if task == 'MNLI' and file == 'train':
        labelidx = COLINTASK[task].index('label2')
    else:
        labelidx = COLINTASK[task].index('label')

    for i in range(len(after)):
        if task == 'MNLI' and i == 119:
            continue

        try:
            a = after[i].split('\t')
            b = before[i].split('\t')
        except:
            print('Split Error')
            continue

        try:
            if b[idx1] != a[0]:
                print('{} : {} / {}'.format(i, b[idx1], a[0]))
                return False
            elif b[idx2] != a[1]:
                print('{} : {} / {}'.format(i, b[idx2], a[1]))
                return False
            else:
                if task == 'MNLI' or task == 'QNLI':
                    if LABEL[b[labelidx]] != a[2]:
                        print('{} : {} / {}'.format(i, LABEL[b[labelidx]], a[2]))
                        return False
                else:
                    if b[labelidx] != a[2]:
                        print('{} : {} / {}'.format(i, b[labelidx], a[2]))
                        return False
        except:
            print(a, b)
    return True

def is_equal(task, filename):
    '''
    sst-2, qqp, mnli, qnli
    '''
    path = './parsing_data/' + task + '/' + filename + '.tsv'
    with open(path, encoding='utf-8') as f:
        data = f.read()
    after = data.split('\n')

    path = './' + task + '/' + filename + '.tsv'
    with open(path, encoding='utf-8') as f:
        data = f.read()
    before = data.split('\n')
    if task != 'CoLA':
        before = before[1:]

    # if len(before) != len(after):
    #     return False

    if task == 'SST-2' or task == 'CoLA':
        return single_quote(task, before, after)
    else:
        return double_quote(task, filename, before, after)

def get_tasks(task_names):
    task_names = task_names.split(',')
    if "all" in task_names:
        tasks = TASKS
    else:
        tasks = []
        for task_name in task_names:
            assert task_name in TASKS, "Task %s not found!" % task_name
            tasks.append(task_name)
    return tasks

def main(argument):
    parser = argparse.ArgumentParser()
    parser.add_argument('--tasks', help='tasks to download data for as a comma separated string',
                        type=str, default='all')
    args = parser.parse_args(argument)

    tasks = get_tasks(args.tasks)

    for task in tasks:
        print()
        print(task)
        if task == 'MNLI':
            print(is_equal(task, 'train'))
            print(is_equal(task, 'dev_matched'))
            print(is_equal(task, 'dev_mismatched'))
        else:
            print(is_equal(task, 'train'))
            print(is_equal(task, 'dev'))


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))