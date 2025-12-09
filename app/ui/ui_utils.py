
import customtkinter as ctk

def bind_global_mouse_scroll(widget, command=None, recursive=True):
    """
    Binds mouse wheel events (Linux Button-4/5 and Windows/Mac MouseWheel)
    to a widget and optionally its children.

    :param widget: The widget to bind events to.
    :param command: A callback function(event) to execute. If None, it tries to invoke the widget's yview_scroll if available.
    :param recursive: If True, binds to all current children recursively.
    """

    # Determine the scroll function
    scroll_func = None

    if command:
        scroll_func = command
    else:
        # Try to find a default scroll function
        if isinstance(widget, ctk.CTkScrollableFrame):
            try:
                # Access internal canvas of CTkScrollableFrame (CTk 5.x)
                # Note: Accessing protected member is necessary as it's not exposed publicly
                scroll_func = widget._parent_canvas.yview_scroll
            except AttributeError:
                 pass
        elif hasattr(widget, "yview_scroll"):
            scroll_func = widget.yview_scroll

    if not scroll_func:
        return # Nothing to bind

    # Helper to adapt the arguments (Tkinter scroll needs (delta, "units"))
    def scroll_handler(direction):
        try:
             # Standard Tkinter scroll methods expect (number, "units")
             scroll_func(direction, "units")
        except TypeError:
             # Fallback if the command expects just delta (e.g. custom function)
             scroll_func(direction)

    def apply_binding(w):
        # Linux (Button-4: Up, Button-5: Down)
        # Direction is -1 for UP (scrolling back), 1 for DOWN (scrolling fwd)
        w.bind("<Button-4>", lambda e: scroll_handler(-1), add="+")
        w.bind("<Button-5>", lambda e: scroll_handler(1), add="+")

        # Windows (MouseWheel)
        # Delta is usually 120. Negative delta means down, Positive means up.
        # We want negative delta to map to +1 (scroll down)
        w.bind("<MouseWheel>", lambda e: scroll_handler(int(-1 * (e.delta / 120))), add="+")

    if recursive:
        _bind_recursive(widget, apply_binding)
    else:
        apply_binding(widget)

def _bind_recursive(widget, binding_func):
    """Helper to bind recursively"""
    binding_func(widget)
    for child in widget.winfo_children():
        _bind_recursive(child, binding_func)
