"""Eklentiyi hazirCevap.nvda-addon olarak paketler: python build.py"""
import os
import zipfile

with zipfile.ZipFile("hazirCevap.nvda-addon", "w", zipfile.ZIP_DEFLATED) as z:
	for root, dirs, files in os.walk("addon"):
		dirs[:] = [d for d in dirs if d != "__pycache__"]
		for f in files:
			p = os.path.join(root, f)
			z.write(p, os.path.relpath(p, "addon"))
