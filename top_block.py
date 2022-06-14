#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Top Block
# GNU Radio version: 3.8.1.0

from gnuradio import analog
import math
from gnuradio import audio
from gnuradio import blocks
from gnuradio import digital
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import zeromq
import osmosdr
import time

class top_block(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "Top Block")

        ##################################################
        # Variables
        ##################################################
        self.samp_rate_audio = samp_rate_audio = 48000
        self.data_rate = data_rate = 1200
        self.samp_rate = samp_rate = 250000
        self.samp_per_sym = samp_per_sym = int(samp_rate_audio/data_rate)
        self.rf_gain = rf_gain = 50
        self.channel_width = channel_width = 12500
        self.center_freq = center_freq = 457937500

        ##################################################
        # Blocks
        ##################################################
        self.zeromq_pub_sink_0 = zeromq.pub_sink(gr.sizeof_char, 1, 'tcp://127.0.0.1:5555', 100, False, -1)
        self.rtlsdr_source_0 = osmosdr.source(
            args="numchan=" + str(1) + " " + ""
        )
        self.rtlsdr_source_0.set_time_unknown_pps(osmosdr.time_spec_t())
        self.rtlsdr_source_0.set_sample_rate(samp_rate)
        self.rtlsdr_source_0.set_center_freq(center_freq, 0)
        self.rtlsdr_source_0.set_freq_corr(0, 0)
        self.rtlsdr_source_0.set_gain(rf_gain, 0)
        self.rtlsdr_source_0.set_if_gain(20, 0)
        self.rtlsdr_source_0.set_bb_gain(20, 0)
        self.rtlsdr_source_0.set_antenna('', 0)
        self.rtlsdr_source_0.set_bandwidth(0, 0)
        self.rational_resampler_xxx_0_0 = filter.rational_resampler_ccc(
                interpolation=samp_rate_audio,
                decimation=samp_rate,
                taps=None,
                fractional_bw=None)
        self.rational_resampler_xxx_0 = filter.rational_resampler_fff(
                interpolation=1,
                decimation=10,
                taps=None,
                fractional_bw=None)
        self.low_pass_filter_0 = filter.fir_filter_ccf(
            1,
            firdes.low_pass(
                1,
                samp_rate,
                4000,
                1000,
                firdes.WIN_HAMMING,
                6.76))
        self.freq_xlating_fir_filter_xxx_0 = filter.freq_xlating_fir_filter_fcf(1, firdes.low_pass(1.0,samp_rate_audio,1000,600), 1500, samp_rate_audio)
        self.digital_clock_recovery_mm_xx_0 = digital.clock_recovery_mm_ff(samp_per_sym*(1+0.0)/10, 0.25*0.175*0.175, 0.5, 0.175, 0.005)
        self.digital_binary_slicer_fb_0 = digital.binary_slicer_fb()
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_ff(-1)
        self.blocks_moving_average_xx_0 = blocks.moving_average_ff(20, 1, 4000, 1)
        self.audio_sink_0 = audio.sink(48000, '', True)
        self.analog_quadrature_demod_cf_0 = analog.quadrature_demod_cf(1)
        self.analog_pwr_squelch_xx_1 = analog.pwr_squelch_cc(-42, 1e-4, 0, True)
        self.analog_nbfm_rx_0 = analog.nbfm_rx(
        	audio_rate=samp_rate_audio,
        	quad_rate=48000,
        	tau=75e-6,
        	max_dev=5e3,
          )



        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_nbfm_rx_0, 0), (self.audio_sink_0, 0))
        self.connect((self.analog_nbfm_rx_0, 0), (self.freq_xlating_fir_filter_xxx_0, 0))
        self.connect((self.analog_pwr_squelch_xx_1, 0), (self.rational_resampler_xxx_0_0, 0))
        self.connect((self.analog_quadrature_demod_cf_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.blocks_moving_average_xx_0, 0), (self.rational_resampler_xxx_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.blocks_moving_average_xx_0, 0))
        self.connect((self.digital_binary_slicer_fb_0, 0), (self.zeromq_pub_sink_0, 0))
        self.connect((self.digital_clock_recovery_mm_xx_0, 0), (self.digital_binary_slicer_fb_0, 0))
        self.connect((self.freq_xlating_fir_filter_xxx_0, 0), (self.analog_quadrature_demod_cf_0, 0))
        self.connect((self.low_pass_filter_0, 0), (self.analog_pwr_squelch_xx_1, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.digital_clock_recovery_mm_xx_0, 0))
        self.connect((self.rational_resampler_xxx_0_0, 0), (self.analog_nbfm_rx_0, 0))
        self.connect((self.rtlsdr_source_0, 0), (self.low_pass_filter_0, 0))

    def get_samp_rate_audio(self):
        return self.samp_rate_audio

    def set_samp_rate_audio(self, samp_rate_audio):
        self.samp_rate_audio = samp_rate_audio
        self.set_samp_per_sym(int(self.samp_rate_audio/self.data_rate))
        self.freq_xlating_fir_filter_xxx_0.set_taps(firdes.low_pass(1.0,self.samp_rate_audio,1000,600))

    def get_data_rate(self):
        return self.data_rate

    def set_data_rate(self, data_rate):
        self.data_rate = data_rate
        self.set_samp_per_sym(int(self.samp_rate_audio/self.data_rate))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.samp_rate, 4000, 1000, firdes.WIN_HAMMING, 6.76))
        self.rtlsdr_source_0.set_sample_rate(self.samp_rate)

    def get_samp_per_sym(self):
        return self.samp_per_sym

    def set_samp_per_sym(self, samp_per_sym):
        self.samp_per_sym = samp_per_sym
        self.digital_clock_recovery_mm_xx_0.set_omega(self.samp_per_sym*(1+0.0)/10)

    def get_rf_gain(self):
        return self.rf_gain

    def set_rf_gain(self, rf_gain):
        self.rf_gain = rf_gain
        self.rtlsdr_source_0.set_gain(self.rf_gain, 0)

    def get_channel_width(self):
        return self.channel_width

    def set_channel_width(self, channel_width):
        self.channel_width = channel_width

    def get_center_freq(self):
        return self.center_freq

    def set_center_freq(self, center_freq):
        self.center_freq = center_freq
        self.rtlsdr_source_0.set_center_freq(self.center_freq, 0)



def main(top_block_cls=top_block, options=None):
    tb = top_block_cls()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()
        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()
    try:
        input('Press Enter to quit: ')
    except EOFError:
        pass
    tb.stop()
    tb.wait()


if __name__ == '__main__':
    main()
