#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
英文翻译表汇总。

按模块拆分为多个文件，避免并行维护时互相冲突：
- factory.py     -> src/gui/factory_calibration_tool.py
- ft_debugger.py -> src/gui/ft_debugger.py

每个文件定义 ``TRANSLATIONS`` 字典：key 为代码中的中文原文，value 为英文译文。
"""

from src.i18n_translations.factory import TRANSLATIONS as _FACTORY
from src.i18n_translations.ft_debugger import TRANSLATIONS as _FT_DEBUGGER

TRANSLATIONS = {}
for _dict in (_FACTORY, _FT_DEBUGGER):
    TRANSLATIONS.update(_dict)
