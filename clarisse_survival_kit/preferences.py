from clarisse_survival_kit.utility import *


def preferences_list():
    preferences = []
    preferences.append({'key': 'contextname_format', 'description': 'Customize Contextname Format', 'kind': str})
    preferences.append({'key': 'override_bridge_settings', 'description': 'Override Bridge Export settings to highest available quality', 'kind': bool})
    # preferences.append({'key': 'global_shading_layer', 'description': 'Global Shading Layer', 'kind': 'ShadingLayer'})
    # preferences.append(
    #     {'key': 'combiner_context', 'description': 'Context for collect combiners containig 3d assets',
    #      'kind': 'OfContext'})
    # preferences.append(
    #     {'key': 'megascans_surface_context', 'description': 'Context for imported Megascans surfaces', 'kind': 'OfContext'})
    # preferences.append(
    #     {'key': 'megascans_3d_context', 'description': 'Context for imported Megascans 3D asset', 'kind': 'OfContext'})
    # preferences.append(
    #     {'key': 'megascans_3dplant_context', 'description': 'Context for imported Megascans 3D plants', 'kind': 'OfContext'})
    return preferences


def preferences_gui(**kwargs):
    ix = get_ix(kwargs.get('ix'))
    preferences = preferences_list()

    class EventRewire(ix.api.EventObject):
        def ok(self, sender, evtid):
            self.apply(self, sender, evtid)
            sender.get_window().hide()

        def apply(self, sender, evtid):
            for pref_id in range(len(preferences)):
                key = preferences[pref_id]['key']
                set_preference(key, line_edits[pref_id].get_text())
            ok_button.disable()
            apply_button.disable()

        def cancel(self, sender, evtid):
            sender.get_window().hide()

        def enable_apply_buttons(self, sender, evtid):
            ok_button.enable()
            apply_button.enable()

        def set_preference(self, sender, evtid, id):
            if check_selection(ix.selection, (preferences[id]['kind'],)):
                line_edits[id].set_text(str(ix.selection[0]))
            self.enable_apply_buttons(sender, evtid)

        def clear_preference(self, sender, evtid, id):
            line_edits[id].set_text('')
            ok_button.enable()
            apply_button.enable()

        def buttonClick(self, sender, evtid):
            if 'set_' in sender.identifier:
                id = int(sender.identifier.replace('set_', ''))
                self.set_preference(sender, evtid, id)
            if 'clear' in sender.identifier:
                id = int(sender.identifier.replace('clear_', ''))
                self.clear_preference(sender, evtid, id)

    class GuiPushButton(ix.api.GuiPushButton):
        def __init__(self, identifier, *args, **kwargs):
            ix.api.GuiPushButton.__init__(self, *args, **kwargs)
            self.connect(self, 'EVT_ID_PUSH_BUTTON_CLICK',
                         self.on_click)
            self.identifier = identifier

        def on_click(self, sender, evtid):
            event_rewire.buttonClick(self, evtid)

    # Window creation
    vertical_spacing = 26
    labels = []
    line_edits = []
    set_buttons = []
    clear_buttons = []
    event_rewire = EventRewire()

    clarisse_win = ix.application.get_event_window()
    window = ix.api.GuiWindow(clarisse_win, 900, 450, 525, (len(preferences) + 4) * 44 + 10)
    window.set_title('Clarisse Survival Kit Preferences')

    # Main widget creation
    panel = ix.api.GuiPanel(window, 0, 0, window.get_width(), window.get_height())
    panel.set_constraints(ix.api.GuiWidget.CONSTRAINT_LEFT, ix.api.GuiWidget.CONSTRAINT_TOP,
                          ix.api.GuiWidget.CONSTRAINT_RIGHT, ix.api.GuiWidget.CONSTRAINT_BOTTOM)

    # Form generation
    ui_id = 1
    pref_id = 0
    for pref_id in range(len(preferences)):
        key = preferences[pref_id]['key']
        labels.append(
            ix.api.GuiLabel(panel, 10, vertical_spacing * ui_id + 4, 400, 22, preferences[pref_id]['description']))
        ui_id += 1
        line_edits.append(ix.api.GuiLineEdit(panel, 10, vertical_spacing * ui_id, 340, 22))
        line_edits[pref_id].set_text(get_preference(key, ''))
        event_rewire.connect(line_edits[pref_id], 'EVT_ID_LINE_EDIT_VALUE_EDITED',
                             event_rewire.enable_apply_buttons)
        set_buttons.append(GuiPushButton('set_{id}'.format(id=pref_id), panel, 360,
                                         vertical_spacing * ui_id, 90, 22, "Set to selected"))
        clear_buttons.append(GuiPushButton('clear_{id}'.format(id=pref_id), panel, 455,
                                           vertical_spacing * ui_id, 60, 22, "Clear"))
        ui_id += 1
    ui_id += 3
    ok_button = ix.api.GuiPushButton(panel, 220, vertical_spacing * ui_id, 95, 22, "OK")
    event_rewire.connect(ok_button, 'EVT_ID_PUSH_BUTTON_CLICK', event_rewire.ok)
    ok_button.disable()
    cancel_button = ix.api.GuiPushButton(panel, 320, vertical_spacing * ui_id, 95, 22, "Cancel")
    event_rewire.connect(cancel_button, 'EVT_ID_PUSH_BUTTON_CLICK', event_rewire.cancel)
    apply_button = ix.api.GuiPushButton(panel, 420, vertical_spacing * ui_id, 95, 22, "Apply")
    event_rewire.connect(apply_button, 'EVT_ID_PUSH_BUTTON_CLICK', event_rewire.apply)
    apply_button.disable()

    # Send all info to clarisse to generate window
    window.show()
    while window.is_shown():
        ix.application.check_for_events()
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
