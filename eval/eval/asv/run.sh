# false error rate = 0.7%
mkdir -p exp
python compute_em.py /root/spk-content/ohnn_sep/slue-voxpopuli/slue-voxpopuli_dev.tsv \
	/root/spk-content/ohnn_sep/slue-voxpopuli/dev \
	/root/spk-content/ohnn_sep/output_speech/libri_tts_clean_100_fbank_xv_ssl_freeze/ohnn/data/voxpup-dev \
	exp

