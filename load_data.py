import json
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from settings import DATA_DIR


def load_dataset(data_dir=DATA_DIR, filename="training_set.json"):
    """
    Load the dataset
    @param data_dir: data directory
    @param filename: dataset JSON file
    @return: dataframe
    """

    with open(f"{data_dir}/{filename}") as f:
        data = json.load(f)

    dataframe_rows = []
    for d in data["data"]:
        title = d["title"]
        paragraphs = d["paragraphs"]
        for p in paragraphs:
            context = p["context"]
            qas = p["qas"]
            for q in qas:
                answers = q["answers"]
                question = q["question"]
                qid = q["id"]
                for a in answers:
                    answer_start = a["answer_start"]
                    text = a["text"]

                    dataframe_row = {
                        "title": title,
                        "context": context,
                        "answer_start": answer_start,
                        "text": text,
                        "question": question,
                        "id": qid
                    }
                    dataframe_rows.append(dataframe_row)

    return pd.DataFrame(dataframe_rows)


def load_dataset_without_answer(path):
    """
    Load dataset without answers
    @param path: dataset file path
    @return: dataset
    """
    with open(path) as f:
        data = json.load(f)

    dataframe_rows = []
    for d in data["data"]:
        title = d["title"]
        paragraphs = d["paragraphs"]
        for p in paragraphs:
            context = p["context"]
            qas = p["qas"]
            for q in qas:
                question = q["question"]
                qid = q["id"]
                dataframe_row = {
                    "title": title,
                    "context": context,
                    "question": question,
                    "id": qid
                }
                dataframe_rows.append(dataframe_row)

    return pd.DataFrame(dataframe_rows)

'''
def remove_error_rows(dataframe, path, filename):
    """
    Remove rows containing errors from the dataset
    @param dataframe: dataset
    @param path: path of the file containing error indices
    @param filename: name of the file containing error indices
    @return: dataframe containing only errors
    """
    with open(f"{path}/{filename}", encoding='utf-8') as f_errors:
        errors = f_errors.read().splitlines()
    dataframe = dataframe[dataframe['id'].isin(errors)]
    dataframe.reset_index(inplace=True, drop=True)
    return dataframe


def remove_2occ_rows(dataframe):
    """
    Remove rows containing more instances of the proposed answer
    @param dataframe: dataset
    @return: dataset containing only rows containing multiple instances of the answer
    """
    occurrences = dataframe.apply(lambda x: x.context.count(x.text), axis=1)
    idx_multiple_occurrences = np.where(occurrences > 1)
    dataframe = dataframe.loc[idx_multiple_occurrences]
    dataframe.reset_index(inplace=True, drop=True)
    return dataframe
'''


def remove_rows(dataframe):
    """
    Remove rows containing errors or more instances of the proposed answer
    @param dataframe: dataset
    @return: test dataset
    """
    # dataset with multiple occurrences of the answer
    occurrences = dataframe.apply(lambda x: x.context.count(x.text), axis=1)
    idx_multiple_occurrences = np.where(occurrences > 1)
    ts_df1 = dataframe.loc[idx_multiple_occurrences]
    ts_df1.reset_index(inplace=True, drop=True)

    ts_df2 = dataframe.loc[~ dataframe.id.isin(ts_df1.id)]
    ts_df2.reset_index(inplace=True, drop=True)
    # dataset with errors
    idx_errors = ts_df2.apply(lambda row: row.answer_start != row.context.find(row.text), axis=1)
    ts_df2 = ts_df2.loc[idx_errors]
    ts_df2.reset_index(inplace=True, drop=True)

    ts_df = pd.concat([ts_df1, ts_df2])
    ts_df.reset_index(inplace=True, drop=True)
    return ts_df


def split_test_set(dataframe):
    """
    Split training and test set
    @param dataframe: dataset
    @return: training dataset, test dataset
    """
    # ts_df1 = remove_error_rows(dataframe, path="./data", filename="error IDs.txt")
    ts_df = remove_rows(dataframe)
    #ts_df = pd.concat([ts_df1, ts_df2])
    #ts_df.reset_index(inplace=True, drop=True)

    # reset indices
    dataframe = dataframe[~dataframe['id'].isin(ts_df.id)]
    dataframe.reset_index(inplace=True, drop=True)
    return dataframe, ts_df


def split_validation_set(dataframe, rate):
    """
    Split dataframe in training and validation set
    nb: records with the same title are kept together
    @param dataframe:
    @param rate: validation / training ratio
    @return:
    """
    # split
    tr_title, val_title = train_test_split(np.unique(dataframe.title), test_size=rate, random_state=0)
    tr_idx = np.isin(dataframe.title, tr_title)
    val_idx = np.isin(dataframe.title, val_title)

    # reset indices
    tr_df = dataframe.loc[tr_idx]
    tr_df.reset_index(inplace=True, drop=True)
    val_df = dataframe.loc[val_idx]
    val_df.reset_index(inplace=True, drop=True)
    return tr_df, val_df
