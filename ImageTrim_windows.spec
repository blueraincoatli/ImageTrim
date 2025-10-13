# -*- mode: python ; coding: utf-8 -*-
"""
Windows专用PyInstaller规格文件 - 保守配置避免DLL问题
"""

import sys
import os

# 项目配置
main_script = "app/main.py"
resources_path = "app/resources"

# Windows特定的排除列表 - 更保守的配置
excludes = [
    # 完全排除大型科学计算库
    'matplotlib', 'mpl_toolkits', 'pylab', 'matplotlib.pyplot',
    'matplotlib.backends', 'matplotlib.patches', 'matplotlib.collections',
    'scipy', 'scipy.constants', 'scipy.fft', 'scipy.integrate',
    'scipy.interpolate', 'scipy.io', 'scipy.linalg', 'scipy.misc',
    'scipy.ndimage', 'scipy.odr', 'scipy.optimize', 'scipy.signal',
    'scipy.sparse', 'scipy.spatial', 'scipy.special', 'scipy.stats',
    'pandas', 'pandas._config', 'pandas._libs', 'pandas.api',
    'pandas.compat', 'pandas.core', 'pandas.errors', 'pandas.io',
    'pandas.plotting', 'pandas.util', 'pandas.tests', 'pandas.tseries',

    # 排除Jupyter/IPython生态
    'IPython', 'ipykernel', 'ipython_genutils', 'jupyter',
    'jupyter_client', 'jupyter_core', 'jupyter_server',
    'notebook', 'nbformat', 'nbconvert', 'ipywidgets',

    # 排除开发工具
    'pytest', 'unittest', 'doctest', 'pdb', 'cProfile',
    'setuptools', 'wheel', 'pip', 'pkg_resources', 'distutils',
    'debugpy', 'jedi', 'parso', 'pylint', 'flake8', 'black',
    'sphinx', 'docutils', 'nose', 'coverage', 'mock',

    # 排除numpy测试组件
    'numpy.testing', 'numpy.f2py', 'numpy.distutils', 'numpy.compat',
    'numpy.conftest', 'numpy._pytesttester', 'numpy.char', 'numpy.ctypeslib',

    # 排除PyQt6大型组件（保留核心功能）
    'PyQt6.QtWebEngine', 'PyQt6.QtWebEngineWidgets', 'PyQt6.QtWebEngineCore',
    'PyQt6.QtNetwork', 'PyQt6.QtNetworkAuth', 'PyQt6.QtMultimedia',
    'PyQt6.QtMultimediaWidgets',
    'PyQt6.QtOpenGL', 'PyQt6.QtOpenGLWidgets', 'PyQt6.QtQuick',
    'PyQt6.QtQuickWidgets', 'PyQt6.QtQml',
    'PyQt6.Qt3DCore', 'PyQt6.Qt3DRender', 'PyQt6.Qt3DInput',
    'PyQt6.Qt3DLogic', 'PyQt6.Qt3DExtras', 'PyQt6.QtCharts',
    'PyQt6.QtDataVisualization', 'PyQt6.QtBluetooth', 'PyQt6.QtPositioning',
    'PyQt6.QtSensors', 'PyQt6.QtSerialPort', 'PyQt6.QtWebSockets',
    'PyQt6.QtNfc', 'PyQt6.QtRemoteObjects', 'PyQt6.QtGamepad',
    'PyQt6.QtLocation', 'PyQt6.QtPrintSupport', 'PyQt6.QtPurchasing',
    'PyQt6.QtScxml', 'PyQt6.QtSpeech', 'PyQt6.QtSvg', 'PyQt6.QtTest',
    'PyQt6.QtDesigner', 'PyQt6.QtHelp', 'PyQt6.QtSql', 'PyQt6.QtXml',
    'PyQt6.QtXmlPatterns', 'PyQt6.QtUiTools', 'PyQt6.QtAxContainer',
    'PyQt6.QtWinExtras', 'PyQt6.QtMacExtras', 'PyQt6.QtX11Extras',
    'PyQt6.QtAndroidExtras', 'PyQt6.QtQuick3D', 'PyQt6.QtQuick3DRuntimeRender',
    'PyQt6.QtQuick3DUtils', 'PyQt6.QtQuickTimeline', 'PyQt6.QtShaderTools',
    'PyQt6.QtVirtualKeyboard', 'PyQt6.QtLabsCalendar', 'PyQt6.QtLabsFolderListModel',
    'PyQt6.QtLabsPlatform', 'PyQt6.QtLabsSettings', 'PyQt6.QtLabsWavefrontMesh',

    # 排除tkinter（虽然不使用但可能被导入）
    'tkinter', 'tk', 'tcl', 'turtle', 'curses',

    # 排除机器学习库
    'sklearn', 'tensorflow', 'torch', 'keras', 'h5py', 'tables', 'numba',
    'sympy', 'statsmodels', 'cv2', 'skimage', 'dask', 'xarray',
]

# 精确的隐式导入 - 只包含必要的模块
hiddenimports = [
    # PyQt6核心组件
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',

    # 确保包含必要的PyQt6组件
    'PyQt6.QtCore.QCoreApplication',
    'PyQt6.QtGui.QGuiApplication',
    'PyQt6.QtWidgets.QApplication',
    'PyQt6.QtCore.Qt',
    'PyQt6.QtCore.QObject',
    'PyQt6.QtCore.QTimer',

    # PIL图像处理核心功能
    'PIL.Image',
    'PIL.ImageQt',
    'PIL.ImageFilter',
    'PIL.ImageEnhance',
    'PIL.ImageOps',
    'PIL.ImageMath',
    'PIL._imaging',  # 核心C扩展
    'PIL._imagingft',  # 字体支持

    # 图像哈希
    'imagehash',
    'imagehash._phash',
    'imagehash._average_hash',
    'imagehash._dhash',
    'imagehash._whash',

    # 数值计算核心
    'numpy.core._multiarray_umath',
    'numpy.core.multiarray',
    'numpy.core.umath',
    'numpy.linalg.lapack_lite',
    'numpy.random.mtrand',

    # 网络请求
    'requests',
    'urllib3',
    'certifi',
    'charset_normalizer',
    'idna',
]

# 分析配置
a = Analysis(
    [main_script],
    pathex=[],
    binaries=[],
    datas=[(resources_path, "resources") if os.path.exists(resources_path) else []],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
    optimize=0,  # 保守的优化级别
)

# Windows特定优化：确保DLL正确加载
if sys.platform == "win32":
    # 确保包含所有必要的DLL
    from PyInstaller.utils.hooks import collect_data_files
    from PyInstaller.utils.hooks import collect_dynamic_libs

    # 收集PyQt6的DLL
    qt_libs = collect_dynamic_libs('PyQt6')
    a.binaries.extend(qt_libs)

    # 收集PIL的DLL
    pil_libs = collect_dynamic_libs('PIL')
    a.binaries.extend(pil_libs)

# PYZ压缩
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# 图标配置
icon_path = None
if os.path.exists("app/resources/icons/imagetrim.ico"):
    icon_path = "app/resources/icons/imagetrim.ico"

# 可执行文件配置 - Windows保守版本
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ImageTrim.exe',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,  # Windows不使用strip避免DLL问题
    upx=False,    # Windows不使用UPX压缩避免DLL加载问题
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_path,
)