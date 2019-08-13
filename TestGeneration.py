import CompositionGeneration as cg
import SoundGeneration as sg

test_freqs = [440, 880]
test_waves = ['sine', 'sine']
test_amps = [0.5, 0.3]
test_starts = [0, 12]
test_durs = [15, 10]

comp = cg.CompositionGenerator(30, rate=44100)

for i in range(2):
    comp.addSoundGenerator(
        test_waves[i],
        test_freqs[i],
        test_amps[i],
        test_starts[i],
        test_durs[i])

print(comp.generators)
comp.writeComposition()
comp.writeCompositionToFile('test')
