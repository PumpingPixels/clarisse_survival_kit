from clarisse_survival_kit.settings import *
from clarisse_survival_kit.app import *
from clarisse_survival_kit.utility import *
import logging
import os


def preferences_list():
    preferences = {}
    preferences['global_shading_layer'] = {'description': 'Global Shading Layer', 'kind': 'ShadingLayer'}
    preferences['megascans_context'] = {'description': 'Context for imported Megascans assets', 'kind': 'OfContext'}
    return preferences


def preferences_gui(**kwargs):
    ix = get_ix(kwargs.get('ix'))
    preferences = preferences_list()
    class EventRewire(ix.api.EventObject):
        # These are the called functions by the connect. It is more flexible to make a function for each button
        def ok(self, sender, evtid):
            sender.get_window().hide()  # Hide the window, if it is done, the window is destroy
            for key in preferences:
                set_preference(key, line_edits[key].get_text())

        def cancel(self, sender, evtid):
            sender.get_window().hide()  # Hide the window, if it is done, the window is destroy

        def set_preference(self, key):
            if check_selection(ix.selection, (preferences[key]['kind'],)):
                line_edits[key].set_text(str(ix.selection[0]))

        def clear_preference(self, key):
            line_edits[key].set_text('')

        def buttonClick(self, sender, evtid):
            if 'set_' in sender.identifier:
                key = sender.identifier.replace('set_', '')
                self.set_preference(key)
            if 'clear' in sender.identifier:
                key = sender.identifier.replace('clear_', '')
                self.clear_preference(key)

    class GuiPushButton(ix.api.GuiPushButton):
        def __init__(self, identifier, *args, **kwargs):
            ix.api.GuiPushButton.__init__(self, *args, **kwargs)
            self.connect(self, 'EVT_ID_PUSH_BUTTON_CLICK',
                         self.on_click)
            self.identifier = identifier

        def on_click(self, sender, evtid):
            event_rewire.buttonClick(self, evtid)

    # Window creation
    vertical_spacing = 20
    i = 1
    line_edits = {}
    set_buttons = {}
    event_rewire = EventRewire()

    clarisse_win = ix.application.get_event_window()
    window = ix.api.GuiWindow(clarisse_win, 900, 450, 554, 520)
    window.set_title('Clarisse Survival Kit Preferences')

    # Main widget creation
    panel = ix.api.GuiPanel(window, 0, 0, window.get_width(), window.get_height())
    panel.set_constraints(ix.api.GuiWidget.CONSTRAINT_LEFT, ix.api.GuiWidget.CONSTRAINT_TOP,
                          ix.api.GuiWidget.CONSTRAINT_RIGHT, ix.api.GuiWidget.CONSTRAINT_BOTTOM)

    # Form generation
    for key in preferences:
        ix.api.GuiLabel(panel, 10, vertical_spacing * i, 400, 22, preferences[key]['description'])
        i += 1
        line_edits[key] = ix.api.GuiLineEdit(panel, 10, vertical_spacing * i, 340, 22)
        line_edits[key].set_text(get_preference(key, ''))
        set_buttons['set_{key}'.format(key=key)] = GuiPushButton('set_{key}'.format(key=key), panel, 360,
                                                                 vertical_spacing * i, 90, 22, "Set to selected")
        set_buttons['set_{key}'.format(key=key)] = GuiPushButton('clear_{key}'.format(key=key), panel, 454,
                                                                 vertical_spacing * i, 90, 22, "Clear")
        i += 1
    i += 1
    ok_button = ix.api.GuiPushButton(panel, 10, vertical_spacing * i, 100, 22, "OK")
    event_rewire.connect(ok_button, 'EVT_ID_PUSH_BUTTON_CLICK', event_rewire.ok)
    cancel_button = ix.api.GuiPushButton(panel, 120, vertical_spacing * i, 100, 22, "Cancel")
    event_rewire.connect(cancel_button, 'EVT_ID_PUSH_BUTTON_CLICK', event_rewire.cancel)

    # Send all info to clarisse to generate window
    window.show()
    while window.is_shown():    ix.application.check_for_events()
    window.destroy()


def set_preference(key, value, **kwargs):
    ix = get_ix(kwargs.get("ix"))
    preferences = ix.application.get_prefs(ix.api.AppPreferences.MODE_APPLICATION)
    if preferences.item_exists("clarisse_survival_kit", key):
        preferences.set_string_value("clarisse_survival_kit", key, value)
    else:
        preferences.add_string("clarisse_survival_kit", key, value)


def get_preference(key, default=None, **kwargs):
    ix = get_ix(kwargs.get("ix"))
    preferences = ix.application.get_prefs(ix.api.AppPreferences.MODE_APPLICATION)
    if preferences.item_exists("clarisse_survival_kit", key):
        return preferences.get_string_value("clarisse_survival_kit", key)
    else:
        return default


def get_ix(ix_local):
    """Simple function to check if ix is imported or not."""
    try:
        ix
    except NameError:
        return ix_local
    else:
        return ix


if __name__ == '__main__':
    preferences_gui()