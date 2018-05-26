
"""This module provides the bannerComment plugin
class and supporting methods."""

import sublime
import sublime_plugin
# import textwrap


def build_comment_data(view, pt):
    """From Default.sublime-package/comment.py."""

    shell_vars = view.meta_info("shellVariables", pt)
    if not shell_vars:
        return ([], [])

    # transform the list of dicts into a single dict
    all_vars = {}
    for v in shell_vars:
        if 'name' in v and 'value' in v:
            all_vars[v['name']] = v['value']

    line_comments = []
    block_comments = []

    # transform the dict into a single array of valid comments
    suffixes = [""] + ["_" + str(i) for i in range(1, 10)]
    for suffix in suffixes:
        start = all_vars.setdefault("TM_COMMENT_START" + suffix)
        end = all_vars.setdefault("TM_COMMENT_END" + suffix)
        disable_indent = all_vars.setdefault("TM_COMMENT_DISABLE_INDENT" + suffix)

        if start and end:
            block_comments.append((start, end, disable_indent == 'yes'))
            block_comments.append((start.strip(), end.strip(), disable_indent == 'yes'))
        elif start:
            line_comments.append((start, disable_indent == 'yes'))
            line_comments.append((start.strip(), disable_indent == 'yes'))

    return (line_comments, block_comments)


class Prefs:

    @staticmethod
    def read():
        settings = sublime.load_settings('CommentBanner.sublime-settings')
        Prefs.character = settings.get('character', '*')
        Prefs.banner_width = settings.get('banner_width', 80)

    @staticmethod
    def load():
        settings = sublime.load_settings('CommentBanner.sublime-settings')
        settings.add_on_change('character', Prefs.read)
        settings.add_on_change('banner_width', Prefs.read)
        Prefs.read()


class BannerCommand(sublime_plugin.TextCommand):
    """create a fancy comment box around the text selection.
    - supports multi line selection
    - supports multi cursor selection
    """

    def __init__(self, *args, **kw):
        super(BannerCommand, self).__init__(*args, **kw)
        Prefs.load()

    def run(self, edit):
        self.comment_character_width = len(build_comment_data(self.view, self.view.sel()[0].begin())[0][0][0]) - 1

        for region in self.view.sel():
            bannerText = self.view.substr(region)
            if bannerText:
                print(region.begin())
                self.view.erase(edit, region)
                self.view.insert(edit, region.begin(),
                                 self.full_screen_banner(bannerText, Prefs.character))
                region_len = (region.begin() +
                              (Prefs.banner_width - self.comment_character_width) * (2 + len(self.lines)))
                self.view \
                    .selection \
                    .add(sublime.Region(region.begin(), region_len))
        # add the language dependend comment characters
        self.view.run_command("toggle_comment", False)

        # remove the selection of the cursor
        self.view.run_command("move", {"by": "characters", "forward": True})

    def full_screen_banner(self, string, symbol='*'):
        def outer_row():
            return ((Prefs.banner_width - self.comment_character_width) - 1) * symbol + '\n'

        def inner_row():
            result = ""
            self.lines = string.splitlines()
            # textwrap.wrap(string)

            # center each line
            for line in self.lines:
                result += "{2} {0:^{1}}{2}\n".format(line, (Prefs.banner_width - self.comment_character_width) - 4,
                                                     symbol)
            return result
        return outer_row() + inner_row() + outer_row()
