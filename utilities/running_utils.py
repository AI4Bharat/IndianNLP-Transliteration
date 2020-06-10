import enum
import sys
import os
import json
import torch
import seaborn as sns
import matplotlib.pyplot as plt

class RunMode(enum.Enum):
    train = "training"
    infer = "inference"
    test  = "testing"

def load_pretrained(model, weight_path):
    if not weight_path:
        return model

    pretrain_dict = torch.load(weight_path)
    model_dict = model.state_dict()
    pretrain_dict = {k: v for k, v in pretrain_dict.items() if k in model_dict}
    print("Pretrained layers Loaded:", pretrain_dict.keys())
    model_dict.update(pretrain_dict)
    model.load_state_dict(model_dict)

    return model


def count_train_param(model):
    train_params_count = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print('The model has {} trainable parameters'.format(train_params_count))
    return train_params_count


def accuracy_score(pred_tnsr, tgt_tnsr):
    '''Simple accuracy calculation for TRAINING phase
    pred_tnsr: torch tensor :shp: (batch, seq_len)
    tgt_tnsr: torch tensor :shp: (batch, voc_size, seq_len)
    '''
    pred_seq = torch.argmax(pred_tnsr, dim=1)
    batch_sz = pred_seq.shape[0]
    crt_cnt = 0
    for i in range(batch_sz):
        if torch.equal(pred_seq[i,:], tgt_tnsr[i, :]):
            crt_cnt += 1
    return torch.tensor(crt_cnt/batch_sz)

def attention_weight_plotter(out_word, in_word, attention_array, save_path = ""):
    '''
    Plot heat map of attention weights
    '''
    font_sz = 10
    plt.figure(figsize = (10,7))
    sns.set(font = "Lohit Devanagari", )
    conf_plot = sns.heatmap(attention_array, annot=False,
                      xticklabels = ["$"]+ list(in_word) + ["#"],
                      yticklabels = out_word)

    conf_plot.yaxis.set_ticklabels(conf_plot.yaxis.get_ticklabels(),
                                    rotation=0, fontsize = font_sz)
    conf_plot.xaxis.set_ticklabels(conf_plot.xaxis.get_ticklabels(),
                                    rotation=0, fontsize = font_sz)
    plt.xlabel('Pred: '+ out_word, fontsize = font_sz)

    conf_plot.figure.savefig( save_path + "/"+in_word+"_attention.png")

    plt.clf()





