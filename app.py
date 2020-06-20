import feedparser
import npyscreen
import json
import curses
import webbrowser


def open_feed_json_file():
    with open('feed.json') as json_file:
        return json.load(json_file)['feeds']


def parse_feed_url(feed_url):
    return feedparser.parse(feed_url)


class TitleTextItem(npyscreen.MultiLineAction):
    def actionHighlighted(self, act_on_this, key_press):
        self.parent.action_callback(str(act_on_this))


class EntryListForm(npyscreen.FormMultiPage):
    def create(self):
        self.add_handlers({
            curses.ascii.CAN: self.parentApp.switchFormPrevious,
            ord('q'): self.parentApp.switchFormPrevious
        })
        entry_list = parse_feed_url(
            self.parentApp.get_url_by_rss_name(self.name))['entries']
        self.entries = {}
        for entry in entry_list:
            self.entries[entry['title']] = entry
        self.add_widget_intelligent(TitleTextItem, values=[
                                    entry['title'] for entry in entry_list])

    def action_callback(self, title):
        webbrowser.open(self.entries[title]['link'])


class SourceSelectionForm(npyscreen.FormMultiPage):
    def create(self):
        self.add_handlers({
            ord('q'): self.parentApp.onCleanExit
        })
        source_list = open_feed_json_file()
        self.add_widget_intelligent(TitleTextItem, values=[
                                    source['title'] for source in source_list])

    def action_callback(self, title):
        self.parentApp.switchForm(title)


class Application(npyscreen.NPSAppManaged):
    def onStart(self):
        self.addForm('MAIN', SourceSelectionForm, name='Select Source')

        self.rss_feeds = {}
        for feed in open_feed_json_file():
            self.rss_feeds[feed['title']] = feed['url']
            self.addFormClass(
                feed['title'], EntryListForm, name=feed['title'])

    def get_url_by_rss_name(self, name):
        return self.rss_feeds[name]

    def onCleanExit(self, *args, **keywords):
        self.switchForm(None)


if __name__ == '__main__':
    Application().run()
