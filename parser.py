import pandas as pd
import csv
import sys
import argparse
from tqdm import tqdm

TASKS = ["CoLA", "SST-2", "QQP", "STS-B", "QNLI", "RTE", "WNLI"]
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

def transfer_label(task, data):
    '''
    QNLI / RTE / MNLI
    QNLI / RTE : entailment is 0, not entailment is 1
    MNLI : entailment is 0, neutral is 1, contradiction is 2
    '''
    if task == 'MNLI':
        label = pd.DataFrame(columns=['label'])
        for element in data['label']:
            if element == 'contradiction':
                label.append(pd.Series(2), ignore_index=True)
            elif element == 'neutral':
                label.append(pd.Series(1), ignore_index=True)
            else:
                label.append(pd.Series(0), ignore_index=True)

        print(label)
        exit()
    else:
        label = pd.DataFrame([1 if element == 'not_entailment' else 0 for element in data['label']])
    return label

def read_tsv(task, data):
    data_list = []
    data = data.split('\n')
    data = data[1:]
    for t in data:
        t = t.split('\t')
        data_list.append(t)

    data_df = pd.DataFrame(columns=COLINTASK[task])
    for l in tqdm(data_list):
        try:
            data_df = data_df.append(pd.Series(l, index=data_df.columns), ignore_index=True)
        except:
            print(l)

    return data_df

def parsing(task):
    with open('./' + task + '/train.tsv', encoding='utf-8') as f:
        data = f.read()
    train_df = read_tsv(task, data)

    if task == 'MNLI':
        with open('./' + task + './dev_matched.tsv', encoding='utf-8') as f:
            data1 = f.read()
        with open('./' + task + './dev_mismatched.tsv', encoding='utf-8') as f:
            data2 = f.read()
        data = data1 + data2
    else:
        with open('./' + task + '/dev.tsv', encoding='utf-8') as f:
            data = f.read()
    dev_df = read_tsv(task, data)

    if 'sentence1' in COLINTASK[task]:
        if task == 'QNLI' or task == 'RTE' or task == 'MNLI':
            train = pd.concat([train_df['sentence1'], train_df['sentence2'], transfer_label(task, train_df['label'])], axis=1, ignore_index=True)
            dev = pd.concat([dev_df['sentence1'], dev_df['sentence2'], transfer_label(task, dev_df['label'])], axis=1, ignore_index=True)
        else:
            train = pd.concat([train_df['sentence1'], train_df['sentence2'], train_df['label']], axis=1, ignore_index=True)
            dev = pd.concat([dev_df['sentence1'], dev_df['sentence2'], dev_df['label']], axis=1, ignore_index=True)
    else:
        train = pd.concat([train_df['sentence'], train_df['label']], axis=1, ignore_index=True)
        dev = pd.concat([dev_df['sentence'], dev_df['label']], axis=1, ignore_index=True)

    train.to_csv('./parsing_data/' + task + '/train.tsv', sep='\t', header=False, index=False)
    dev.to_csv('./parsing_data/' + task + '/dev.tsv', sep='\t', header=False, index=False)

def main(argument):
    parser = argparse.ArgumentParser()
    parser.add_argument('--task', type=str, default='all')
    args = parser.parse_args(argument)

    tasks = get_tasks(args.tasks)

    for task in tasks:
        print(task)
        parsing(task)

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))