from neoscore.common import *
import harmony
from random import choice, random, randrange
import time

gray_list = ["#000000",
             "#808080",
             "#D3D3D3",
             "#F2F3F5"]


# todo timing and reverse half
# todo add polyrhytmic into this equation


class For_Piano:
    def __init__(self, duration):
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
        self.end_time = duration + time.time()

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
        self.treble_staff = Staff((Mm(75), Mm(100)), None, Mm(300), line_spacing=Mm(5), pen=fat_pen)
        treble_clef = Clef(ZERO, self.treble_staff, 'treble')

        self.bass_staff = Staff((Mm(75), Mm(150)), None, Mm(300), line_spacing=Mm(5), pen=fat_pen)
        bass_clef = Clef(ZERO, self.bass_staff, 'bass')

        # add bar furniture
        self.piano_staff_list = [self.treble_staff, self.bass_staff]
        system_line = SystemLine(self.piano_staff_list)
        self.end_line = Barline(Mm(250), self.piano_staff_list)
        piano_bracket = Brace(self.piano_staff_list)
        dynamic = Dynamic((ZERO, self.bass_staff.unit(7)), self.bass_staff, "ppp")
        self.pedal = PedalLine((ZERO, self.bass_staff.unit(8)), bass_clef, Mm(300))

        # position BPM/ live pulse indicator on staff
        pulse_pen = Pen(color="#ff0000")
        brush = Brush()
        self.bpm_pulse = MusicText((ZERO, self.treble_staff.unit(-2)), self.treble_staff, "metNoteQuarterUp", brush=brush, pen=pulse_pen)
        self.bpm = Text((Mm(10), ZERO), self.bpm_pulse, "= 60", scale=2)

    def build_new_events(self, chord, time_sig, duration, polyrhythm):
        """organises event generation and collects an event list.
        :returns: list of neoscore objects"""

        # init events list
        neoscore_events_list = []

        #######################
        # overall structure
        #######################

        # get new time signatures
        time_sig_treble = TimeSignature(ZERO, self.treble_staff, time_sig)
        time_sig_bass = TimeSignature(ZERO, self.bass_staff, time_sig)
        neoscore_events_list.append(time_sig_treble)
        neoscore_events_list.append(time_sig_bass)

        # calculate new bar length from time sig
        self.total_bar_length = int((8 / time_sig[1]) * time_sig[0])

        # build quaver x-position list for bar length
        initial_offset = 25
        quaver_mm_unit = 25
        end_offset = 25
        self.quaver_position_list_mm = [initial_offset]
        for quaver in range(self.total_bar_length):
            self.quaver_position_list_mm.append((quaver + 1) * quaver_mm_unit + initial_offset)
        print(f"quaver quaver_position_list_mm list = {self.quaver_position_list_mm}")

        # make quaver position list for iterating through quaver_position_list_mm (LH, RH)
        next_8th_position_list = [0, 0]

        # change blank bar to fit new time sig
        self.treble_staff.length = Mm(initial_offset + (self.total_bar_length * quaver_mm_unit) + end_offset)
        self.bass_staff.length = Mm(initial_offset + (self.total_bar_length * quaver_mm_unit) + end_offset)
        self.end_line.x = Mm(self.quaver_position_list_mm[-1] + end_offset)
        self.pedal.end_x = Mm(self.quaver_position_list_mm[-1] + end_offset)

        #######################
        # add first rest
        #######################
        for i, hand in enumerate(next_8th_position_list):
            first_rest_object, new_8th_position = self.add_first_rest(time_sig,
                                                self.piano_staff_list[i],
                                                next_8th_position_list[i])

            # add objects to master events list
            neoscore_events_list.append(first_rest_object)
            # amend next 8th position list
            next_8th_position_list[i] = new_8th_position

        print(f"next_8th_position = {next_8th_position_list} out of {self.total_bar_length}")

        #######################
        # get note list
        #######################
        # determine note event duration in quavers
        # todo add polyrhytmic into this equation
        note_event_length = int((8 / duration[1]) * duration[0])

        # # calc polyrythm extras if applicable
        # if polyrhythm:
        #     poly_nums = (int(polyrhythm[0]), int(polyrhythm[-1]))
        #     polyrhythm_extra = (8 / poly_nums[1]) * poly_nums[0]
        #     note_event_length =
        print(f'note event length for {duration} = ', note_event_length, "quavers")

        # get new notes from harmony & sort into LH & RH & clean duplicates
        raw_note_list = self.makes_new_notes(chord)
        treble_note_list, bass_note_list = self.clean_note_list(raw_note_list)
        note_list_list = [treble_note_list, bass_note_list]

        #######################
        # block or separate hands
        #######################
        if random() > 0.5:
            print("BLOCK CHORD")

            # get position of block chord for each hand
            # todo: this shuold be for only 1 hand (RH?)
            # if treble_note_list:
            for i, hand in enumerate(note_list_list):
                neoscore_events, next_8th_position = self.note_position(note_event_length,
                                            next_8th_position_list[i],
                                            note_list_list[i],
                                            self.piano_staff_list[i])

                # put rests and notes on master event list
                for e in neoscore_events:
                    print(e)
                    neoscore_events_list.append(e)

                # final padding if required
                end_padding = self.padding_rests(next_8th_position)
                for pad in end_padding:
                    rest = Chordrest(Mm(self.quaver_position_list_mm[next_8th_position]),
                                     self.treble_staff,
                                     None, (pad, 8))
                    neoscore_events_list.append(rest)
            # print(f"next_8th_position = {self.treble_next_8th_position}, {self.bass_next_8th_position}")

        # or treat them as 2 separate events
        else:
            print("SEPARATE HANDS")
            # get position of block chord for each hand
            for i, hand in enumerate(note_list_list):
                neoscore_events, next_8th_position = self.note_position(note_event_length,
                                                               next_8th_position_list[i],
                                                               note_list_list[i],
                                                               self.piano_staff_list[i])

                # put rests and notes on master event list
                for e in neoscore_events:
                    print(e)
                    neoscore_events_list.append(e)

                # final padding if required
                print(f"last 1/8th position for {hand} is {next_8th_position}")
                end_padding = self.padding_rests(next_8th_position)
                for pad in end_padding:
                    rest = Chordrest(Mm(self.quaver_position_list_mm[next_8th_position]),
                                     self.treble_staff,
                                     None, (pad, 8))
                    print(f"rest = {rest}")
                    neoscore_events_list.append(rest)
            # print(f"next_8th_position = {self.treble_next_8th_position}, {self.bass_next_8th_position}")

        for hand in enumerate(note_list_list):
            for events in hand:
                print(f"adding {events} from {hand}")
                neoscore_events_list.append(events)

        return neoscore_events_list


    def note_position(self, duration_of_note,
                      next_8th_position,
                      hand_list,
                      staff):
        """position of note/ chord event, pads with rest at front if needed.
        :returns list of Chordrest events (chords and rests)"""

        # position the note event somewhere in the remaining bar
        local_event_list = []
        # print(f"next_8th_position = {next_8th_position}")
        # todo - this is very wrong
        remaining_duration = self.total_bar_length - (next_8th_position + duration_of_note)
        note_position = randrange(remaining_duration)
        print(f"random note position = {note_position} out of {remaining_duration}")

        # pad with rests
        rests_padding = self.padding_rests(next_8th_position - note_position)
        print("rests padding = ", rests_padding)

        for i, pad in enumerate(rests_padding):
            if hand_list:
                print(f"next_8th_position = {next_8th_position}")
                rest_pad = Chordrest(Mm(self.quaver_position_list_mm[next_8th_position]),
                                       staff, [],
                                       (pad, 8))
                local_event_list.append(rest_pad)
                next_8th_position += pad
                print(f"next_8th_position = {next_8th_position}")

        # adjust note length to accom rest padding
        # if duration_of_note > duration_of_note + next_8th_position:
        #     duration_of_note = remaining_duration - next_8th_position

        # calc note coords
        event_x = Mm(self.quaver_position_list_mm[next_8th_position])
        print(f"duration_of_note {duration_of_note}")
        event_duration = (duration_of_note, 8)
        print(f"event_duration {event_duration}")

        # add note to staff
        if hand_list:
            notes = Chordrest(event_x,
                              staff,
                              hand_list,
                              event_duration)
            local_event_list.append(notes)

            # how much of bar is left?
            print(f"event_duration {event_duration}")
            next_8th_position += duration_of_note
            print(f"next_8th_position = {next_8th_position}")

        return local_event_list, next_8th_position

    def clean_note_list(self, raw_chord_list):
        """Removes any dupl;icate notes from not list.
            Returns cleaned list for LH & RH"""
        treble_note_list = []
        bass_note_list = []

        clean_note_list = [i for n, i in enumerate(raw_chord_list) if i not in raw_chord_list[:n]]
        print("note list = ", raw_chord_list, "clean list = ", clean_note_list)

        # split between hands
        for note in clean_note_list:
            if Pitch.from_str(note).staff_pos_from_middle_c <= 0:
                treble_note_list.append(note)
            else:
                bass_note_list.append(note)

        return treble_note_list, bass_note_list

    def add_first_rest(self, time_sig, staff, next_8th_position):
        """if time signature is 5/8 then the first rest is a quaver.
                else a crotchet.
                Make a Chordrest.
                Return: Chordrest"""
        if time_sig[0] <= 5 and time_sig[1] == 8:
            first_rest_duration = 1
        else:
            first_rest_duration = 2
        print(f"first rest duration = {first_rest_duration}")

        first_rest = Chordrest(Mm(self.quaver_position_list_mm[0]), staff, None, (first_rest_duration, 8))
        next_8th_position += first_rest_duration
        print(f"first_rest = {first_rest}, next_event_list = {next_8th_position}")
        return first_rest, next_8th_position

    def padding_rests(self, last_8th_position) -> list:
        print(last_8th_position)
        padding_list = []
        while last_8th_position > 0:
            print(f"padding remaining_total_bar_length {last_8th_position}")
            if last_8th_position % 4 == 0:
                rest_duration = 4
                print("A")
            elif last_8th_position % 4 == 1:
                rest_duration = 1
                print("B")
            elif last_8th_position % 4 == 2:
                rest_duration = 2
                print("B")
            elif last_8th_position % 4 == 3:
                rest_duration = 3
                print("B")

            padding_list.append(rest_duration)
            last_8th_position -= rest_duration
            print(f"rest duration = {rest_duration},remaining dur = {last_8th_position}")

        print(f"Padding list = {padding_list}")
        return padding_list

        #     print(f"padding remaining_total_bar_length {remaining_duration}")
        #     if remaining_duration == 4:
        #         rest_duration = remaining_duration
        #         padding_list.append(rest_duration)
        #         print("A")
        #     elif remaining_duration == 2:
        #         rest_duration = remaining_duration
        #         padding_list.append(rest_duration)
        #     elif remaining_duration == 1:
        #         rest_duration = remaining_duration
        #         padding_list.append(rest_duration)
        #         print("B")
        #     else:
        #         rest_duration = remaining_duration % 4
        #         padding_list.append(rest_duration)
        #         print("C")
        #     remaining_duration -= rest_duration
        #     print(f"rest duration = {rest_duration},remaining dur = {remaining_duration}")
        #
        # print(f"Padding list = {padding_list}")
        # return padding_list

    def first_rest(self, time_sig):
        """if time signature is 5/8 then the first rest is a quaver.
        else a crotchet"""
        if time_sig[1] == 8 and time_sig[0] <= 5:
            first_rest_duration = 1
        else:
            first_rest_duration = 2
        print(f"first rest duration = {first_rest_duration}")
        return first_rest_duration

    def makes_new_notes(self, chord) -> list:
        """Calculates all note events for current bar"""
        # calculate how many notes from chord
        note_list = []
        num_notes = randrange(1, len(chord))
        # print(f"Len of chard = {len(chord)}, num of random notes = {num_notes}")

        # add chosen notes to note list
        for i in range(num_notes):
            note_list.append(chord[i])
        print(f"note list = {note_list}")

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
            print(f"added A, B or C additional note")

        # # bubble sort for duplicate notes
        # clean_note_list = self.check_for_duplicate_notes(note_list)
        # print("CLEAN note list = ", clean_note_list)
        return note_list

    # def check_for_duplicate_notes(self, note_list) -> list:
    #     """Removes any dupl;icate notes from not list.
    #         Returns cleaned list"""
    #     clean_note_list = [i for n, i in enumerate(note_list) if i not in note_list[:n]]
    #     print("note list = ", note_list, "clean list = ", clean_note_list)
    #     return clean_note_list

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

        print(f"get event data = {next_notes, next_time_sig, next_duration, next_polyrhythm}")
        return next_notes, next_time_sig, next_duration, next_polyrhythm

    def remove_active_notes(self, active_notes_list):
        """Wipes clean all the old note events from previous bar"""
        for event in active_notes_list:
            print(f"removing event {event}")
            event.remove()

    def pulse_metronome_mark(self):
        """Pulses te metronome mark depending on time sig"""
        new_colour = gray_list[self.tick_count % 4]
        self.bpm_pulse.pen.color = new_colour
        self.bpm_pulse.brush.color = Color(new_colour)

    def terminate(self):
        neoscore.shutdown()

    def reverse_build_from_list(self, time_sig, duration, polyrhythm):
        pass

    def refresh_func(self, time):
        """Main loop, refreshing the UI"""
        # while time.time() <= self.end_time:

        # print(self.tick_count)
        self.pulse_metronome_mark()

        self.tick_count += 1

        if self.tick_count >= self.total_bar_length * 2:
            self.tick_count = 0
            self.remove_active_notes(self.active_note_list)
            chord, time_sig, duration, polyrhythm = self.get_event_data()
            bar_length = (8 / time_sig[1]) * time_sig[0]
            print("bar length = ", time_sig, bar_length)
            # if time <= self.end_time / 2:
            self.active_note_list = self.build_new_events(chord, time_sig, duration, polyrhythm)
            # else:
            #     self.active_note_list = self.reverse_build_from_list(time_sig, duration, polyrhythm)

        # self.terminate()


if __name__ == "__main__":
    for_piano = For_Piano(duration=360)

    # set the refresh function to the score main loop
    # change fps to allow pulse to fade
    neoscore.set_refresh_func(refresh_func=for_piano.refresh_func, target_fps=4)

    neoscore.show(display_page_geometry=False)

