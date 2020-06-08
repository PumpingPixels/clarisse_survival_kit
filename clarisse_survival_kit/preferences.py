from clarisse_survival_kit.utility import *


def preferences_list():
    preferences = []
    preferences.append(
        {'key': 'megascans_naming', 'description': 'Customize naming convention for imported Megascans assets',
         'kind': str, 'default': '{dirname}'})
    preferences.append(
        {'key': 'megascans_import_context', 'description': 'Top-level context to store imported Megascans assets',
         'kind': 'OfContext'})
    preferences.append(
        {'key': 'combiner_context', 'description': 'Context for collecting combiners containing 3d assets',
         'kind': 'OfContext'})
    preferences.append({'key': 'global_shading_layer', 'description': 'Global Shading Layer', 'kind': 'ShadingLayer'})
    preferences.append({'key': 'override_bridge_settings',
                        'description': "Override Bridge's export settings (use highest available resolution and LOD)",
                        'kind': bool})
    return preferences


# class TerrainGui(ix.api.GuiWindow):
#     def __init__(self, title, x, y, w, h):
#         super(TerrainGui, self).__init__(ix.application.get_event_window(), x, y, w, h)
#         self.set_title(title)
#         self.panel = ix.api.GuiPanel(self, 0, 0, self.get_width(), self.get_height())
#         self.panel.set_constraints(ix.api.GuiWidget.CONSTRAINT_LEFT, ix.api.GuiWidget.CONSTRAINT_TOP,
#                                    ix.api.GuiWidget.CONSTRAINT_RIGHT, ix.api.GuiWidget.CONSTRAINT_BOTTOM)
#         self.check_box = ix.api.GuiCheckbox(self.panel, 140, 130, "test")
#         self.check_box.set_value(True)
#         self.connect(self.check_box, "EVT_ID_CHECKBOX_CLICK", self.on_event)
#
#     def on_event(self, sender, evtid):
#         print("event received", sender, evtid)
#
# window = TerrainGui("Heightmap wizard", 900, 450, 400, 640)
# window.show()
# while window.is_shown():
#     ix.application.check_for_events()
# window.destroy()


class IdentifiedPushButton(ix.api.GuiPushButton):
    def __init__(self, identifier, parent, *args, **kwargs):
        super(IdentifiedPushButton, self).__init__(*args, **kwargs)
        self.connect(self, 'EVT_ID_PUSH_BUTTON_CLICK',
                     self.on_click)
        self.identifier = identifier
        self.parent = parent

    def on_click(self, sender, evtid):
        self.parent.button_click(self, evtid)


class PreferencesGui(ix.api.GuiWindow):
    def __init__(self, title, x, y, w, h):
        super(PreferencesGui, self).__init__(ix.application.get_event_window(), x, y, w, h)
        self.preferences = preferences_list()

        vertical_spacing = 26
        self.labels = []
        self.input_fields = []
        self.set_buttons = []
        self.clear_buttons = []
        self.set_title(title)
        self.panel = ix.api.GuiPanel(self, 0, 0, self.get_width(), self.get_height())
        self.panel.set_constraints(ix.api.GuiWidget.CONSTRAINT_LEFT, ix.api.GuiWidget.CONSTRAINT_TOP,
                                   ix.api.GuiWidget.CONSTRAINT_RIGHT, ix.api.GuiWidget.CONSTRAINT_BOTTOM)

        # Form generation
        ui_id = 1
        pref_id = 0
        for pref_id in range(len(self.preferences)):
            key = self.preferences[pref_id]['key']
            self.labels.append(ix.api.GuiLabel(self.panel, 10, vertical_spacing * ui_id + 4, 400, 22,
                                          self.preferences[pref_id]['description']))
            ui_id += 1
            if self.preferences[pref_id]['kind'] == bool:
                input_field = ix.api.GuiCheckbox(self.panel, 10, vertical_spacing * ui_id, "")
                input_field.set_value(get_preference(key, self.preferences[pref_id].get('default', False)))
                self.connect(input_field, 'EVT_ID_CHECKBOX_CLICK', self.enable_apply_buttons)
            else:
                input_field = ix.api.GuiLineEdit(self.panel, 10, vertical_spacing * ui_id, 340, 22)
                input_field.set_text(get_preference(key, self.preferences[pref_id].get('default', '')))
                self.connect(input_field, 'EVT_ID_LINE_EDIT_VALUE_EDITED', self.enable_apply_buttons)
            self.input_fields.append(input_field)
            if self.preferences[pref_id]['kind'] in ['ShadingLayer', 'OfContext']:
                self.set_buttons.append(IdentifiedPushButton('set_{id}'.format(id=pref_id), self, self.panel, 360,
                                                 vertical_spacing * ui_id, 100, 22, "Set to selected"))
            self.clear_buttons.append(IdentifiedPushButton('clear_{id}'.format(id=pref_id), self, self.panel, 470,
                                               vertical_spacing * ui_id, 60, 22, "Default"))
            ui_id += 1
        ui_id += 3
        self.ok_button = ix.api.GuiPushButton(self.panel, 220, vertical_spacing * ui_id, 95, 22, "OK")
        self.connect(self.ok_button, 'EVT_ID_PUSH_BUTTON_CLICK', self.ok)
        self.ok_button.disable()
        self.cancel_button = ix.api.GuiPushButton(self.panel, 320, vertical_spacing * ui_id, 95, 22, "Cancel")
        self.connect(self.cancel_button, 'EVT_ID_PUSH_BUTTON_CLICK', self.cancel)
        self.apply_button = ix.api.GuiPushButton(self.panel, 420, vertical_spacing * ui_id, 95, 22, "Apply")
        self.connect(self.apply_button, 'EVT_ID_PUSH_BUTTON_CLICK', self.apply)
        self.apply_button.disable()

    def ok(self, sender, evtid):
        self.apply(sender, evtid)
        sender.get_window().hide()

    def apply(self, sender, evtid):
        for pref_id in range(len(self.preferences)):
            key = self.preferences[pref_id]['key']
            if isinstance(self.input_fields[pref_id], ix.api.GuiCheckbox):
                value = self.input_fields[pref_id].get_value()
            elif isinstance(self.input_fields[pref_id], ix.api.GuiLineEdit):
                value = self.input_fields[pref_id].get_text()
            else:
                value = None
            set_preference(key, value)
        self.ok_button.disable()
        self.apply_button.disable()

    def cancel(self, sender, evtid):
        sender.get_window().hide()

    def enable_apply_buttons(self, sender, evtid):
        self.ok_button.enable()
        self.apply_button.enable()

    def set_preference(self, sender, evtid, id):
        if check_selection(ix.selection, (self.preferences[id]['kind'],)):
            self.input_fields[id].set_text(str(ix.selection[0]))
        self.enable_apply_buttons(sender, evtid)

    def clear_preference(self, sender, evtid, id):
        if isinstance(self.input_fields[id], ix.api.GuiCheckbox):
            self.input_fields[id].set_value(self.preferences[id].get('default', False))
        elif isinstance(self.input_fields[id], ix.api.GuiLineEdit):
            self.input_fields[id].set_text(self.preferences[id].get('default', ''))
        self.ok_button.enable()
        self.apply_button.enable()

    def button_click(self, sender, evtid):
        if 'set_' in sender.identifier:
            id = int(sender.identifier.replace('set_', ''))
            self.set_preference(sender, evtid, id)
        if 'clear' in sender.identifier:
            id = int(sender.identifier.replace('clear_', ''))
            self.clear_preference(sender, evtid, id)


def set_preference(key, value, **kwargs):
    ix = get_ix(kwargs.get("ix"))
    preferences = ix.application.get_prefs(ix.api.AppPreferences.MODE_APPLICATION)
    if isinstance(value, str):
        if preferences.item_exists("clarisse_survival_kit", key):
            preferences.set_string_value("clarisse_survival_kit", key, value)
        else:
            preferences.add_string("clarisse_survival_kit", key, value)
    if isinstance(value, bool):
        if preferences.item_exists("clarisse_survival_kit", key):
            preferences.set_bool_value("clarisse_survival_kit", key, value)
        else:
            preferences.add_bool("clarisse_survival_kit", key, value)


def get_preference(key, default=None, **kwargs):
    ix = get_ix(kwargs.get("ix"))
    preferences = ix.application.get_prefs(ix.api.AppPreferences.MODE_APPLICATION)
    if preferences.item_exists("clarisse_survival_kit", key):
        if preferences.get_item_value_type("clarisse_survival_kit", key) == 0:
            return preferences.get_bool_value("clarisse_survival_kit", key)
        elif preferences.get_item_value_type("clarisse_survival_kit", key) == 3:
            value = preferences.get_string_value("clarisse_survival_kit", key)
            if value:
                return value
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
    window = PreferencesGui('Clarisse Survival Kit Preferences', 900, 450, 540, (len(preferences_list()) + 4) * 44 + 10)
    window.show()
    while window.is_shown():
        ix.application.check_for_events()
    window.destroy()
