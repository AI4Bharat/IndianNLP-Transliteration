import os
import sys
import utilities.lang_data_utils as lutl
import utilities.running_utils as rutl

''' VacabSanitizer usage
voc_sanitize = lutl.VocabSanitizer("data/X_word_list.json")
result = voc_sanitize.reposition(result)
'''

hi_glyph = lutl.GlyphStrawboss("hi")
en_glyph = lutl.GlyphStrawboss("en")
# hi_vocab = lutl.VocableStrawboss("data/konkani/gom_all_words_sorted.json")

device = "cpu"

##=============== Models =======================================================
import torch

from tasks.rnn_xlit_runner import model
weight_path = "hypotheses/Training_gom_115/weights/Training_gom_115_model.pth"

weights = torch.load( weight_path, map_location=torch.device(device))
model.load_state_dict(weights)
model.eval()

# ------------- Correction model -----------------------------------------------
'''
from tasks.corr_xlit_runner import corr_model
corr_weight_path = "hypotheses/Training_mai_116_corr3_a/weights/Training_mai_116_corr3_a_corrnet.pth"

corr_weights = torch.load( corr_weight_path, map_location=torch.device(device))
corr_model.load_state_dict(corr_weights)
corr_model.eval()

    c_out_list = [ corr_model.inference(out) for out in out_list]
    c_result = [ hi_vocab.get_word(out.cpu().numpy()) for out in c_out_list]
'''

from tasks.emb_xlit_runner import emb_model
emb_weight_path = "hypotheses/Training_gom_emb2/weights/Training_gom_emb2_embnet.pth"

emb_weights = torch.load( emb_weight_path, map_location=torch.device(device))
emb_model.load_state_dict(emb_weights)
emb_model.eval()

### -------------- Annoy object ------------------------------------------------
import utilities.embed_utils as eutl

# eutl.create_annoy_index_from_model(
#         voc_json_file = "data/konkani/gom_all_words_sorted.json",
#         glyph_obj = hi_glyph,
#         model_func = emb_model.get_word_embedding,
#         save_prefix= 'hypotheses/Training_gom_emb2/emb2')
# sys.exit()

annoy_obj = eutl.AnnoyStrawboss(
                voc_json_file = "data/konkani/gom_all_words_sorted.json",
                annoy_tree_path = "hypotheses/Training_gom_emb2/Gom_emb2_word_vec.annoy",
                vec_sz =300)

##==============================================================================

def pred_contrive(corr_lst, pred_lst):
    out =[]
    for l in corr_lst:
        if (l not in out) and (l != "<UNK>"):
            out.append(l)
    for l in pred_lst:
        if l not in out:
            out.append(l)
    return out[:len(corr_lst)]


def inferencer(word, topk = 1, knear = 1):

    in_vec = torch.from_numpy(en_glyph.word2xlitvec(word)).to(device)
    ## change to active or passive beam
    p_out_list = model.active_beam_inference(in_vec, beam_width = topk)
    p_result = [ hi_glyph.xlitvec2word(out.cpu().numpy()) for out in p_out_list]

    emb_list = [ emb_model.get_word_embedding(out) for out in p_out_list]

    c_result = [annoy_obj.get_nearest_vocab(emb, count = knear) for emb in emb_list ]
    c_result = sum(c_result, []) # delinieate 2d list
    result = pred_contrive(c_result, p_result)
    return result



def infer_analytics(word):
    """Analytics by ploting values
    """
    save_path = os.path.dirname(weight_path) + "/viz_log/"
    if not os.path.exists(save_path): os.makedirs(save_path)

    in_vec = torch.from_numpy(en_glyph.word2xlitvec(word))
    out, aw = model.inference(in_vec, debug=1)
    result = hi_glyph.xlitvec2word(out.numpy())

    rutl.attention_weight_plotter(result, word, aw.detach().numpy()[:len(result)],
                                    save_path=save_path )
    return result


if __name__ == "__main__":
    while(1):
        a = input()
        result = inferencer(a)
        print(result)