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
        """organises event generation and collects an event list"""

        # init events list
        new_events_list = []

        #######################
        # overall structure
        #######################

        # get new time signatures
        time_sig_treble = TimeSignature(ZERO, self.treble_staff, time_sig)
        time_sig_bass = TimeSignature(ZERO, self.bass_staff, time_sig)
        new_events_list.append(time_sig_treble)
        new_events_list.append(time_sig_bass)

        # calculate new bar length from time sig
        self.total_bar_length = int((8 / time_sig[1]) * time_sig[0])
        # remaining_total_bar_length = self.total_bar_length
        # print("remaining duration = ", remaining_total_bar_length)

        # build quaver x-position list for bar length
        initial_offset = 25
        quaver_mm_unit = 25
        end_offset = 25

        self.quaver_position_list_mm = [initial_offset]
        for quaver in range(self.total_bar_length):
            self.quaver_position_list_mm.append((quaver + 1) * quaver_mm_unit + initial_offset)
        print(f"quaver offset list = {self.quaver_position_list_mm}")

        # change blank bar to fit new time sig
        self.treble_staff.length = Mm(initial_offset + (self.total_bar_length * quaver_mm_unit) + end_offset)
        self.bass_staff.length = Mm(initial_offset + (self.total_bar_length * quaver_mm_unit) + end_offset)
        self.end_line.x = Mm(self.quaver_position_list_mm[-1] + end_offset)
        self.pedal.end_x = Mm(self.quaver_position_list_mm[-1] + end_offset)

        # make quaver position list for iterating through quaver_position_list_mm
        self.treble_next_8th_position = 0
        self.bass_next_8th_position = 0
        next_8th_position_list = [self.treble_next_8th_position,
                                  self.bass_next_8th_position]

        #######################
        # add first rest
        #######################
        for i, hand in enumerate(next_8th_position_list):

            first_rest = self.add_first_rest(time_sig,
                                                self.piano_staff_list[i],
                                                next_8th_position_list[i])
            new_events_list.append(first_rest)


        #######################
        # get note list
        #######################
        # determine note event duration in quavers
        # todo add polyrhytmic into this equation
        note_event_length = (8 / duration[1]) * duration[0]

        # # calc polyrythm extras if applicable
        # if polyrhythm:
        #     poly_nums = (int(polyrhythm[0]), int(polyrhythm[-1]))
        #     polyrhythm_extra = (8 / poly_nums[1]) * poly_nums[0]
        #     note_event_length =
        print(f'note event length for {duration} = ', note_event_length, "quavers")

        # get new notes from harmony
        raw_note_list = self.makes_new_notes(chord)
        # sort into LH & RH & clean duplicates
        treble_note_list, bass_note_list = self.clean_note_list(raw_note_list)
        hand_list = [treble_note_list, bass_note_list]

        #######################
        # block or separate hands
        #######################
        if random() > 0.5:
            # todo check if individual hand list has anything in it
            print("BLOCK CHORD")

            # get position of block chord for each hand
            for i, hand in enumerate(hand_list):
                events, last_8th_position = self.note_position(note_event_length,
                                            next_8th_position_list[i],
                                            hand_list[i],
                                            self.piano_staff_list[i])

                # put rests and notes on master event list
                for e in events:
                    hand.append(e)

                # final padding if required
                end_padding = self.padding_rests(last_8th_position)
                for pad in end_padding:
                    rest = Chordrest(Mm(self.quaver_position_list_mm[last_8th_position]),
                                     self.treble_staff,
                                     None, (pad, 8))
                    new_events_list.append(rest)

        # or treat them as 2 separate events
        else:
            print("SEPARATE HANDS")
            # get position of block chord for each hand
            for i, hand in enumerate(hand_list):
                events, last_8th_position = self.note_position(note_event_length,
                                                               next_8th_position_list[i],
                                                               hand_list[i],
                                                               self.piano_staff_list[i])

                # put rests and notes on master event list
                for e in events:
                    hand.append(e)

                # final padding if required
                print(f"last 1/8th position for {hand} is {last_8th_position}")
                end_padding = self.padding_rests(last_8th_position)
                for pad in end_padding:
                    rest = Chordrest(Mm(self.quaver_position_list_mm[last_8th_position]),
                                     self.treble_staff,
                                     None, (pad, 8))
                    new_events_list.append(rest)

        return treble_note_list, bass_note_list


    def note_position(self, duration_of_note,
                      next_8th_position,
                      hand_list,
                      staff):
        """position of note/ chord event, pads with rest at front if needed.
        :returns list of Chordrest events (chords and rests)"""

        # position the note event somewhere in the remaining bar
        event_list = []
        remaining_duration = self.total_bar_length - next_8th_position
        note_position = randrange(remaining_duration)
        print(f"note position = {note_position}")

        # pad with rests
        rests_padding = self.padding_rests(note_position - remaining_duration)
        print("rests padding = ", rests_padding)
        for i, pad in enumerate(rests_padding):
            if hand_list:
                print(f"next_8th_position = {next_8th_position}")
                rest_pad = Chordrest(Mm(self.quaver_position_list_mm[next_8th_position]),
                                       staff, [],
                                       (pad, 8))
                event_list.append(rest_pad)
                next_8th_position += pad

        # adjust note length to accom rest oadding
        if duration_of_note > remaining_duration - next_8th_position:
            duration_of_note = remaining_duration - next_8th_position

        # calc note coords
        event_x = Mm(self.quaver_position_list_mm[next_8th_position])
        event_duration = (duration_of_note, 8)

        # add note to staff
        if hand_list:
            notes = Chordrest(event_x,
                              staff,
                              hand_list,
                              event_duration)
            event_list.append(notes)

            # how much of bar is left?
            next_8th_position += event_duration

        return event_list, next_8th_position


        #
        # bass_first_rest = Chordrest(Mm(quaver_position_list_mm[0]), self.bass_staff, None, (first_rest_duration, 8))
        # new_events_list.append(bass_first_rest)
        #
        # remaining_total_bar_length -= first_rest_duration
        # treble_next_8th_position = first_rest_duration
        # bass_next_8th_position = first_rest_duration
        # return first_rest_duration
        #
        # #######################
        # # get note list
        # #######################
        #
        # # determine note event duration
        # # todo add polyrhytmic into this equation
        # note_event_length = (8 / duration[1]) * duration[0]
        # print(f'note event length for {duration} = ', note_event_length, "quavers")

        # # note duration greater than bar length + 1 beat rest
        # if note_event_length > remaining_total_bar_length:
        #     note_event_length = remaining_total_bar_length

        # # get new notes from harmony
        # clean_note_list = self.makes_new_notes(chord)

        # sort into LH & RH
        # treble_note_list = []
        # bass_note_list = []
        # for note in clean_note_list:
        #     if Pitch.from_str(note).staff_pos_from_middle_c <= 0:
        #         treble_note_list.append(note)
        #     else:
        #         bass_note_list.append(note)

        #######################
        # Put notes and padding on staffs
        #######################
        #
        # # are treble and bass notes a block?
        # if random() > 0.5:
        #     # todo check if individual hand list has anything in it
        #
        #     print("BLOCK CHORD")
        #     # treble and bass notes are a chordal block
        #     # position note event for both
        #     note_event_position_offset, adj_note_length, remaining_duration = self.note_position(remaining_total_bar_length, note_event_length)
        #
        #     # add rests before event
        #     rests_padding = self.padding_rests(note_event_position_offset)
        #     for i, pad in enumerate(rests_padding):
        #         if treble_note_list:
        #             treble_pad = Chordrest(Mm(quaver_position_list_mm[treble_next_8th_position]), self.treble_staff, [], (pad, 8))
        #             new_events_list.append(treble_pad)
        #             treble_next_8th_position += pad
        #
        #         if bass_note_list:
        #             bass_pad = Chordrest(Mm(quaver_position_list_mm[bass_next_8th_position]), self.bass_staff, [], (pad, 8))
        #             new_events_list.append(bass_pad)
        #             bass_next_8th_position += pad
        #
        #     # calculate params for the note/chord event
        #     if treble_note_list:
        #         treble_event_x = Mm(quaver_position_list_mm[treble_next_8th_position])
        #         treble_event_duration = (adj_note_length, 8)
        #
        #     # calc remaining duration for end pad
        #         treble_remaining_duration = remaining_duration
        #         treble_next_8th_position += adj_note_length
        #
        #     if bass_note_list:
        #         bass_event_x = Mm(quaver_position_list_mm[bass_next_8th_position])
        #         bass_event_duration = (adj_note_length, 8)
        #
        #         bass_remaining_duration = remaining_duration
        #         bass_next_8th_position += adj_note_length
        #
        # # or treat them as 2 separate events
        # else:
        #     print("SEPARATE HANDS")
        #     # note_position), int(duration_of_note), int(remaining_duration)
        #     note_event_position_offset, adj_note_length, remaining_duration = self.note_position(remaining_total_bar_length, note_event_length)
        #
        #     # add rests before event for treble clef
        #     rests_padding = self.padding_rests(note_event_position_offset)
        #     for i, pad in enumerate(rests_padding):
        #         treble_pad = Chordrest(Mm(quaver_position_list_mm[treble_next_8th_position]), self.treble_staff, [], (pad, 8))
        #         new_events_list.append(treble_pad)
        #         treble_next_8th_position += pad
        #
        #     # calc note coords
        #     treble_event_x = Mm(quaver_position_list_mm[treble_next_8th_position])
        #     treble_event_duration = (adj_note_length, 8)
        #     treble_next_8th_position += adj_note_length
        #
        #     # add rests before event for bass clef
        #     note_event_position_offset, adj_note_length, remaining_duration = self.note_position(remaining_total_bar_length, note_event_length)
        #
        #     # add rests before event for bass clef
        #     rests_padding = self.padding_rests(note_event_position_offset)
        #     for i, pad in enumerate(rests_padding):
        #         bass_pad = Chordrest(Mm(quaver_position_list_mm[bass_next_8th_position]), self.bass_staff, [], (pad, 8))
        #         new_events_list.append(bass_pad)
        #         bass_next_8th_position += pad
        #
        #     # calc note coords
        #     bass_event_x = Mm(quaver_position_list_mm[bass_next_8th_position])
        #     bass_event_duration = (adj_note_length, 8)
        #     bass_next_8th_position += adj_note_length
        #
        # treble_remaining_duration = remaining_duration
        # bass_remaining_duration = remaining_duration
        #
        # # print("event durations", treble_event_duration, bass_event_duration)
        # # print them on the staves
        # if treble_note_list:
        #     treble_notes = Chordrest(treble_event_x,
        #                              self.treble_staff,
        #                              treble_note_list,
        #                              treble_event_duration)
        #     new_events_list.append(treble_notes)
        #
        # if bass_note_list:
        #     bass_notes = Chordrest(bass_event_x,
        #                            self.bass_staff,
        #                            bass_note_list,
        #                            bass_event_duration)
        #     new_events_list.append(bass_notes)
        #
        # #######################
        # # final padding
        # #######################
        #
        # print(f"remaining durations. Treble = {treble_remaining_duration}, bass = {bass_remaining_duration}")
        #
        # treble_end_padding_rests_list = self.padding_rests(treble_remaining_duration)
        # for i, pad in enumerate(treble_end_padding_rests_list):
        #     treble_first_rest = Chordrest(Mm(quaver_position_list_mm[treble_next_8th_position]), self.treble_staff, None, (pad, 8))
        #     new_events_list.append(treble_first_rest)
        #     treble_next_8th_position += pad
        #
        # bass_end_padding_rests_list = self.padding_rests(bass_remaining_duration)
        # for i, pad in enumerate(bass_end_padding_rests_list):
        #     bass_first_rest = Chordrest(Mm(quaver_position_list_mm[bass_next_8th_position]), self.bass_staff, None, (pad, 8))
        #     new_events_list.append(bass_first_rest)
        #     bass_next_8th_position += pad
        #
        # return new_events_list

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

    def add_first_rest(self, time_sig, staff, next_event_list):
        """if time signature is 5/8 then the first rest is a quaver.
                else a crotchet.
                Make a Chordrest.
                Return: Chordrest"""
        if time_sig[1] == 8 and time_sig[0] <= 5:
            first_rest_duration = 1
        else:
            first_rest_duration = 2
        print(f"first rest duration = {first_rest_duration}")

        first_rest = Chordrest(Mm(self.quaver_position_list_mm[0]), staff, None, (first_rest_duration, 8))
        next_event_list += first_rest_duration
        return first_rest

    def padding_rests(self, last_8th_position) -> list:
        remaining_duration = self.total_bar_length - last_8th_position
        padding_list = []
        while remaining_duration > 0:
            print(f"padding remaining_total_bar_length {remaining_duration}")
            if remaining_duration % 4 == 0:
                rest_duration = 4
                print("A")
            elif remaining_duration % 4 == 1:
                rest_duration = 1
                print("B")
            elif remaining_duration % 4 == 2:
                rest_duration = 2
                print("B")
            elif remaining_duration % 4 == 3:
                rest_duration = 3
                print("B")

            padding_list.append(rest_duration)
            remaining_duration -= rest_duration
            print(f"rest duration = {rest_duration},remaining dur = {remaining_duration}")

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
        print(f"Len of chard = {len(chord)}, num of random notes = {num_notes}")

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
            print(f"added A, b or C additional note")

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
            if time <= self.end_time / 2:
                self.active_note_list = self.build_new_events(chord, time_sig, duration, polyrhythm)
            else:
                self.active_note_list = self.reverse_build_from_list(time_sig, duration, polyrhythm)

        # self.terminate()


if __name__ == "__main__":
    for_piano = For_Piano(duration=360)

    # set the refresh function to the score main loop
    # change fps to allow pulse to fade
    neoscore.set_refresh_func(refresh_func=for_piano.refresh_func, target_fps=4)

    neoscore.show(display_page_geometry=False)

