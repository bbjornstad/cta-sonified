# This library creates a SoundGenerator class, which will hold data for each
# wave that we will need to generate in order to produce sound. Borrowed
# heavily from Sid Perida's work available online.

import numpy as np
from scipy.io.wavfile import write
from fractions import gcd


# Note that this SoundGenerator class does not currently support changing
# amplitude, as is required by our project. We extend this generation
# module in the library CompositionGeneration
class SoundGenerator():
    def __init__(
            self,
            wave='sine',
            frequency=500,
            amplitude=1.0,
            duration=5,
            rate=44100):

        self.wave = str(wave)
        self.frequency = float(frequency)
        self.amplitude = self.limitAmplitude(amplitude)
        self.duration = float(duration)
        self.sound = np.array([])
        self.SAMPLE_RATE = int(rate)
        self.limit = np.vectorize(self.limitAmplitude)

        # Generate Sound
        if (wave == 'sine'):
            self.sound = self.generateSineWave()
        elif(wave == 'square'):
            self.sound = self.generateSquareWave()
        elif(wave == 'saw'):
            self.sound = self.generateSawtoothWave()
        elif(wave == 'constant'):
            self.sound = self.generateConstantWave()
        elif(wave == 'noise'):
            self.sound = self.generateWhiteNoiseWave()
        elif(wave == 'combination'):
            self.sound = self.sound

    def limitAmplitude(self, amplitude):
        return max(min(float(amplitude), 1.0), -1.0)

    def getSound(self):
        return self.sound

    def getFrequency(self):
        return self.frequency

    def getDuration(self):
        return self.duration

    def getSampleRate(self):
        return self.SAMPLE_RATE

    def getSampleCount(self):
        return int(self.duration * self.SAMPLE_RATE)

    def getSinglePhaseArray(self):
        singleCycleLength = self.SAMPLE_RATE / float(self.frequency)
        omega = np.pi * 2 / singleCycleLength
        phaseArray = np.arange(0, int(singleCycleLength)) * omega
        return phaseArray

    def generateSineWave(self):
        # Get Phase Array
        phaseArray = self.getSinglePhaseArray()
        # Compute Sine Values and scale by amplitude
        singleCycle = self.amplitude * np.sin(phaseArray)
        # Resize to match duration
        return np.resize(singleCycle, (self.getSampleCount(),)).astype(np.float)

    def generateSquareWave(self):
        # Use the fact that sign of sine is square wave and scale by amplitude
        return self.amplitude * np.sign(self.generateSineWave())

    def generateSawtoothWave(self):
        # Get Phase Array
        phaseArray = self.getSinglePhaseArray()
        # Compute Saw Values and scale by amplitude
        piInverse = 1 / np.pi
        saw = np.vectorize(lambda x: 1 - piInverse * x)
        singleCycle = self.amplitude * saw(phaseArray)
        # Resize to match duration
        return np.resize(singleCycle, (self.sampleCount,)).astype(np.float)

    def generateConstantWave(self):
        # Get Phase Array
        phaseArray = self.getSinglePhaseArray()
        # Assign to amplitude
        singleCycle = self.amplitude
        # Resize to match duration
        return np.resize(singleCycle, (self.sampleCount,)).astype(np.float)

    def generateWhiteNoiseWave(self):
        # Random samples between -1 and 1
        return np.random.uniform(-1, 1, self.getSampleCount())

    def writeWAVToFile(self, filename):
        write(filename + ".wav", self.SAMPLE_RATE, self.getSound())

    # operator overloads
    def combineSounds(self, soundObj, operator='+'):
        # Figure out which is the longer sound
        if len(self.sound) < len(soundObj.getSound()):
            minSound = np.copy(self.getSound())
            maxSound = np.copy(soundObj.getSound())
        else:
            maxSound = np.copy(self.getSound())
            minSound = np.copy(soundObj.getSound())

        # Perform appropriate operation
        if operator == '+':
            maxSound[0:len(minSound)] = maxSound[0:len(minSound)] + minSound
        elif operator == '-':
            maxSound[0:len(minSound)] = maxSound[0:len(minSound)] - minSound
        elif operator == '*':
            maxSound[0:len(minSound)] = maxSound[0:len(minSound)] * minSound

        # Limite sound values to within -1 and +1
        newSound = self.limit(maxSound)

        # Calculate metadata for new sound
        newFrequency = int(self.getFrequency()) * int(soundObj.getFrequency()) / \
            gcd(int(self.getFrequency()), int(soundObj.getFrequency()))
        newDuration = float(len(newSound)) / self.SAMPLE_RATE
        newAmplitude = np.max(newSound)

        # Create new sound object and return object
        returnObj = SoundGenerator(
            wave='combination',
            frequency=newFrequency,
            amplitude=newAmplitude,
            duration=newDuration)

        # Set sound value to newSound
        returnObj.setSound(newSound)
        return returnObj

    def __add__(self, soundObj):
        return self.combineSounds(soundObj, '+')

    def __sub__(self, soundObj):
        return self.combineSounds(soundObj, '-')

    def __mul__(self, soundObj):
        if isinstance(soundObj, int) or isinstance(soundObj, float):
            scaleFactor = limitAmplitude(soundObj)
            if(scaleFactor < 0):
                scaleFactor = 0.0
            returnObj = SoundGenerator(
                self.waveType, self.frequency, self.amplitude * scaleFactor, self.duration)
            sound = self.getSound()
            returnObj.setSound(sound * scaleFactor)
            return returnObj
        return self.combineSounds(soundObj, '*')

    def __xor__(self, soundObj):

        # Join two sound pieces together
        newSound = np.append(self.getSound(), soundObj.getSound())

        # Calculate metadata for new sound
        newFrequency = int(self.getFrequency()) * int(soundObj.getFrequency()) / \
            gcd(int(self.getFrequency()), int(soundObj.getFrequency()))
        newDuration = self.getDuration() + soundObj.getDuration()
        newAmplitude = np.max(newSound)

        # Create new sound object and return object
        returnObj = SoundGenerator(
            wave='combination', frequency=newFrequency, amplitude=newAmplitude, duration=newDuration)

        # Set sound value to newSound
        returnObj.setSound(newSound)
        return returnObj

    def __pow__(self, soundObj):
        # Figure out which is the longer sound
        if len(self.sound) < len(soundObj.getSound()):
            minSound = np.copy(self.getSound())
            maxSound = np.copy(soundObj.getSound())

        else:
            maxSound = np.copy(self.getSound())
            minSound = np.copy(soundObj.getSound())
        minSound = np.resize(minSound, (len(maxSound),))
        #newFrequency = int(self.getFrequency()) * int(soundObj.getFrequency()) / gcd(int(self.getFrequency()), int(soundObj.getFrequency()))
        newDuration = float(len(maxSound)) / SAMPLE_RATE
        # Frequency does not matter here
        minSoundObj = SoundGenerator(wave="Temp", frequency=100, amplitude=np.max(
            minSound), duration=newDuration)
        minSoundObj.setSound(minSound)
        maxSoundObj = SoundGenerator(wave="Temp", frequency=100, amplitude=np.max(
            maxSound), duration=newDuration)
        maxSoundObj.setSound(maxSound)
        return (minSoundObj * maxSoundObj)

    def setDuration(self, new_duration):
        self.__init__(wave=self.wave, frequency=self.frequency,
                      amplitude=self.amplitude, duration=new_duration, rate=self.SAMPLE_RATE)

    def setSound(self, soundArray):
        self.sound = soundArray
