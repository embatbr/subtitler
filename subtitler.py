# -*- coding: utf-8 -*-


"""author: Eduardo Tenório

Program written without internet. This is hell!

The program command line is 'python3.3 subtitler --in=<value>[ <optional_args>]',
where each argument is in the format '--<key>=<value>'. The only necessary argument
is the input (key: '--in'). If an output filename is not given, the output will
be saved over the input file.

Arguments:
--in: Name of the input file.
--out: Name of the output file.
--time: Time in the format '[-]hh:mm:ss,MMM'. The minus signal indicates to
decrement time. No signal means increment.

Arguments TODO:
--nodeaf: Remove subtitles for deafs.
--subs: list of subtitles changed by <--time>. If no value is given, change all.
"""


import re, sys


# example: '00:00:05,652 --> 00:00:07,780'
TIME_LENGTH = 12
TIME_REGEX = r'([0-9]{2}:){2}[0-9]{2},[0-9]{3}'
PERIOD_REGEX = r'%s[ ]*-->[ ]*%s$' % (TIME_REGEX, TIME_REGEX)

TIME_REGEX_OBJECT = re.compile(r'%s$' % TIME_REGEX)
PERIOD_REGEX_OBJECT = re.compile(PERIOD_REGEX)


# class Time and auxiliar functions

class Time(object):
    """A Time object contains hours, minutes, seconds and miliseconds.
    """

    def __init__(self, hours, minutes, seconds, miliseconds):
        self.time = hours*60*60*1000 + minutes*60*1000 + seconds*1000 + miliseconds

    def __str__(self):
        hours = self.time // (60*60*1000)
        minutes = (self.time % (60*60*1000)) // (60*1000)
        seconds = ((self.time % (60*60*1000)) % (60*1000)) // 1000
        miliseconds = self.time % 1000

        ret = '%02d:%02d:%02d,%03d' % (hours, minutes, seconds, miliseconds)
        return ret

    def increase_time(self, time, factor=1):
        self.time = self.time + factor*time.time


def string_to_time(str_time):
    hours = int(str_time[0 : 2])
    minutes = int(str_time[3 : 5])
    seconds = int(str_time[6 : 8])
    miliseconds = int(str_time[9 : ])

    return Time(hours, minutes, seconds, miliseconds)


# class Subtitle

class Subtitle(object):
    """A Subtitle object is composed of
    """

    def __init__(self, start_time, end_time, content):
        self.start_time = start_time
        self.end_time = end_time
        self.content = content

    def __str__(self):
        ret = '%s --> %s\n' % (self.start_time, self.end_time)
        ret = '%s%s\n' % (ret, self.content)
        return ret

    def increase_time(self, time, factor=1):
        self.start_time.increase_time(time, factor)
        self.end_time.increase_time(time, factor)


# class SubtitleList

class SubtitleList(object):
    """The object representation of the SRT file.
    """

    def __init__(self, subtitles):
        self.subtitles = subtitles

    def __str__(self):
        ret = ''

        num_subtitles = len(self.subtitles)
        for (i, subtitle) in zip(range(num_subtitles), self.subtitles):
            ret = '%s%d\n%s\n' % (ret, i + 1, subtitle)

        return ret.strip()

    def increase_time(self, time, factor=1, indexes=None):
        for subtitle in self.subtitles:
            subtitle.increase_time(time, factor)


# working functions

def remove_index_and_find_periods_indexes(lines):
    """Search for pattern PERIOD_REGEX, delete the previous element (index) and
    find the pattern's new index. Return a list of these indexes.
    """
    indexes = []
    for line in lines:
        if PERIOD_REGEX_OBJECT.match(line):
            index = lines.index(line)
            del lines[index - 1]
            indexes.append(index - 1)

    return indexes

def file_reader(filename):
    """Read a SRT file and return a list of Subtitle objects.
    """
    subfile = open(filename)
    lines = subfile.readlines()
    subfile.close()

    lines = [line[0 : -1] for line in lines if line != '\n']
    indexes = remove_index_and_find_periods_indexes(lines)

    subtitles = []
    num_indexes = len(indexes)
    for i in range(num_indexes):
        begin = indexes[i]
        end = indexes[i + 1] if (i + 1) < num_indexes else len(lines)

        period = lines[begin]
        start_time = string_to_time(period[0 : TIME_LENGTH])
        end_time = string_to_time(period[-TIME_LENGTH : ])
        content = '\n'.join(lines[begin + 1 : end])

        subtitle = Subtitle(start_time, end_time, content)
        subtitles.append(subtitle)

    return SubtitleList(subtitles)


if __name__ == '__main__':
    args = sys.argv[1 : ]

    if args != []:
        arg_dict = {}
        for arg in args:
            (key, value) = (arg, True)
            if '=' in arg:
                (key, value) = tuple(arg.split('=', 1))
            arg_dict[key] = value

        input_name = arg_dict['--in']
        output_name = arg_dict['--out'] if '--out' in arg_dict else input_name
        time = arg_dict['--time'] if '--time' in arg_dict else None
        indexes = arg_dict['--indexes'] if '--indexes' in arg_dict else None
        nodeaf = arg_dict['--nodeaf'] if '--nodeaf' in arg_dict else None

        subtitle_list = file_reader(input_name)

        if time:
            factor = 1
            if time[0] == '-':
                factor = -1
                time = time[1 : ]

            time = string_to_time(time)
            subtitle_list.increase_time(time, factor=factor, indexes=indexes)

        # if nodeaf:
        #     subtitle_list.remove_deaf_subtitles()

        output_file = open(output_name, 'w')
        print(subtitle_list, file=output_file)