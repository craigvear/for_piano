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
        self.tick_count = 0

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

        # add bar furniture
        self.piano_staff = [self.treble_staff, self.bass_staff]
        system_line = SystemLine(self.piano_staff)
        end_line = Barline(Mm(250), self.piano_staff)
        piano_bracket = Brace(self.piano_staff)
        dynamic = Dynamic((ZERO, self.bass_staff.unit(7)), self.bass_staff, "ppp")
        pedal = PedalLine((ZERO, self.bass_staff.unit(8)), bass_clef, Mm(250))

        # position BPM/ live pulse indicator on staff
        pulse_pen = Pen(color="#ff0000")
        # self.bpm = MetronomeMark((ZERO, self.treble_staff.unit(-2)), self.treble_staff, "metNoteQuarterUp", "= 60")
        brush = Brush()
        self.bpm_pulse = MusicText((ZERO, self.treble_staff.unit(-2)), self.treble_staff, "metNoteQuarterUp", brush=brush, pen=pulse_pen)
        self.bpm = Text((Mm(10), ZERO), self.bpm_pulse, "= 60", scale=2)



        # position a crotchet rest at start of every bar
        # self.treble_rest = Chordrest(ZERO, self.treble_staff, None, (1, 4))
        # self.bass_rest = Chordrest(ZERO, self.bass_staff, None, (1, 4))

    def build_new_events(self, chord, time_sig, duration, polyrhythm):
        # init events list
        new_events_list = []
        remaining_total_bar_length = 0

        #######################
        # STRUCTURE
        #######################

        # make new time signatures
        time_sig_treble = TimeSignature(ZERO, self.treble_staff, time_sig)
        time_sig_bass = TimeSignature(ZERO, self.bass_staff, time_sig)
        new_events_list.append(time_sig_treble)
        new_events_list.append(time_sig_bass)

        # calculate new bar length from time sig
        self.total_bar_length = (8 / time_sig[1]) * time_sig[0]

        # add first rest
        first_rest_duration = self.first_rest(time_sig)
        print(f"first rest duration = {first_rest_duration}")
        treble_first_rest = Chordrest(Mm(20), self.treble_staff, None, (first_rest_duration, 8))
        bass_first_rest = Chordrest(Mm(20), self.bass_staff, None, (first_rest_duration, 8))
        new_events_list.append(treble_first_rest)
        new_events_list.append(bass_first_rest)

        remaining_total_bar_length = self.total_bar_length - first_rest_duration
        print("remaining duration = ", remaining_total_bar_length)

        # determine note event duration
        # todo add polyrhytmic into this equation
        note_event_length = (8 / duration[1]) * duration[0]
        print(f'note event length for {duration} = ', note_event_length, "quavers")

        # note duration greater than bar length + 1 beat rest
        if note_event_length > remaining_total_bar_length:
            note_event_length = remaining_total_bar_length
        # remaining_total_bar_length -= note_event_length
        print(f"time sig, bar length, remaining, note event length = {time_sig, self.total_bar_length, remaining_total_bar_length, note_event_length}")

        #######################
        # NOTES
        #######################

        # get new notes from harmony
        clean_note_list = self.makes_new_notes(chord)
        print("remaining duration = ", remaining_total_bar_length)

        # sort into correct staff
        print("note list = ", clean_note_list)
        treble_note_list = []
        bass_note_list = []
        for note in clean_note_list:
            if Pitch.from_str(note).staff_pos_from_middle_c <= 0:
                treble_note_list.append(note)
            else:
                bass_note_list.append(note)

        # are treble and bass notes a block?
        if random() > 0.5:
            print("BLOCK CHORD")
            # treble and bass notes are a chordal block
            # position note event for both
            note_event_position_offset, adj_note_length, remaining_duration = self.note_position(remaining_total_bar_length, note_event_length)

            second_rests = self.padding_rests(note_event_position_offset)
            for pad in second_rests:
                new_events_list.append(pad)

            treble_event_x = Mm((first_rest_duration + note_event_position_offset) * 25)
            bass_event_x = Mm((first_rest_duration + note_event_position_offset) * 25)
            treble_event_duration = (adj_note_length, 8)
            bass_event_duration = (adj_note_length, 8)

        # or treat them as 2 separate events
        else:
            print("SEPARATE HANDS")
            # note_position), int(duration_of_note), int(remaining_duration)
            note_event_position_offset, adj_note_length, remaining_duration = self.note_position(remaining_total_bar_length, note_event_length)
            treble_event_x = Mm((first_rest_duration + note_event_position_offset) * 25)
            treble_event_duration = (adj_note_length, 8)
            second_rests = self.padding_rests(note_event_position_offset)
            for pad in second_rests:
                new_events_list.append(pad)

            note_event_position_offset, adj_note_length, remaining_duration = self.note_position(remaining_total_bar_length, note_event_length)
            bass_event_x = Mm((first_rest_duration + note_event_position_offset) * 25)
            bass_event_duration = (adj_note_length, 8)
            second_rests = self.padding_rests(note_event_position_offset)
            for pad in second_rests:
                new_events_list.append(pad)

        print("event durations", treble_event_duration, bass_event_duration)
        # print them on the staves
        treble_notes = Chordrest(treble_event_x,
                                 self.treble_staff,
                                 treble_note_list,
                                 treble_event_duration)
        bass_notes = Chordrest(bass_event_x,
                               self.bass_staff,
                               bass_note_list,
                               bass_event_duration)
        new_events_list.append(treble_notes)
        new_events_list.append(bass_notes)

        remaining_total_bar_length = remaining_duration
        print("remaining duration = ", remaining_total_bar_length)

        end_padding_rests_list = self.padding_rests(remaining_total_bar_length)
        for pad in end_padding_rests_list:
            new_events_list.append(pad)

        return new_events_list

    def padding_rests(self, remaining_total_bar_length):
        remaining_total_bar_length = int(remaining_total_bar_length)
        padding = []
        while remaining_total_bar_length > 0:
            print(f"padding {remaining_total_bar_length}")
            if remaining_total_bar_length == 4:
                rest_duration = remaining_total_bar_length
            else:
                rest_duration = remaining_total_bar_length % 4
            treble_pad = Chordrest(Mm(80), self.treble_staff, [], (rest_duration, 8))
            bass_pad = Chordrest(Mm(80), self.bass_staff, [], (rest_duration, 8))
            padding.append(treble_pad)
            # todo - this is wrong when we get to split hands!!!!
            padding.append(bass_pad)
            remaining_total_bar_length -= rest_duration
        return padding

    def first_rest(self, time_sig):
        """if time signature is 5/8 then the first rest is a quaver.
        else a crotchet"""
        if time_sig[1] == 8 and time_sig[0] <= 5:
            first_rest_duration = 1
        else:
            first_rest_duration = 2
        return first_rest_duration

    def note_position(self, remaining_duration, duration_of_note):
        """Adds a rest buffer at front of bar after the preset 1/4"""
        print("rhythm calc   ", remaining_duration, duration_of_note)

        # position the note event somewhere in the remaining bar
        note_position = randrange(remaining_duration)
        print(f"note position = {note_position}")

        # how much of bar is left?
        remaining_duration -= note_position
        print(f"remaining bar = {remaining_duration}")

        # crop duration of note?
        if duration_of_note <= remaining_duration:
            remaining_duration -= duration_of_note
        elif duration_of_note > remaining_duration:
            duration_of_note = remaining_duration
            remaining_duration = 0

        return int(note_position), int(duration_of_note), int(remaining_duration)

        #
        # compound = remaining_duration - duration_of_note
        #
        # print("compound = ", compound)
        # if compound < 0:
        #     remaining_duration = 0
        #     duration_of_note = remaining_duration
        # elif compound == 0:
        #     note_event_position_offset = 0
        # else:
        #     note_event_position_offset = randrange(compound) + 1
        # print(note_event_position_offset, duration_of_note)


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
        new_colour = gray_list[self.tick_count % 4]
        self.bpm_pulse.pen.color = new_colour
        self.bpm_pulse.brush.color = Color(new_colour)

    def refresh_func(self, time):
        """Main loop, refreshing the UI"""
        # print(self.tick_count)
        self.pulse_metronome_mark()

        self.tick_count += 1
        if self.tick_count >= self.total_bar_length * 2:
            self.tick_count = 0
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

