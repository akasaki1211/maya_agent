# -*- coding: utf-8 -*-
from pathlib import Path

def run(vectorstore_path:Path):
    try:
        import os
        os.environ['OPENAI_API_KEY']
    except KeyError:
        from maya import cmds
        cmds.error(u'環境変数 OPENAI_API_KEY が設定されていません。')
    else:
        from .ui import show_ui
        show_ui(vectorstore_path)