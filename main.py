from neoscore.common import *
import harmony
from random import choice, random, randrange

gray_list = ["#000000",
             "#808080",
             "#D3D3D3",
             "#F2F3F5"]

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
        self.active_note_list = self.build_new_events(notes, time_sig, duration, polyrhythm)

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

    def build_new_events(self, chord, time_sig, duration, polyrhythm):
        # init events list
        new_events_list = []

        # calculate new bar length from time sig & display time sig
        bar_length = (8 / time_sig[1]) * time_sig[0]
        print("bar length = ", time_sig, bar_length)

        # make new time signatures
        time_sig_treble = TimeSignature(ZERO, self.treble_staff, time_sig)
        time_sig_bass = TimeSignature(ZERO, self.bass_staff, time_sig)
        new_events_list.append(time_sig_treble)
        new_events_list.append(time_sig_bass)

        # make new notes
        clean_note_list = self.makes_new_notes(chord)

        # Pads 1st part of bar with rests
        first_rest = self.first_rest(bar_length, duration)
        new_events_list.append(first_rest)

        # sort and print onto correct staff
        # todo random seperation of RH & LH across the bar
        print("note list = ", clean_note_list)
        treble_note_list = []
        bass_note_list = []

        for note in clean_note_list:
            if Pitch.from_str(note).staff_pos_from_middle_c <= 0:
                treble_note_list.append(note)
            else:
                bass_note_list.append(note)

        treble_notes = Chordrest(Mm(100), self.treble_staff, treble_note_list, duration)
        bass_notes = Chordrest(Mm(100), self.bass_staff, bass_note_list, duration)
        new_events_list.append(treble_notes)
        new_events_list.append(bass_notes)

        return new_events_list

    def first_rest(self, bar_length, duration) -> list:
        """Adds a rest buffer at front of bar. Will always be > 1/4 note"""
        first_rest_list = []
        first_rest_list.append((1, 4))

        return first_rest_list

    def makes_new_notes(self, chord) -> list:
        """Calculates all note events for current bar"""
        # calculate how many notes from chord
        note_list = []
        num_notes = randrange(1, len(chord))
        print(len(chord), num_notes)

        # add chosen notes to note list
        for i in range(num_notes):
            note_list.append(chord[i][0])
        print(note_list)

        # add the missing notes from this chord to the end list
        end_list = []
        if num_notes < len(chord):
            for ie in range(len(chord) - num_notes):
                end_list.append(chord[ie][0])
            self.build_from_end.append(end_list)

        # 3 in 5 chance last note in chord as a, b, c variation
        if num_notes != len(chord):
            added_note = chord[-1]
            last_note_octave = randrange(5)
            if last_note_octave == 0:
                note_list.append(added_note)
            elif last_note_octave == 1:
                if added_note[-1] == "'" or added_note[-1] == ",":
                    note_list.append(added_note[:-1] + ",")
                else:
                    note_list.append(added_note + ",")
            elif last_note_octave == 2:
                if added_note[-1] == "'" or added_note[-1] == ",":
                    note_list.append(added_note[:-1] + ",,")
                else:
                    note_list.append(added_note + ",,")

        # bubble sort for duplicate notes
        clean_note_list = self.check_for_duplicate_notes(note_list)
        return clean_note_list

    def check_for_duplicate_notes(self, note_list) -> list:
        """Removes any dupl;icate notes from not list.
            Returns cleaned list"""
        clean_note_list = [i for n, i in enumerate(note_list) if i not in note_list[:n]]
        print("note list = ", note_list, "clean list = ", clean_note_list)
        return clean_note_list

    def get_event_data(self):
        """Randomly chooses notes, time sig, durations etc
        from harmony list.
            Returns choices"""
        next_notes = choice(harmony.chord_list)
        next_time_sig = choice(harmony.time_sigs)
        next_duration = choice(harmony.durations)
        if random() > 0.6:
            next_polyrhythm = choice(harmony.polythythms)
        else:
            next_polyrhythm = None

        print(next_notes, next_time_sig, next_duration, next_polyrhythm)
        return next_notes, next_time_sig, next_duration, next_polyrhythm

    def remove_active_notes(self, active_notes_list):
        """Wipes clean all the old note events from previous bar"""
        for event in active_notes_list:
            event.remove()

    def pulse_metronome_mark(self):
        """Pulses te metronome mark depending on time sig"""
        new_colour = gray_list[self.beat_count % 4]
        self.bpm_pulse.pen.color = new_colour
        self.bpm_pulse.brush.color = Color(new_colour)

    def refresh_func(self, time):
        """Main loop, refreshing the UI"""
        print(self.beat_count)
        self.pulse_metronome_mark()

        self.beat_count += 1
        if self.beat_count >= 16:
            self.beat_count = 0
            self.remove_active_notes(self.active_note_list)
            chord, time_sig, duration, polyrhythm = self.get_event_data()
            bar_length = (8 / time_sig[1]) * time_sig[0]
            print("bar length = ", time_sig, bar_length)
            self.active_note_list = self.build_new_events(chord, time_sig, duration, polyrhythm)


if __name__ == "__main__":
    for_piano = For_Piano()

    # set the refresh function to the score main loop
    # change fps to allow pulse to fade
    neoscore.set_refresh_func(refresh_func=for_piano.refresh_func, target_fps=4)

    neoscore.show(display_page_geometry=False)

