from neoscore.common import *
import harmony
from random import choice, random, randrange

gray_list = ["#000000", "#808080", "#D3D3D3", "#F2F3F5"]

class For_Piano:
    def __init__(self):
        # initiate neoscore with bespoke paper
        new_paper = Paper(Mm(400), Mm(300), Mm(1), Mm(1), Mm(1), Mm(1))
        neoscore.setup(new_paper)

        # set up harmony lists
        self.chord_list = harmony.chord_list
        self.time_sig_list = harmony.time_sigs
        self.duration_list = harmony.durations
        self.polyrhythm_list = harmony.polythythms

        # set up class vars
        self.beat_count = 0

        # start a list that builds up the composition from end to mid-point
        self.build_from_end = []

        # build blank bar
        self.build_blank_bar()

        # build first events on blank bar
        notes, time_sig, duration, polyrhythm = self.get_event_data()
        self.build_notes(notes, time_sig, duration, polyrhythm)

    def build_blank_bar(self):
        # add titles
        title = Text((Mm(100), Mm(20)), None, "for_piano (2022)", scale=6)
        name = Text((Mm(100), Mm(40)), None, "Craig Vear", scale=3)
        fat_pen = Pen(thickness=Mm(1))

        # make staffs and clefs
        self.treble_staff = Staff((Mm(75), Mm(100)), None, Mm(250), line_spacing=Mm(5), pen=fat_pen)
        treble_clef = Clef(ZERO, self.treble_staff, 'treble')

        self.bass_staff = Staff((Mm(75), Mm(150)), None, Mm(250), line_spacing=Mm(5), pen=fat_pen)
        bass_clef = Clef(ZERO, self.bass_staff, 'bass')

        self.piano_staff = [self.treble_staff, self.bass_staff]

        # add bar furniture
        system_line = SystemLine(self.piano_staff)
        end_line = Barline(Mm(250), self.piano_staff)
        piano_bracket = Brace(self.piano_staff)
        dynamic = Dynamic((ZERO, self.bass_staff.unit(7)), self.bass_staff, "ppp")

        # position BPM/ live pulse indicator on staff
        pulse_pen = Pen(color="#ff0000")
        # self.bpm = MetronomeMark((ZERO, self.treble_staff.unit(-2)), self.treble_staff, "metNoteQuarterUp", "= 60")
        brush = Brush()
        self.bpm_pulse = MusicText((ZERO, self.treble_staff.unit(-2)), self.treble_staff, "metNoteQuarterUp", brush=brush, pen=pulse_pen)
        self.bpm = Text((Mm(10), ZERO), self.bpm_pulse, "= 60", scale=2)

    def build_notes(self, chord, time_sig, duration, polyrhythm):
        # calculate new bar length from time sig & display time sig
        new_events_list = []

        bar_length = (8 / time_sig[1]) * time_sig[0]
        print("bar length = ", time_sig, bar_length)

        time_sig_treble = TimeSignature(ZERO, self.treble_staff, time_sig)
        time_sig_bass = TimeSignature(ZERO, self.bass_staff, time_sig)

        new_events_list.append(time_sig_treble)
        new_events_list.append(time_sig_bass)

        # calculate how many notes from chord
        note_list = []
        num_notes = randrange(2, len(chord))
        note_list.append(chord[:num_notes][0])
        self.build_from_end.append(chord[num_notes:])

        # last note in chord as a, b, c octave
        # last_note_octave = randrange(4)
        # if last_note_octave == 1:
        #     note_list.append(chord[-1])
        # elif last_note_octave == 2:
        #     note_list.append(chord[-1][0:-1] + ",")
        # elif last_note_octave == 3:
        #     note_list.append(chord[-1][0:-1] + ",,")

        print(note_list)
        treble_note_list = []
        bass_note_list = []

        for note in note_list:
            if Pitch.from_str(note).staff_pos_from_middle_c <= 0:
                treble_note_list.append(note)
            else:
                bass_note_list.append(note)

        treble_notes = Chordrest(Mm(100), self.treble_staff, treble_note_list, duration)
        bass_notes = Chordrest(Mm(100), self.bass_staff, bass_note_list, duration)
        new_events_list.append(treble_notes)
        new_events_list.append(bass_notes)

    def get_event_data(self):
        next_notes = choice(harmony.chord_list)
        next_time_sig = choice(harmony.time_sigs)
        next_duration = choice(harmony.durations)
        if random() > 0.6:
            next_polyrhythm = choice(harmony.polythythms)
        else:
            next_polyrhythm = None

        print(next_notes, next_time_sig, next_duration, next_polyrhythm)
        return next_notes, next_time_sig, next_duration, next_polyrhythm

    def refresh_func(self, time):
        print(self.beat_count)
        new_colour = gray_list[self.beat_count % 4]
        self.bpm_pulse.pen.color = new_colour
        # self.bpm_pulse.brush.color = new_colour
        self.beat_count += 1
        if self.beat_count >= 8:
            self.beat_count = 0
            chord, time_sig, duration, polyrhythm = self.get_event_data()
            bar_length = (8 / time_sig[1]) * time_sig[0]
            print("bar length = ", time_sig, bar_length)


if __name__ == "__main__":
    for_piano = For_Piano()

    # set the refresh function to the score main loop
    # change fps to allow pulse to fade
    neoscore.set_refresh_func(refresh_func=for_piano.refresh_func, target_fps=4)

    neoscore.show(display_page_geometry=False)

