# Author: Victor Hugo Garcia de Oliveira
# Date: 2025-12-29
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Este arquivo de código-fonte está sujeito aos termos da Mozilla Public
# License, v. 2.0. Se uma cópia da MPL não foi distribuída com este
# arquivo, você pode obter uma em https://mozilla.org/MPL/2.0/.
import pytest
from unittest.mock import MagicMock
from app.ui.views.add_dialog import AddDialog
from app.ui.views.edit_dialog import EditDialog

# Mock ctk to prevent GUI creation issues in headless env
import customtkinter as ctk

# We need to mock the CTkToplevel because it tries to talk to the window manager
# which fails in headless mode even with a dummy display sometimes if not careful.
# But pytest-mock can help. However, CTk inherits from tkinter classes.

def test_add_dialog_instantiation(mocker):
    """Test that AddDialog can be instantiated (conceptually) and logic runs."""
    # We mock the superclass __init__ to avoid TclError
    mocker.patch("customtkinter.CTkToplevel.__init__")

    # Mock methods called in __init__
    mocker.patch("customtkinter.CTkToplevel.title")
    mocker.patch("customtkinter.CTkToplevel.transient")
    mocker.patch("customtkinter.CTkToplevel.lift")
    mocker.patch("customtkinter.CTkToplevel.focus_force")
    mocker.patch("customtkinter.CTkToplevel.grab_set")

    # Mock widgets to avoid TclError during creation
    mocker.patch("customtkinter.CTkLabel")
    mocker.patch("customtkinter.CTkEntry")
    mocker.patch("customtkinter.CTkButton")

    parent = MagicMock()
    fields = {"name": "Name"}

    # Instantiate
    dialog = AddDialog(parent, "Title", fields)

    # Verify our new calls were made
    ctk.CTkToplevel.transient.assert_called_with(parent)
    ctk.CTkToplevel.lift.assert_called()
    ctk.CTkToplevel.focus_force.assert_called()
    ctk.CTkToplevel.grab_set.assert_called()

def test_edit_dialog_instantiation(mocker):
    """Test that EditDialog can be instantiated."""
    mocker.patch("customtkinter.CTkToplevel.__init__")
    mocker.patch("customtkinter.CTkToplevel.title")
    mocker.patch("customtkinter.CTkToplevel.transient")
    mocker.patch("customtkinter.CTkToplevel.lift")
    mocker.patch("customtkinter.CTkToplevel.focus_force")
    mocker.patch("customtkinter.CTkToplevel.grab_set")

    mocker.patch("customtkinter.CTkLabel")
    mocker.patch("customtkinter.CTkEntry")
    mocker.patch("customtkinter.CTkButton")

    parent = MagicMock()
    fields = {"name": "Name"}
    data = {"id": 1, "name": "Old"}
    callback = MagicMock()

    dialog = EditDialog(parent, "Title", fields, data, callback)

    ctk.CTkToplevel.transient.assert_called_with(parent)
    ctk.CTkToplevel.lift.assert_called()
    ctk.CTkToplevel.focus_force.assert_called()
    ctk.CTkToplevel.grab_set.assert_called()
