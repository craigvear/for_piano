from neoscore.common import *
import harmony
from random import choice, random

new_paper = Paper(Mm(400), Mm(300), Mm(1), Mm(1), Mm(1), Mm(1))
neoscore.setup(new_paper)
beat_count = 0

def build_bar():
    # rest the quaver count
    global beat_count
    global treble_staff
    global bass_staff

    beat_count = 0

    # add titles
    title = Text((Mm(100), Mm(20)), None, "for_piano (2022)", scale=6)
    name = Text((Mm(100), Mm(40)), None, "Craig Vear", scale=3)
    fat_pen = Pen(thickness=Mm(1))

    # make staffs and clefs
    treble_staff = Staff((Mm(75), Mm(100)), None, Mm(250), line_spacing=Mm(5), pen=fat_pen)
    treble_clef = Clef(ZERO, treble_staff, 'treble')

    bass_staff = Staff((Mm(75), Mm(150)), None, Mm(250), line_spacing=Mm(5), pen=fat_pen)
    bass_clef = Clef(ZERO, bass_staff, 'bass')

    # add in bar furniture
    system_line = SystemLine([treble_staff, bass_staff])
    end_line = Barline(Mm(250), [treble_staff, bass_staff])
    piano_bracket = Brace([treble_staff, bass_staff])

    dynamic = Dynamic((ZERO, bass_staff.unit(7)), bass_staff, "ppp")

def build_notes(chord, time_sig, duration, polyrhythm):
    global treble_staff
    global bass_staff

    time_sig_treble = TimeSignature(ZERO, treble_staff, time_sig)
    time_sig_bass = TimeSignature(ZERO, bass_staff, time_sig)

    Chordrest(Mm(100), treble_staff, chord, duration)


build_bar()


def refresh_func(time):
    global beat_count
    print("1/8th beat")
    beat_count += 1
    if beat_count >= 2:
        beat_count = 0
        chord, time_sig, duration, polyrhythm = get_now_decisions()
        bar_length = (8 / time_sig[1]) * time_sig[0]
        print("bar length = ", time_sig, bar_length)

def get_now_decisions():
    next_chord = choice(harmony.chord_list)
    next_time_sig = choice(harmony.time_sigs)
    next_duration = choice(harmony.durations)
    if random() > 0.6:
        next_polyrhythm = choice(harmony.polythythms)
    else:
        next_polyrhythm = None

    print(next_chord, next_time_sig, next_duration, next_polyrhythm)
    return next_chord, next_time_sig, next_duration, next_polyrhythm


chord, time_sig, duration, polyrhythm = get_now_decisions()
build_notes(chord, time_sig, duration, polyrhythm)

neoscore.set_refresh_func(refresh_func=refresh_func, target_fps=2)

neoscore.show(display_page_geometry=False)

