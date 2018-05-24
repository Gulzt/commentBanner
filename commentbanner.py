
"""This module provides the bannerComment plugin
class and supporting methods."""

import sublime
import sublime_plugin
# import textwrap


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
        for region in self.view.sel():
            bannerText = self.view.substr(region)
            if bannerText:
                print(region.begin())
                self.view.erase(edit, region)
                self.view.insert(edit, region.begin(),
                                 self.full_screen_banner(bannerText, Prefs.character))
                region_len = (region.begin() +
                              (Prefs.banner_width - 1) * (2 + len(self.lines)))
                self.view \
                    .selection \
                    .add(sublime.Region(region.begin(), region_len))
        # add the language dependend comment characters
        self.view.run_command("toggle_comment", False)

        # remove the selection of the cursor
        self.view.run_command("move", {"by": "characters", "forward": True})

    def full_screen_banner(self, string, symbol='*'):
        def outer_row():
            return ((Prefs.banner_width - 1) - 1) * symbol + '\n'

        def inner_row():
            result = ""
            self.lines = string.splitlines()
            # textwrap.wrap(string)

            # center each line
            for line in self.lines:
                result += "{2} {0:^{1}}{2}\n".format(line, (Prefs.banner_width - 1) - 4,
                                                     symbol)
            return result
        return outer_row() + inner_row() + outer_row()
