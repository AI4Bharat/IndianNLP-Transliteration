import os
from utilities.lang_data_utils import GlyphStrawboss, VocabSanitizer
import utilities.running_utils as rutl

hi_glyph = GlyphStrawboss("hi")
en_glyph = GlyphStrawboss("en")

##============ RNN Based =======================================================
import torch
from hypotheses.training_85.recurrent_nets_85 import model
weight_path = "hypotheses/training_85/Training_85_model.pth"
# voc_sanitize = VocabSanitizer("data/X_word_list.json")

weights = torch.load( weight_path, map_location=torch.device('cpu'))
model.load_state_dict(weights)
model.eval()

def inferencer(word, topk = 3):
    if topk == 1:
        in_vec = torch.from_numpy(en_glyph.word2xlitvec(word))
        out = model.inference(in_vec)
        result =[ hi_glyph.xlitvec2word(out.numpy()) ]
        return result
    else:
        in_vec = torch.from_numpy(en_glyph.word2xlitvec(word))
        ## change to active or passive beam
        out_list = model.active_beam_inference(in_vec, beam_width = topk)
        result = [ hi_glyph.xlitvec2word(out.numpy()) for out in out_list]
        # result = voc_sanitize.reposition(result)
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