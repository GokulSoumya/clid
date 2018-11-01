"""
clid.gui.widgets
~~~~~~~~~~~~~~~~

Custom widgets made using `prompt_toolkit`.
"""

from collections import OrderedDict

from prompt_toolkit.application import get_app
from prompt_toolkit.filters import Condition
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.bindings.focus import (
    focus_next as focus_next_widget,
    focus_previous as focus_previous_widget,
)
from prompt_toolkit.layout import ScrollOffsets
from prompt_toolkit.layout.containers import (
    HSplit,
    VSplit,
    Window,
    ConditionalContainer,
)
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.margins import NumberedMargin, ScrollbarMargin
from prompt_toolkit.layout.processors import BeforeInput
from prompt_toolkit.layout.screen import Point
from prompt_toolkit.widgets import Label, TextArea


class ItemList:
    """
    A widget for showing a list of items, complete with a scroll bar,
    line numbers and navigation keybindings.
    Attributes:
        items (list of str): List of items to show.
        cursor (prompt_toolkit.layout.screen.Point):
            Represents the cursor position in terms of lines and columns.
        _disp_items (list of tuples):
            `items` converted into a form `prompt_toolkit` can recognize and
            display properly.
        self.control: `prompt_toolkit` control that actually displays the data.
        self.window (prompt_toolkit.layout.Window):
            A `Window` displays a control, and is responsible for line wrapping,
            scrolling, etc.
    """

    def __init__(self, items):
        # fmt: off

        self.control = FormattedTextControl(
            text=None,  # handled by set_items method
            get_cursor_position=lambda: self.cursor,
            key_bindings=self._get_key_bindings(),
            focusable=True,
        )

        self.set_items(items)

        self.window = Window(
            content=self.control,
            # ignore_content_height=True,
            wrap_lines=False,
            cursorline=True,
            always_hide_cursor=True,
            right_margins=[ScrollbarMargin()],
            left_margins=[NumberedMargin()],
            scroll_offsets=ScrollOffsets(top=2, bottom=2),
        )

        # fmt: on

    def set_items(self, items):
        self.items = items
        self.cursor = Point(0, 0)
        self._disp_items = [("", i + "\n") for i in items]
        self.control.text = self._disp_items

    def move_cursor_up(self, lines_to_move=1):
        # Move the cursor up by `lines_to_move` lines.
        y = self.cursor.y
        y = y - lines_to_move if y > 0 else 0
        self.cursor = Point(0, y)

    def move_cursor_down(self, lines_to_move=1):
        total_lines = len(self.items)
        y = self.cursor.y
        y = y + lines_to_move if y + lines_to_move < total_lines else y
        self.cursor = Point(0, y)

    def move_cursor_to_beginning(self):
        self.cursor = Point(0, 0)

    def move_cursor_to_end(self):
        y = len(self.items) - 1
        self.cursor = Point(0, y)

    def move_cursor_page_up(self):
        visible_lines = len(self.window.render_info.displayed_lines)
        # NOTE: we subtract 3 from visible_lines to compensate for scroll offsets
        #       so that the line from where page up was pressed is still visible
        #       at the bottom
        self.move_cursor_up(lines_to_move=visible_lines - 3)

    def move_cursor_page_down(self):
        visible_lines = len(self.window.render_info.displayed_lines)
        self.move_cursor_down(lines_to_move=visible_lines - 3)

    def _get_key_bindings(self):
        keybindings = KeyBindings()

        keybindings.add("up")(lambda event: self.move_cursor_up())
        keybindings.add("k")(lambda event: self.move_cursor_up())
        keybindings.add("down")(lambda event: self.move_cursor_down())
        keybindings.add("j")(lambda event: self.move_cursor_down())
        keybindings.add("home")(lambda event: self.move_cursor_to_beginning())
        keybindings.add("end")(lambda event: self.move_cursor_to_end())
        keybindings.add("pageup")(lambda event: self.move_cursor_page_up())
        keybindings.add("pagedown")(lambda event: self.move_cursor_page_down())

        return keybindings

    def __pt_container__(self):
        return self.window


class SearchToolbar:
    """
    Toolbar for searching the contents of another widget, like an `ItemList`.
    The widget is hidden by default. To focus the widget and start searching,
    set the `is_searching` attribute to True.
    Attributes:
        text (str): Current text in the search field.
        is_searching (bool): Whether the user is searching for text.
    """

    def __init__(self, handler, return_focus_to):
        """
        Args:
            handler:
                Function to be called when user presses `Enter`. It should
                accept one parameter, the search text.
            return_focus_to:
                A `prompt_toolkit` Window or widget or container that is focused
                after the user has pressed the enter key.
        """
        self._handler = handler
        self._is_searching = False
        self._return_focus_widget = return_focus_to

        def accept_handler(*args):
            if self.text:
                self._handler(self.text)
            self.is_searching = False

        self._search_control = TextArea(
            height=1,
            multiline=False,
            dont_extend_height=True,
            accept_handler=accept_handler,
            input_processors=[BeforeInput(text="/")],
        )

        self.window = ConditionalContainer(
            content=self._search_control, filter=Condition(lambda: self._is_searching)
        )

    @property
    def is_searching(self):
        return self._is_searching

    @is_searching.setter
    def is_searching(self, value):
        self._is_searching = value
        if self._is_searching:
            get_app().layout.focus(self)
        else:
            get_app().layout.focus(self._return_focus_widget)

    @property
    def text(self):
        return self._search_control.text

    def __pt_container__(self):
        return self.window


class LabeledTextArea:
    """
    Widget for accepting input, with an attached label.
    Attributes:
        label (str): Text to be used as label.
        text (str): Initial value of the input field.
    """

    def __init__(self, label="", text=""):
        self.label = label + ": "

        # fmt: off

        self._text_control = TextArea(
            text=text,
            focusable=True,
            multiline=False,
            wrap_lines=False,
        )

        self._label_control = Label(text=self.label, dont_extend_width=True)

        self.container = HSplit(
            [
                VSplit([
                    self._label_control,
                    self._text_control,
                ])
            ],
            height=1,
        )

        # fmt: on

    @property
    def text(self):
        return self._text_control.text

    @text.setter
    def text(self, value):
        self._text_control.text = value

    def __pt_container__(self):
        return self.container


class FieldsEditor:
    """
    A widget for editing multiple fields. All the fields will be represented
    using a `LabeledTextArea`.

    For example, if we use:
    >>> fields = {'field1': 'editable text', 'f2': 'other editable text'}
    >>> FieldsEditor(fields)
    >>> # create other necessary `prompt_toolkit` objects, etc

    then the window will look like:

    +--------------------------------+
    | field1: editable text          |
    | f2: other editable text        |
    |                                |
    +--------------------------------+
    """

    def __init__(self, fields):
        """
        Args:
            fields (dict):
                Fields to be edited. The key should be the name of the field
                (which will be a label) and key should be initial value of the
                field (which will be filled into the text area). Use an
                OrderedDict if order in which the fields are displayed is
                important.
        """
        # Map field name to corresponding edit control
        self._field_controls = OrderedDict(
            {
                field_name: LabeledTextArea(label=field_name, text=value)
                for field_name, value in fields.items()
            }
        )

        # fmt: off

        self.container = HSplit(
            [*self._field_controls.values()],  # child widgets
            key_bindings=self._get_key_bindings(),
        )

        # fmt: on

    def get_fields(self):
        """
        Return an OrderedDict with the field name as key and the current field
        value as values.
        """
        return OrderedDict(
            {
                field_name: field_control.text
                for field_name, field_control in self._field_controls.items()
            }
        )

    def _get_key_bindings(self):
        keybindings = KeyBindings()

        keybindings.add("up")(focus_previous_widget)
        keybindings.add("s-tab")(focus_previous_widget)
        keybindings.add("down")(focus_next_widget)
        keybindings.add("tab")(focus_next_widget)

        return keybindings

    def __pt_container__(self):
        return self.container
