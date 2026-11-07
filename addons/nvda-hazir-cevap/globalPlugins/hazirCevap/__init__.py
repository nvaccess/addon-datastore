# -*- coding: UTF-8 -*-
"""Quick Response: pastes saved texts quickly using shortcut keys."""

import json
import os

import addonHandler
import api
import globalPluginHandler
import gui
import config
import core
import keyboardHandler
import queueHandler
import scriptHandler
import ui
import wx
from gui import guiHelper
from logHandler import log
from scriptHandler import script

addonHandler.initTranslation()

_FILE = "hazirCevap.json"
_CATEGORY = _("Quick Response")


def _path():
	return os.path.join(config.getUserDefaultConfigPath(), _FILE)


class Store:
	"""Stores an unlimited number of {name, text, gesture} entries as JSON."""

	def __init__(self):
		self.entries = []
		self.load()

	def load(self):
		try:
			with open(_path(), "r", encoding="utf-8") as f:
				data = json.load(f)
			self.entries = [
				{
					"name": str(e.get("name", "")),
					"text": str(e.get("text", "")),
					"gesture": str(e.get("gesture", "")),
				}
				for e in data if isinstance(e, dict)
			]
		except FileNotFoundError:
			self.entries = []
		except Exception:
			log.error("Quick Response: entries could not be read", exc_info=True)
			self.entries = []

	def save(self):
		try:
			tmp = _path() + ".tmp"
			with open(tmp, "w", encoding="utf-8") as f:
				json.dump(self.entries, f, ensure_ascii=False, indent=1)
			os.replace(tmp, _path())
		except Exception:
			log.error("Quick Response: entries could not be saved", exc_info=True)
			ui.message(_("Entries could not be saved"))


class EntryDialog(wx.Dialog):
	def __init__(self, parent, entry=None):
		super().__init__(parent, title=_("Quick response"))
		entry = entry or {"name": "", "text": "", "gesture": ""}
		main = wx.BoxSizer(wx.VERTICAL)
		helper = guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		self.name = helper.addLabeledControl(_("&Name:"), wx.TextCtrl, value=entry["name"])
		self.text = helper.addLabeledControl(
			_("&Text:"), wx.TextCtrl, value=entry["text"],
			style=wx.TE_MULTILINE, size=(450, 200),
		)
		self.gesture = helper.addLabeledControl(
			_("&Shortcut (e.g. kb:NVDA+control+1, can be left blank):"),
			wx.TextCtrl, value=entry["gesture"],
		)
		helper.addDialogDismissButtons(self.CreateButtonSizer(wx.OK | wx.CANCEL))
		main.Add(helper.sizer, border=guiHelper.BORDER_FOR_DIALOGS, flag=wx.ALL)
		self.SetSizerAndFit(main)
		self.Bind(wx.EVT_BUTTON, self.onOk, id=wx.ID_OK)
		self.name.SetFocus()

	def onOk(self, evt):
		if not self.text.GetValue().strip():
			gui.messageBox(_("Text cannot be empty."), _("Error"), wx.OK | wx.ICON_ERROR, self)
			self.text.SetFocus()
			return
		evt.Skip()

	def result(self):
		text = self.text.GetValue()
		gesture = self.gesture.GetValue().strip()
		if gesture and not gesture.startswith("kb"):
			gesture = "kb:" + gesture
		name = self.name.GetValue().strip() or text.strip().splitlines()[0][:40]
		return {"name": name, "text": text, "gesture": gesture}


class ManagerDialog(wx.Dialog):
	_instance = None

	def __init__(self, parent, plugin):
		super().__init__(parent, title=_("Quick Response Manager"))
		self.plugin = plugin
		main = wx.BoxSizer(wx.VERTICAL)
		helper = guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		self.list = helper.addLabeledControl(
			_("&Saved responses:"), wx.ListBox, choices=[], size=(450, 250),
		)
		btns = guiHelper.ButtonHelper(wx.HORIZONTAL)
		self.addBtn = btns.addButton(self, label=_("&Add..."))
		self.editBtn = btns.addButton(self, label=_("&Edit..."))
		self.delBtn = btns.addButton(self, label=_("&Delete"))
		self.pasteBtn = btns.addButton(self, label=_("&Paste"))
		helper.addItem(btns.sizer)
		helper.addDialogDismissButtons(self.CreateButtonSizer(wx.CLOSE))
		main.Add(helper.sizer, border=guiHelper.BORDER_FOR_DIALOGS, flag=wx.ALL)
		self.SetSizerAndFit(main)
		self.SetEscapeId(wx.ID_CLOSE)
		self.addBtn.Bind(wx.EVT_BUTTON, self.onAdd)
		self.editBtn.Bind(wx.EVT_BUTTON, self.onEdit)
		self.delBtn.Bind(wx.EVT_BUTTON, self.onDelete)
		self.pasteBtn.Bind(wx.EVT_BUTTON, self.onPaste)
		self.list.Bind(wx.EVT_LISTBOX_DCLICK, self.onEdit)
		self.Bind(wx.EVT_BUTTON, lambda e: self.Close(), id=wx.ID_CLOSE)
		self.Bind(wx.EVT_CLOSE, self.onClose)
		self.refresh()

	def refresh(self, select=0):
		entries = self.plugin.store.entries
		labels = [
			e["name"] + (" (%s)" % e["gesture"][3:] if e["gesture"] else "")
			for e in entries
		]
		self.list.Set(labels)
		if labels:
			self.list.SetSelection(max(0, min(select, len(labels) - 1)))
		for b in (self.editBtn, self.delBtn, self.pasteBtn):
			b.Enable(bool(labels))

	def onAdd(self, evt):
		dlg = EntryDialog(self)
		if dlg.ShowModal() == wx.ID_OK:
			self.plugin.store.entries.append(dlg.result())
			self.plugin.changed()
			self.refresh(len(self.plugin.store.entries) - 1)
		dlg.Destroy()
		self.list.SetFocus()

	def onEdit(self, evt):
		i = self.list.GetSelection()
		if i == wx.NOT_FOUND:
			return
		dlg = EntryDialog(self, self.plugin.store.entries[i])
		if dlg.ShowModal() == wx.ID_OK:
			self.plugin.store.entries[i] = dlg.result()
			self.plugin.changed()
			self.refresh(i)
		dlg.Destroy()
		self.list.SetFocus()

	def onDelete(self, evt):
		i = self.list.GetSelection()
		if i == wx.NOT_FOUND:
			return
		if gui.messageBox(
			_("Delete selected response?"), _("Confirmation"), wx.YES_NO | wx.ICON_QUESTION, self,
		) == wx.YES:
			del self.plugin.store.entries[i]
			self.plugin.changed()
			self.refresh(i)
		self.list.SetFocus()

	def onPaste(self, evt):
		i = self.list.GetSelection()
		if i == wx.NOT_FOUND:
			return
		entry = self.plugin.store.entries[i]
		self.Close()
		wx.CallLater(300, self.plugin.paste, entry)

	def onClose(self, evt):
		ManagerDialog._instance = None
		self.Destroy()


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	scriptCategory = _CATEGORY

	def __init__(self):
		super().__init__()
		self.store = Store()
		self._dynamic = {}
		self._bind()

	def terminate(self):
		if ManagerDialog._instance:
			try:
				ManagerDialog._instance.Destroy()
			except Exception:
				pass
		super().terminate()

	def _bind(self):
		self._dynamic = {}
		for e in self.store.entries:
			g = e["gesture"]
			if g and g.startswith("kb:"):
				self._dynamic[g[3:].lower()] = e

	def changed(self):
		self.store.save()
		self._bind()

	def getScript(self, gesture):
		script_ = super().getScript(gesture)
		if script_ or not self._dynamic:
			return script_
		try:
			ids = [i[3:].lower() for i in gesture.normalizedIdentifiers if i.startswith("kb")]
			ids += [i[3:].lower() for i in gesture.identifiers if i.startswith("kb:")]
		except Exception:
			return None
		for i in ids:
			entry = self._dynamic.get(i)
			if entry:
				return lambda g, e=entry: self.paste(e)
		return None

	def paste(self, entry):
		if not api.copyToClip(entry["text"]):
			ui.message(_("Failed to copy to clipboard"))
			return
		core.callLater(150, self._sendPaste)

	def _sendPaste(self):
		try:
			keyboardHandler.KeyboardInputGesture.fromName("control+v").send()
		except Exception:
			log.error("Quick Response: paste failed", exc_info=True)
			ui.message(_("Failed to paste"))

	@script(
		description=_("Opens the quick response manager"),
		gesture="kb:NVDA+control+shift+h",
		category=_CATEGORY,
	)
	def script_openManager(self, gesture):
		wx.CallAfter(self._openManager)

	def _openManager(self):
		if ManagerDialog._instance:
			ManagerDialog._instance.Raise()
			return
		gui.mainFrame.prePopup()
		d = ManagerDialog(gui.mainFrame, self)
		ManagerDialog._instance = d
		d.Show()
		d.Raise()
		gui.mainFrame.postPopup()

	@script(
		description=_("Selects and pastes from the quick response list"),
		gesture="kb:NVDA+control+shift+l",
		category=_CATEGORY,
	)
	def script_choose(self, gesture):
		if not self.store.entries:
			ui.message(_("No saved quick responses"))
			return
		wx.CallAfter(self._choose)

	def _choose(self):
		gui.mainFrame.prePopup()
		dlg = wx.SingleChoiceDialog(
			gui.mainFrame, _("Select response to paste"), _("Quick Response"),
			[e["name"] for e in self.store.entries],
		)
		ok = dlg.ShowModal() == wx.ID_OK
		sel = dlg.GetSelection()
		dlg.Destroy()
		gui.mainFrame.postPopup()
		if ok:
			wx.CallLater(300, self.paste, self.store.entries[sel])