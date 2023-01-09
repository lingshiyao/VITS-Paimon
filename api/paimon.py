import soundfile as sf
import torch

import commons
import utils
from api.app_constance import AppConstance
from api.block_runner.base import Base
from models import SynthesizerTrn
from text import text_to_sequence
from text.symbols import symbols
from zfoutils import ZfoUtils


class Paimon(Base):
    hps = None
    net_g = None

    def __init__(self):
        self.hps = utils.get_hparams_from_file(AppConstance.biaobei_base_json)
        self.net_g = SynthesizerTrn(
            len(symbols),
            self.hps.data.filter_length // 2 + 1,
            self.hps.train.segment_size // self.hps.data.hop_length,
            **self.hps.model).cuda()
        _ = self.net_g.eval()
        _ = utils.load_checkpoint(AppConstance.G_1434000_pth, self.net_g, None)
        None

    def get_text(self, text):
        print(1.1, text)
        text_norm = text_to_sequence(text, self.hps.data.text_cleaners)
        print(1.2)
        if self.hps.data.add_blank:
            print(1.3)
            text_norm = commons.intersperse(text_norm, 0)
            print(1.4)
        text_norm = torch.LongTensor(text_norm)
        print(1.5, text_norm)
        return text_norm

    def gen(self, text, token, need_cache):
        if self.lock:
            return None
        self.lock = True
        result = self._gen(text, token, need_cache)
        self.lock = False
        return result

    def _gen(self, text, token, need_cache):
        length_scale = 1
        if need_cache:
            audio_path = AppConstance.OUT_PUT_PATH + ZfoUtils.md5(text) + '.wav'
        else:
            audio_path = AppConstance.OUT_PUT_PATH + token + '.wav'
        print(1)
        stn_tst = self.get_text(text)
        print(2)
        with torch.no_grad():
            print(3)
            x_tst = stn_tst.cuda().unsqueeze(0)
            print(4)
            x_tst_lengths = torch.LongTensor([stn_tst.size(0)]).cuda()
            print(5)
            audio = \
                self.net_g.infer(x_tst, x_tst_lengths, noise_scale=.667, noise_scale_w=0.8, length_scale=length_scale)[
                    0][
                    0, 0].data.cpu().float().numpy()
        print(6)
        sf.write(audio_path, audio, samplerate=self.hps.data.sampling_rate)
        print(7)
        return audio_path
