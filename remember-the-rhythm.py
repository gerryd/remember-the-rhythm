#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gi.repository import GObject
from gi.repository import Peas
from gi.repository import RB
from gi.repository import Gio
from gi.repository import GLib

from gi.repository.GLib import Variant
from remember_prefs import RememberPreferences

import logging
import sys

GSETTINGS_KEY = "org.gnome.rhythmbox.plugins.remember-the-rhythm"
KEY_PLAYBACK_TIME = 'playback-time'
KEY_LOCATION = 'last-entry-location'
KEY_PLAYLIST = 'playlist'
KEY_BROWSER_VALUES = 'browser-values'
KEY_PLAY_STATE = 'play-state'
KEY_SOURCE = 'source'
KEY_STARTUP_STATE = 'startup-state'

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
logger = logging.getLogger("remember-the-rhythm")

class RememberTheRhythm(GObject.Object, Peas.Activatable):
    __gtype_name = 'RememberTheRhythm'
    object = GObject.property(type=GObject.Object)

    first_run = False

    def __init__(self):
        GObject.Object.__init__(self)
        self.settings = Gio.Settings.new(GSETTINGS_KEY)
        self.location = self.settings.get_string(KEY_LOCATION)
        self.playlist = self.settings.get_string(KEY_PLAYLIST)
        self.playback_time = self.settings.get_uint(KEY_PLAYBACK_TIME)
        self.browser_values_list = self.settings.get_value(KEY_BROWSER_VALUES)
        self.play_state = self.settings.get_boolean(KEY_PLAY_STATE)
        self.source = None
        self.source_name = self.settings.get_string(KEY_SOURCE)
        self.startup_state = self.settings.get_uint(KEY_STARTUP_STATE)

    def do_activate(self):
        logger.debug("do_activate")
        self.shell = self.object
        self.library = self.shell.props.library_source
        self.shell_player = self.shell.props.shell_player
        self.playlist_manager = self.shell.props.playlist_manager
        self.db = self.shell.props.db
        self.backend_player = self.shell_player.props.player
        self.startup_volume = self.shell_player.get_volume()[1]
        logger.debug("saved startup volume as %f" % self.startup_volume)

        def try_load(*args):
            if len(self.playlist_manager.get_playlists()) == 0:
                GLib.idle_add(self._load_complete)
            else:
                self._load_complete()

        self.shell.props.db.connect('load-complete', try_load)

    def do_deactivate(self):
        self.first_run = True

    def _connect_signals(self):
        self.shell_player.connect('playing-changed', self.playing_changed)
        self.shell_player.connect('playing-source-changed', self.playing_source_changed)
        self.shell_player.connect('elapsed-changed', self.elapsed_changed)

    def _load_complete(self, *args, **kwargs):
        """
        called when load-complete signal is fired - this plays what was remembered
        :param args:
        :param kwargs:
        :return:
        """

        logger.debug("load_complete")
        if not self.location:
            self._scenario = 4
            self.first_run = True
            self._connect_signals()
            return

        entry = self.db.entry_lookup_by_location(self.location)
        logger.debug(self.location)
        if not entry:
            self.first_run = True
            self._connect_signals()
            return

        if self.playlist:
            playlists = self.playlist_manager.get_playlists()
            for playlist in playlists:
                if playlist.props.name == self.playlist:
                    self.source = playlist
                    break

        # now switch to the correct source to play the remembered entry
        if not self.source:
            logger.debug(self.location)
            self.source = self.shell.guess_source_for_uri(self.location)

        self.shell_player.set_playing_source(self.source)
        #self.shell_player.set_selected_source(self.source)

        # when dealing with playing we start a thread (so we don't block the UI
        # each stage we wait a bit for stuff to start working
        time = self.playback_time

        def scenarios():
            logger.debug("scenario %d" % self._scenario)

            if self._scenario == 1:
                # always mute the sound - this helps with the pause scenario
                # where we have to start playing first before pausing... but
                # we dont want to here what is playing

                #p = subprocess.Popen(['amixer set Master mute > /dev/null'], shell=True, stdout=subprocess.PIPE)
                logger.debug("setting volume to zero")
                self.shell_player.set_volume(0.0)
                self._scenario += 1
                return True

            if self._scenario == 2:
                # play the entry for the source chosen
                logger.debug(entry)
                logger.debug(self.source)
                self.shell_player.play_entry(entry, self.source)
                #self.shell_player.set_playing_time(time)
                self._scenario += 1
                return True

            if self._scenario == 3:
                # now pause if the preferences options calls for this.
                logger.debug(self.play_state)
                logger.debug(self.startup_state)
                if (not self.play_state and self.startup_state == 1) or \
                                self.startup_state == 2:
                    logger.debug("pausing")
                    self.shell_player.pause()
                    # note for radio streams rhythmbox doesnt pause - it can only stop
                    # so basically nothing we can do - just let the stream play
                    self._scenario += 1
                    return True

            self._scenario = 4
            # for the playing entry attempt to move to the remembered time
            try:
                self.shell_player.set_playing_time(time)
            except:
                # fallthrough ... some streams - radio - cannot seek
                pass

            # unmute and end the thread
            logger.debug("setting volume to %f" % self.startup_volume)
            self.shell_player.set_volume(self.startup_volume)
            #p = subprocess.Popen(['amixer set Master unmute > /dev/null'], shell=True, stdout=subprocess.PIPE)
            return False

        self._scenario = 1
        GLib.timeout_add_seconds(1, scenarios)

        self._connect_signals()
        self.first_run = True

    def playing_source_changed(self, player, source, data=None):
        """
        called when user changes what is playing in a different source
        :param player:
        :param source:
        :param data:
        :return:
        """
        logger.debug("playing source changed")
        if self._scenario != 4:
            return

        if source:
            self.source = source
            if self.source in self.playlist_manager.get_playlists():
                self.settings.set_string('playlist', self.source.props.name)
                self.settings.set_string('source', '')
            else:
                self.settings.set_string('playlist', '')
                self.settings.set_string('source', self.source.props.name)
                self.source_name = self.source.props.name

    def playing_changed(self, player, playing, data=None):
        """
        called when user changes what is actually playing
        :param player:
        :param playing:
        :param data:
        :return:
        """

        def init_source():
            logger.debug("init source")
            if self.source:
                views = self.source.get_property_views()
                for i, view in enumerate(views):
                    if i in self.browser_values_list:
                        value = self.browser_values_list[i]
                        if value:
                            view.set_selection(value)
                self.shell.props.display_page_tree.select(self.source)
                # self.shell_player.jump_to_current()

        logger.debug("playing_changed")
        if self._scenario != 4:
            return

        entry = self.shell_player.get_playing_entry()

        if entry:
            logger.debug("found entry")
            success, self.play_state = self.shell_player.get_playing()

            self.location = entry.get_string(RB.RhythmDBPropType.LOCATION)
            logger.debug(self.location)
        else:
            logger.debug("not found entry")
            self.play_state = False
            self.location = ""

        GLib.idle_add(self.save_rhythm, 0)


    def elapsed_changed(self, player, entry, data=None):
        """
        called when something is playing - remembers the time within a track
        :param player:
        :param entry:
        :param data:
        :return:
        """
        if not self.first_run:
            return

        if self._scenario != 4:
            try:
                self.shell_player.set_playing_time(self.playback_time)
            except:
                pass

        try:
            if self.playback_time:
                save_time = True
            else:
                save_time = False

            if save_time and self.playback_time == self.shell_player.get_playing_time()[1]:
                save_time = False

            self.playback_time = self.shell_player.get_playing_time()[1]

            GLib.idle_add(self.save_rhythm)

        except:
            pass


    def save_rhythm(self, pb_time=None):
        """
        This actually saves info into gsettings
        :param pb_time:
        :return:
        """
        if self.location:
            pb_time = pb_time is None and self.playback_time or pb_time is None
            self.settings.set_uint(KEY_PLAYBACK_TIME, pb_time)
            self.settings.set_string(KEY_LOCATION, self.location)
            #logger.debug("last location %s" % self.location)
        self.settings.set_boolean(KEY_PLAY_STATE, self.play_state)

        if self.source:
            views = self.source.get_property_views()
            browser_values_list = []
            for view in views:
                browser_values_list.append(view.get_selection())
            self.browser_values_list = Variant('aas', browser_values_list)
            self.settings.set_value(KEY_BROWSER_VALUES, self.browser_values_list)


    def _import(self):
        """
        dummy routine to stop pycharm from optimising out the preferences import
        :return:
        """
        RememberPreferences()
