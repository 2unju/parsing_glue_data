import csv
import sys
import argparse
import pandas as pd
import tqdm

TASKS = ["CoLA", "SST-2", "QQP", "MNLI", "STS-B", "QNLI", "RTE", "WNLI", "MRPC"]
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

def transfer_label(task, label):
    '''
    QNLI / RTE / MNLI
    QNLI / RTE : entailment is 0, not entailment is 1
    MNLI : entailment is 0, neutral is 1, contradiction is 2
    '''

    if task == 'MNLI':
        if label == 'contradiction':
            label = 2
        elif label == 'neutral':
            label = 1
        else:
            label = 0
    elif task == 'RTE' or task == 'QNLI':
        label = 1 if label == 'not_entailment' else 0

    return label

def parsing(task, filename):
    '''
    NOT MRPC
    '''
    data_list = []
    path = './' + task + '/' + filename + '.tsv'
    with open(path, encoding='utf-8') as f:
        data = f.read()
    data = data.split('\n')
    col = data[0].split('\t')

    if 'test' in filename:
        if task == 'STS-B' or task == 'MNLI':
            for line in data[1:]:
                line = line.split('\t')
                try:
                    tmp = [line.pop(-2), line.pop(-1)]
                    data_list.append(tmp)
                except:
                    print(line)
        else:
            for line in data[1:]:
                line = line.split('\t')
                line.pop(0)
                data_list.append(line)
    else:
        if task == 'CoLA' or task == 'SST-2':
            idx1 = COLINTASK[task].index('sentence')
            idx2 = None
        else:
            idx1 = COLINTASK[task].index('sentence1')
            idx2 = COLINTASK[task].index('sentence2')

        if task == 'MNLI' and filename == 'train':
            labelidx = COLINTASK[task].index('label2')
        else:
            labelidx = COLINTASK[task].index('label')

        if task == 'CoLA' and filename != 'test':
            data_list.append([col[idx1], col[labelidx]])

        for line in data[1:]:
            line = line.split('\t')

            if idx2 == None:
                try:
                    data_list.append([line[idx1], transfer_label(task, line[labelidx])])
                except:
                    print(line)
            else:
                try:
                    data_list.append([line[idx1], line[idx2], transfer_label(task, line[labelidx])])
                except:
                    print(line)
                    if line[0] == '119':
                        data_list.append([line[idx1].split('" ')[0], line[idx1].split('" ')[1], transfer_label(task, line[idx2])])

    path = './parsing_data/' + task + '/' + filename + '.tsv'
    with open(path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter='\t', quoting=csv.QUOTE_NONE, quotechar=None)
        writer.writerows(data_list)

def parsing_MRPC(filename):
    data_list = []
    path = './MRPC/' + filename + '.tsv'
    with open(path, encoding='utf-8') as f:
        data = f.read()
    data = data.split('\n')
    for line in data:
        line = line.split('\t')
        try:
            data_list.append([line[3], line[4], line[0]])
        except:
            print(line)

    path = './parsing_data/MRPC/' + filename + '.tsv'
    with open(path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter='\t', quoting=csv.QUOTE_NONE, quotechar=None)
        writer.writerows(data_list)

def main(argument):
    parser = argparse.ArgumentParser()
    parser.add_argument('--tasks', help='tasks to download data for as a comma separated string',
                        type=str, default='all')
    args = parser.parse_args(argument)

    tasks = get_tasks(args.tasks)

    for task in tasks:
        print(task)
        if task == 'MRPC':
            parsing_MRPC('train')
            parsing_MRPC('validation')
            parsing_MRPC('test')
        elif task == 'MNLI':
            parsing(task, 'train')
            parsing(task, 'dev_matched')
            parsing(task, 'dev_mismatched')
            parsing(task, 'test_matched')
            parsing(task, 'test_mismatched')
        else:
            parsing(task, 'train')
            parsing(task, 'dev')
            parsing(task, 'test')

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))