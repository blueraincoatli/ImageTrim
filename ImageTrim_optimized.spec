# -*- mode: python ; coding: utf-8 -*-
"""
优化的PyInstaller规格文件 - 大幅减小文件体积
针对ImageTrim项目的特殊优化
"""

import sys
import os
from pathlib import Path

# 跨平台路径处理
main_script = "app/main.py"
resources_path = "app/resources"

# 动态排除列表 - 针对大体积库
excludes = [
    # 完整排除matplotlib及其所有组件（最大体积节省）
    'matplotlib', 'mpl_toolkits', 'pylab', 'matplotlib.pyplot',
    'matplotlib.backends', 'matplotlib.patches', 'matplotlib.collections',
    'matplotlib.path', 'matplotlib.cm', 'matplotlib.colors', 'matplotlib.figure',
    'matplotlib.axes', 'matplotlib.ticker', 'matplotlib.font_manager',
    'matplotlib.text', 'matplotlib.lines', 'matplotlib.patches',
    'matplotlib.collections', 'matplotlib.image', 'matplotlib.colorbar',
    'matplotlib.legend', 'matplotlib.scale', 'matplotlib.transforms',
    'matplotlib.projections', 'matplotlib.spines', 'matplotlib.ticker',
    'matplotlib.offsetbox', 'matplotlib.table', 'matplotlib.sankey',
    'matplotlib.rcsetup', 'matplotlib.animation', 'matplotlib.dates',
    'matplotlib.finance', 'matplotlib.mlab', 'matplotlib.type1font',
    'matplotlib.afm', 'matplotlib.cbook', 'matplotlib.cbook_deprecated',
    'matplotlib.compat', 'matplotlib.tight_bbox', 'matplotlib.testing',
    'matplotlib.tri', 'matplotlib.widgets', 'matplotlib.artist',
    'matplotlib.docstring', 'matplotlib.fontconfig_pattern', 'matplotlib.ft2font',
    'matplotlib.hatch', 'matplotlib.layout_engine', 'matplotlib.legend_handler',
    'matplotlib.lines', 'matplotlib.markers', 'matplotlib.path',
    'matplotlib.patches', 'matplotlib.quiver', 'matplotlib.rcsetup',
    'matplotlib.scale', 'matplotlib.sphinxext', 'matplotlib.stackplot',
    'matplotlib.streamplot', 'matplotlib.table', 'matplotlib.texmanager',
    'matplotlib.text', 'matplotlib.textpath', 'matplotlib.ticker',
    'matplotlib.transforms', 'matplotlib.tri', 'matplotlib.type1font',
    'matplotlib.units', 'matplotlib.verbose', 'matplotlib.widgets',

    # 完整排除scipy（第二大体积节省）
    'scipy', 'scipy.constants', 'scipy.fft', 'scipy.integrate', 'scipy.interpolate',
    'scipy.io', 'scipy.linalg', 'scipy.misc', 'scipy.ndimage', 'scipy.odr',
    'scipy.optimize', 'scipy.signal', 'scipy.sparse', 'scipy.spatial', 'scipy.special',
    'scipy.stats', 'scipy.cluster', 'scipy.stats', 'scipy.version', 'scipy.weave',
    'scipy.__config__', 'scipy._lib', 'scipy._build_utils', 'scipy._distributor_init',
    'scipy._test_frees', 'scipy._test_warnings', 'scipy.conftest', 'scipy.tests',

    # 排除pandas相关
    'pandas', 'pandas._config', 'pandas._libs', 'pandas._testing', 'pandas.api',
    'pandas.compat', 'pandas.core', 'pandas.errors', 'pandas.io', 'pandas.plotting',
    'pandas.util', 'pandas.tests', 'pandas.tseries', 'pandas.util',

    # 排除Jupyter/IPython生态
    'IPython', 'ipykernel', 'ipython_genutils', 'jupyter', 'jupyter_client',
    'jupyter_core', 'jupyter_server', 'notebook', 'nbformat', 'nbconvert',
    'ipywidgets', 'ipython_genutils', 'traitlets', 'jinja2', 'markupsafe',

    # 排除开发工具
    'pytest', 'unittest', 'doctest', 'pdb', 'cProfile', 'profile', 'pstats',
    'setuptools', 'wheel', 'pip', 'pkg_resources', 'distutils', 'ensurepip',
    'debugpy', 'jedi', 'parso', 'pylint', 'flake8', 'black', 'isort', 'autopep8',
    'sphinx', 'docutils', 'nose', 'coverage', 'mock', 'hypothesis',

    # 排除numpy测试和不需要的组件
    'numpy.testing', 'numpy.f2py', 'numpy.distutils', 'numpy.compat',
    'numpy.conftest', 'numpy._pytesttester', 'numpy.char', 'numpy.ctypeslib',
    'numpy.emath', 'numpy.rec', 'numpy.polynomial', 'numpy.random._pickle',
    'numpy.random._common', 'numpy.random._generator', 'numpy.random._philox',
    'numpy.random._pcg64', 'numpy.random._sfc64', 'numpy.random._mt19937',

    # 排除PyQt6大型组件
    'PyQt6.QtWebEngine', 'PyQt6.QtWebEngineWidgets', 'PyQt6.QtWebEngineCore',
    'PyQt6.QtNetwork', 'PyQt6.QtNetworkAuth', 'PyQt6.QtMultimedia', 'PyQt6.QtMultimediaWidgets',
    'PyQt6.QtOpenGL', 'PyQt6.QtOpenGLWidgets', 'PyQt6.QtQuick', 'PyQt6.QtQuickWidgets',
    'PyQt6.QtQml', 'PyQt6.Qt3DCore', 'PyQt6.Qt3DRender', 'PyQt6.Qt3DInput',
    'PyQt6.Qt3DLogic', 'PyQt6.Qt3DExtras', 'PyQt6.QtCharts', 'PyQt6.QtDataVisualization',
    'PyQt6.QtBluetooth', 'PyQt6.QtPositioning', 'PyQt6.QtSensors', 'PyQt6.QtSerialPort',
    'PyQt6.QtWebSockets', 'PyQt6.QtNfc', 'PyQt6.QtRemoteObjects', 'PyQt6.QtGamepad',
    'PyQt6.QtLocation', 'PyQt6.QtPrintSupport', 'PyQt6.QtPurchasing', 'PyQt6.QtScxml',
    'PyQt6.QtSpeech', 'PyQt6.QtSvg', 'PyQt6.QtTest', 'PyQt6.QtDesigner',
    'PyQt6.QtHelp', 'PyQt6.QtSql', 'PyQt6.QtXml', 'PyQt6.QtXmlPatterns',
    'PyQt6.QtUiTools', 'PyQt6.QtAxContainer', 'PyQt6.QtWinExtras', 'PyQt6.QtMacExtras',
    'PyQt6.QtX11Extras', 'PyQt6.QtAndroidExtras', 'PyQt6.QtQuick3D', 'PyQt6.QtQuick3DRuntimeRender',
    'PyQt6.QtQuick3DUtils', 'PyQt6.QtQuickTimeline', 'PyQt6.QtShaderTools',
    'PyQt6.QtVirtualKeyboard', 'PyQt6.QtLabsCalendar', 'PyQt6.QtLabsFolderListModel',
    'PyQt6.QtLabsPlatform', 'PyQt6.QtLabsSettings', 'PyQt6.QtLabsWavefrontMesh',

    # 排除tkinter（虽然不使用但可能被导入）
    'tkinter', 'tk', 'tcl', 'turtle', 'curses',

    # 排除网络和数据库相关
    'urllib', 'http', 'ftplib', 'smtplib', 'poplib', 'imaplib',
    'sqlite3', 'sqlite3.dbapi2', 'bsddb', 'gdbm', 'dbm',

    # 排除不需要的标准库模块
    'email', 'mailcap', 'mailbox', 'mimetypes', 'xmlrpc', 'xml.dom', 'xml.sax',
    'distutils', 'setuptools', 'pkg_resources', 'importlib_metadata',
    'concurrent.futures', 'asyncio', 'asyncore', 'asynchat', 'socket', 'socketserver',
    'ssl', 'hashlib', 'hmac', 'secrets', 'cryptography', 'OpenSSL',

    # 排除机器学习和数据科学库
    'sklearn', 'tensorflow', 'torch', 'keras', 'h5py', 'tables', 'numba',
    'sympy', 'statsmodels', 'cv2', 'skimage', 'dask', 'xarray',

    # 排除不需要的PIL功能
    'PIL.BlpImagePlugin', 'PIL.BufrStubImagePlugin', 'PIL.CurImagePlugin',
    'PIL.DcxImagePlugin', 'PIL.EpsImagePlugin', 'PIL.FitsStubImagePlugin',
    'PIL.FliImagePlugin', 'PIL.FpxImagePlugin', 'PIL.FtexImagePlugin',
    'PIL.GbrImagePlugin', 'PIL.GifImagePlugin', 'PIL.GribStubImagePlugin',
    'PIL.Hdf5StubImagePlugin', 'PIL.IcnsImagePlugin', 'PIL.IcoImagePlugin',
    'PIL.ImImagePlugin', 'PIL.ImtImagePlugin', 'PIL.IptcImagePlugin',
    'PIL.Jpeg2KImagePlugin', 'PIL.JpegImagePlugin', 'PIL.McIdasImagePlugin',
    'PIL.MicImagePlugin', 'PIL.MpegImagePlugin', 'PIL.MpoImagePlugin',
    'PIL.MspImagePlugin', 'PIL.PaletteImagePlugin', 'PIL.PalmImagePlugin',
    'PIL.PcdImagePlugin', 'PIL.PcxImagePlugin', 'PIL.PdfImagePlugin',
    'PIL.PixarImagePlugin', 'PIL.PngImagePlugin', 'PIL.PpmImagePlugin',
    'PIL.PsdImagePlugin', 'PIL.QoiImagePlugin', 'PIL.SgiImagePlugin',
    'PIL.SpiderImagePlugin', 'PIL.SunImagePlugin', 'PIL.TgaImagePlugin',
    'PIL.TiffImagePlugin', 'PIL.WmfImagePlugin', 'PIL.XbmImagePlugin',
    'PIL.XpmImagePlugin', 'PIL.XVThumbImagePlugin', 'PIL.WebPImagePlugin',

    # 排除测试相关
    'test', 'tests', 'testing', 'unittest', 'doctest', 'pytest',
    'nose', 'nose2', 'unittest2', 'testtools', 'fixtures',
]

# 只保留需要的隐式导入
hiddenimports = [
    # PyQt6核心组件（只保留需要的）
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',

    # PIL图像处理（只保留核心功能）
    'PIL.Image',
    'PIL.ImageQt',
    'PIL.ImageFilter',
    'PIL.ImageEnhance',
    'PIL.ImageDraw',
    'PIL.ImageFont',
    'PIL.ImageOps',
    'PIL.ImageMath',
    'PIL._imaging',  # 核心C扩展
    'PIL._imagingft',  # 字体支持
    'PIL._imagingmorph',  # 形态学操作

    # 图像哈希
    'imagehash',
    'imagehash._phash',
    'imagehash._average_hash',
    'imagehash._dhash',
    'imagehash._whash',

    # 数值计算（最小化）
    'numpy.core._multiarray_umath',
    'numpy.core.multiarray',
    'numpy.core.umath',
    'numpy.linalg.lapack_lite',
    'numpy.fft._pocketfft',
    'numpy.random._common',
    'numpy.random._generator',
    'numpy.random.mtrand',

    # 网络请求（如果需要）
    'requests',
    'urllib3',
    'certifi',

    # 如果需要scipy的部分功能，只包含特定模块
    # 'scipy.special._cdflib',  # 只如果确实需要特殊函数
    # 'scipy.spatial.distance',  # 只如果需要距离计算
]

# 分析配置 - 使用优化参数
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
    optimize=2,  # 最高优化级别
)

# 优化PYZ - 使用最高压缩级别
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# 跨平台图标配置 - 仅在文件存在时使用
icon_config = None

# 检查不同平台的图标文件
icon_files = []
if sys.platform == "win32":
    icon_files = ["app/resources/icons/imagetrim.ico"]
elif sys.platform == "darwin":
    icon_files = ["app/resources/icons/imagetrim.icns", "app/resources/icons/imagetrim.ico"]
else:  # Linux
    icon_files = ["app/resources/icons/imagetrim.png", "app/resources/icons/imagetrim.ico"]

# 查找第一个存在的图标文件
for icon_path in icon_files:
    if os.path.exists(icon_path):
        icon_config = icon_path
        break
else:
    icon_config = None

# 可执行文件配置 - 优化版本
exe_kwargs = {
    'pyz': pyz,
    'a.scripts': a.scripts,
    'a.binaries': a.binaries,
    'a.zipfiles': a.zipfiles,
    'a.datas': a.datas,
    'exclude_binaries': False,
    'name': 'ImageTrim' if sys.platform != "win32" else 'ImageTrim.exe',
    'debug': False,  # 关闭调试模式
    'bootloader_ignore_signals': False,
    'strip': False,  # Windows不启用strip避免DLL问题
    'upx': False,   # Windows暂时不启用UPX避免DLL加载问题
    'upx_exclude': [],
    'runtime_tmpdir': None,
    'console': False,  # 无控制台窗口
    'disable_windowed_traceback': False,
    'argv_emulation': False,
    'target_arch': None,
    'codesign_identity': None,
    'entitlements_file': None,
}

# Windows特殊配置
if sys.platform == "win32":
    exe_kwargs.update({
        'strip': False,  # Windows不使用strip
        'upx': False,    # Windows不使用UPX压缩
        'exclude_binaries': False,
        # 确保包含必要的PyQt6 DLL
        'runtime_hooks': [],
    })

# 添加图标（如果有）
if icon_config:
    exe_kwargs['icon'] = icon_config

exe = EXE(**exe_kwargs)

# macOS应用包配置（仅在macOS上创建）
if sys.platform == "darwin":
    app = BUNDLE(
        exe,
        name='ImageTrim.app',
        icon=icon_config if icon_config else None,
        bundle_identifier='com.imagetrim.imagetrim',
        info_plist={
            'CFBundleName': 'ImageTrim',
            'CFBundleDisplayName': 'ImageTrim',
            'CFBundleVersion': '1.1.5',
            'CFBundleShortVersionString': '1.1.5',
            'CFBundleIdentifier': 'com.imagetrim.imagetrim',
            'NSHighResolutionCapable': True,
            'NSSupportsAutomaticGraphicsSwitching': True,
            'LSMinimumSystemVersion': '10.14',
            'CFBundleDocumentTypes': [
                {
                    'CFBundleTypeExtensions': ['jpg', 'jpeg', 'png', 'webp', 'avif'],
                    'CFBundleTypeName': 'Image File',
                    'CFBundleTypeRole': 'Viewer',
                    'LSHandlerRank': 'Alternate'
                }
            ]
        }
    )