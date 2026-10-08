# -*- coding: utf-8 -*-
"""mediapipe 中文路径兼容补丁。

mediapipe 0.10.14 的 C++ 资源加载器在 Windows 上无法打开含中文的绝对路径
（如 D:\\Claude工作区\\...），导致：
  1) Hands() 初始化时抛 FileNotFoundError（hand_landmark_tracking_cpu.binarypb）
  2) process() 运行时抛 "Can't find file"（各 .tflite 模型）

修复（三层）：
  A. ValidatedGraphConfig.initialize 前切换到 mediapipe 包根目录，
     将绝对路径转成相对路径传入，绕过 C++ 对 binarypb 的绝对路径查找。
  B. SolutionBase.__init__ 执行完后，把 resource_util 的资源目录覆盖为
     Windows 8.3 短路径（纯 ASCII），使图内 .tflite 资源经 ASCII 路径可读。
"""
import ctypes
import os

import mediapipe as mp
from mediapipe.python._framework_bindings import resource_util
from mediapipe.python._framework_bindings import validated_graph_config as _vgc
from mediapipe.python import solution_base as _solution_base

_PKG_ROOT = os.path.dirname(mp.__file__)

# Windows 8.3 短路径（纯 ASCII），供 C++ 资源加载器使用
_short_root = None
try:
    _buf = ctypes.create_unicode_buffer(260)
    _r = ctypes.windll.kernel32.GetShortPathNameW(
        os.path.dirname(_PKG_ROOT), _buf, 260
    )
    if _r:
        _short_root = _buf.value
except Exception:
    _short_root = None

_orig_init = _vgc.ValidatedGraphConfig.initialize


def _patched_initialize(self, binary_graph_path=None, graph_config=None):
    if binary_graph_path:
        normalized = os.path.normpath(binary_graph_path)
        if os.path.isabs(normalized):
            try:
                rel = os.path.relpath(normalized, _PKG_ROOT)
            except ValueError:
                rel = None
            if rel and not rel.startswith(".."):
                saved = os.getcwd()
                try:
                    os.chdir(_PKG_ROOT)
                    return _orig_init(self, binary_graph_path=rel.replace("\\", "/"))
                except Exception:
                    os.chdir(saved)
                    raise
    return _orig_init(
        self, binary_graph_path=binary_graph_path, graph_config=graph_config
    )


_vgc.ValidatedGraphConfig.initialize = _patched_initialize

if _short_root:
    _orig_sb_init = _solution_base.SolutionBase.__init__

    def _patched_sb_init(self, *args, **kwargs):
        result = _orig_sb_init(self, *args, **kwargs)
        try:
            resource_util.set_resource_dir(_short_root)
        except Exception:
            pass
        return result

    _solution_base.SolutionBase.__init__ = _patched_sb_init
