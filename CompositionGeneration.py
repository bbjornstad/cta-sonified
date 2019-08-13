# this class defines the extension to SoundGeneration, in which we
# aim to produce a class that holds a composition of SoundGenerators
# which must be combined to create our piece.

import SoundGeneration as sg
import numpy as np
import pandas as pd
from scipy.io.wavfile import write


# we need to do a bit of thinking about how to best organize our composition
# in particular, we need to hold a series of SoundGenerators, which much each
# be appropriately combined and written out to the wav file.
class CompositionGenerator():
    def __init__(self, duration, rate=44100):
        self.duration = float(duration)
        self.SAMPLE_RATE = int(rate)
        self.total_samples = int(duration * self.SAMPLE_RATE)
        self.composition = np.asarray([])
        # the generators item is a dictionary where the keys are disjoint
        # intervals that partition the entire composition, associated each
        # to a list of SoundGenerators for this section.
        self.generators = {}

    def writeCompositionToFile(self, filename):
        write(filename + ".wav", self.SAMPLE_RATE, self.getComposition())

    def getComposition(self):
        return self.composition

    def getSampleRate(self):
        return self.SAMPLE_RATE

    def getDuration(self):
        return self.duration

    def generateFromPandas(self, df):
        pass

    # I think that the best option here might be to write a helper function
    # that can handle taking in a bunch of sound generators
    # and dividing up the samples into a bunch of unique partitions, then
    # associating these unique partitions with a list of sound generators
    # that will be used in that time.

    def createDisjointPartitions(self, list_of_intervals):
        new_partitions = []
        points = []
        for interval in list_of_intervals:
            if interval[0] not in points:
                points.append(interval[0])
            if interval[1] not in points:
                points.append(interval[1])
        sorted_points = sorted(points)
        for i in range(len(sorted_points) - 1):
            interval = (sorted_points[i], sorted_points[i + 1])
            new_partitions.append(interval)
        return new_partitions

    def writeComposition(self):
        """ This function aggregates all the sound generators and writes
            thier contents into the composition numpy array, then deletes
            the sound generators that were used to make the sounds. """
        for interval in self.generators:
            list_of_gens = self.generators[interval]
            new_sound = None
            start, end = interval[0], interval[1]
            start_samps = int(start * self.SAMPLE_RATE)
            end_samps = int(end * self.SAMPLE_RATE)
            if len(list_of_gens) <= 0:
                # this will need to be fixed so that silent sections can
                # be accomodated.
                new_sound = np.zeros(shape=(1, end_samps - start_samps))
            elif len(list_of_gens) == 1:
                new_sound = list_of_gens[0].getSound()
            else:
                new_sg = list_of_gens[0]
                for i in range(len(list_of_gens) - 1):
                    new_sg += list_of_gens[i + 1]
                new_sound = new_sg.getSound()

            self.composition = np.append(self.composition, new_sound)

    def getGeneratorsInInterval(self, interval):
        present_gens = []

        for key in self.generators:
            start, end = key[0], key[1]
            gens = self.generators[key]
            if (start <= interval[0] < end) or (start < interval[1] <= end):
                present_gens.extend(gens)

        # we use set to only take the unique gens (i.e. remove possible
        # duplicate generators that may have been added multiple times)
        return list(set(present_gens))

    def fixGeneratorDurations(self, gen_dict):
        def fix_gen_list(l, dur):
            new_gen_list = []
            for g in l:
                new_sg = sg.SoundGenerator(
                    wave=g.wave,
                    frequency=g.frequency,
                    amplitude=g.amplitude,
                    duration=dur,
                    rate=g.SAMPLE_RATE)
                new_gen_list.append(new_sg)
            return new_gen_list

        fixed_gens = {i: fix_gen_list(gen_dict[i], i[1] - i[0])
                      for i in gen_dict}

        return fixed_gens

    def addSoundGenerator(self, wave, freq, amplitude, start, duration):
        interval = (start, start + duration)
        new_sg = sg.SoundGenerator(
            wave=wave,
            frequency=freq,
            amplitude=amplitude,
            rate=self.SAMPLE_RATE,
            duration=duration)

        if interval in self.generators.keys():
            self.generators[interval].append(new_sg)
        else:
            self.generators.update({interval: [new_sg]})

        old_intervals = self.generators.keys()

        new_intervals = self.createDisjointPartitions(old_intervals)

        new_gens = [self.getGeneratorsInInterval(i) for i in new_intervals]

        new_gen_dict = dict(zip(new_intervals, new_gens))

        self.generators = self.fixGeneratorDurations(new_gen_dict)
