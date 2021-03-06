# Conventions In Source Code

## Naming Conventions

### Base Classes

- Base classes start with `Clid`, except for `__main__.ClidApp`; Eg: `ClidMultiLine`.

### Forms

- Forms end with `View`; Eg: `MainView`
- Forms will have `prefdb` and `mp3db` attributes, refering to `prefdb` and `mp3db` attributes of
  `__main__.ClidApp`.
- Traditional Forms will also have a `maindb` attribute, refering to the database it will be mostly interacting
with; Eg: `maindb` attribute of `PreferencesView` will refer to `prefdb`

### Widgets

- Widgets start with first name of parent form; Eg: `MainActionController` is a child widget of parent form `MainView`.
- If the same widget is used by more than one form, above convention fails.

### Handlers

Handlers are executed when a keypress matches a keybinding.

- Handlers start with `h_`; Eg: `h_cursor_up`.
- `char` parameter of a handler is generally not used.
