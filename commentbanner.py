import sublime
import sublime_plugin


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
    """Create a comment box around the selection.

    * supports multi-line selection
    * supports multi-cursor selection
    """

    def __init__(self, *args, **kw):
        super(BannerCommand, self).__init__(*args, **kw)
        Prefs.load()

    def run(self, edit):
        view = self.view

        for region in view.sel():
            lines = view.full_line(region)
            if not lines.empty():
                content = view.substr(lines)
                banner = self.make_banner(content, Prefs.banner_width, Prefs.character)
                view.replace(edit, lines, banner)
                view.sel().add(sublime.Region(lines.begin(), lines.begin() + len(banner)))

        view.run_command('move', {'by': 'characters', 'forward': True})

    def get_comment_charaters(self):
        shell_vars = self.view.meta_info('shellVariables', 0)

        # transform the list of dicts into a single dict
        all_vars = {}
        for v in shell_vars:
            if 'name' in v and 'value' in v:
                all_vars[v['name']] = v['value']

        return all_vars.setdefault('TM_COMMENT_START', '')

    def make_banner(self, string, banner_width, symbol):
        comment_characters = self.get_comment_charaters()

        outer = comment_characters + (Prefs.banner_width - len(comment_characters)) * symbol + '\n'

        inner = ''
        for line in string.splitlines():
            # center each line
            inner += comment_characters + "{2} {0:^{1}}{2}\n".format(line, Prefs.banner_width - len(comment_characters) - 3, symbol)

        return outer + inner + outer
