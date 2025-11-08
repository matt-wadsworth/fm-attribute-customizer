# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all
import os
from pathlib import Path

# Get project root for icon path
project_root = Path(SPECPATH)
icon_path = project_root / 'icon.ico'
if not icon_path.exists():
    icon_path = project_root / 'icon.png'
icon = str(icon_path) if icon_path.exists() else None

# Exclude unused PyQt6 modules to reduce size significantly
# These modules are not used by the application (only QtCore, QtGui, QtWidgets are used)
excluded_qt_modules = [
    'PyQt6.QtWebEngine',
    'PyQt6.QtWebEngineCore',
    'PyQt6.QtWebEngineWidgets',
    'PyQt6.QtBluetooth',
    'PyQt6.QtLocation',
    'PyQt6.QtMultimedia',
    'PyQt6.QtMultimediaWidgets',
    'PyQt6.QtNetwork',
    'PyQt6.QtNfc',
    'PyQt6.QtPositioning',
    'PyQt6.QtQml',
    'PyQt6.QtQuick',
    'PyQt6.QtQuickWidgets',
    'PyQt6.QtSql',
    'PyQt6.QtSvg',
    'PyQt6.QtSvgWidgets',
    'PyQt6.QtTest',
    'PyQt6.QtXml',
    'PyQt6.QtXmlPatterns',
    'PyQt6.QtCharts',
    'PyQt6.QtDataVisualization',
    'PyQt6.Qt3DCore',
    'PyQt6.Qt3DRender',
    'PyQt6.Qt3DInput',
    'PyQt6.Qt3DLogic',
    'PyQt6.Qt3DAnimation',
    'PyQt6.Qt3DExtras',
    'PyQt6.QtDesigner',
    'PyQt6.QtHelp',
    'PyQt6.QtOpenGL',
    'PyQt6.QtOpenGLWidgets',
    'PyQt6.QtPrintSupport',
    'PyQt6.QtSerialPort',
    'PyQt6.QtStateMachine',
    'PyQt6.QtTextToSpeech',
    'PyQt6.QtWebSockets',
    'PyQt6.QtWebChannel',
]

# Collect UnityPy - filter out test/example/doc files
unitypy_datas = []
unitypy_binaries = []
unitypy_hiddenimports = ['UnityPy']

try:
    tmp_ret = collect_all('UnityPy')
    # Filter out test files, examples, and documentation
    for data in tmp_ret[0]:
        if isinstance(data, tuple) and len(data) >= 2:
            dest_path = str(data[1]).lower()
            # Exclude test files, examples, and docs
            if not any(skip in dest_path for skip in ['/test', '/tests', '/example', '/examples', '/doc', '/docs', '.md', 'readme']):
                unitypy_datas.append(data)
        else:
            unitypy_datas.append(data)
    unitypy_binaries = tmp_ret[1]
    unitypy_hiddenimports += tmp_ret[2]
except Exception:
    pass

# Collect PyQt6 - filter out unused modules and unnecessary files
pyqt6_datas = []
pyqt6_binaries = []
pyqt6_hiddenimports = ['PyQt6', 'PyQt6.QtCore', 'PyQt6.QtGui', 'PyQt6.QtWidgets']

try:
    tmp_ret = collect_all('PyQt6')
    # Filter PyQt6 data to exclude unused modules and unnecessary files
    for data in tmp_ret[0]:
        if isinstance(data, tuple) and len(data) >= 2:
            # Check both source and destination paths, normalize separators
            src_path = str(data[0]).lower().replace('\\', '/')
            dest_path = str(data[1]).lower().replace('\\', '/')
            combined_path = src_path + ' ' + dest_path
            # Exclude test files, examples, docs, and unused module plugins/binaries
            skip_patterns = ['/test', '/tests', '/example', '/examples', '/doc', '/docs', '.md', 'readme',
                            'webengine', 'bluetooth', 'location', 'multimedia', 'network', 'qml', 'quick',
                            'sql', 'svg', 'xml', 'charts', '3d', 'designer', 'help', 'opengl', 'print',
                            'serial', 'statemachine', 'texttospeech', 'websockets', 'webchannel',
                            # Exclude plugin directories that depend on excluded modules
                            'plugins/renderers', 'plugins/sceneparsers', 'plugins/webview',
                            'plugins/geometryloaders', 'pyqt6qmlplugin']
            if not any(skip in combined_path for skip in skip_patterns):
                pyqt6_datas.append(data)
        else:
            pyqt6_datas.append(data)
    
    # Filter binaries similarly - exclude unused module DLLs and their plugin dependencies
    for binary in tmp_ret[1]:
        if isinstance(binary, tuple) and len(binary) >= 2:
            # Check both source and destination paths, normalize separators
            src_path = str(binary[0]).lower().replace('\\', '/')
            dest_path = str(binary[1]).lower().replace('\\', '/')
            combined_path = src_path + ' ' + dest_path
            skip_patterns = ['webengine', 'bluetooth', 'location', 'multimedia', 'network', 'qml', 'quick',
                            'sql', 'svg', 'xml', 'charts', '3d', 'designer', 'help', 'opengl', 'print',
                            'serial', 'statemachine', 'texttospeech', 'websockets', 'webchannel',
                            # Exclude plugin directories that depend on excluded modules
                            'plugins/renderers', 'plugins/sceneparsers', 'plugins/webview',
                            'plugins/geometryloaders', 'pyqt6qmlplugin',
                            # Exclude specific plugin DLLs
                            'rhirenderer', 'assimpscene', 'gltfscene', 'qtwebview',
                            'defaultgeometryloader', 'gltfgeometryloader', 'openglrenderer',
                            'pyqt6qmlplugin.dll', 'defaultgeometryloader.dll', 'gltfgeometryloader.dll',
                            'openglrenderer.dll', 'rhirenderer.dll', 'assimpsceneimport.dll',
                            'gltfsceneexport.dll', 'gltfsceneimport.dll', 'qtwebview_webengine.dll',
                            'qtwebview_webview2.dll']
            if not any(skip in combined_path for skip in skip_patterns):
                pyqt6_binaries.append(binary)
        else:
            pyqt6_binaries.append(binary)
    
    # Filter hidden imports
    pyqt6_hiddenimports += [h for h in tmp_ret[2] if not any(ex in h for ex in excluded_qt_modules)]
except Exception:
    pass

datas = pyqt6_datas + unitypy_datas
binaries = pyqt6_binaries + unitypy_binaries
hiddenimports = pyqt6_hiddenimports + unitypy_hiddenimports

# Exclude unused standard library modules (be conservative - don't exclude modules that dependencies might need)
# Note: 'inspect' is needed by importlib.metadata (used by fsspec/UnityPy), so don't exclude it
excludes = [
    'pydoc',
    'tkinter',
    'unittest',
    'pdb',
    'doctest',
    'argparse',
    'difflib',
    'pydoc_data',
    'test',
    'tests',
    'distutils',
    'setuptools',
    'lib2to3',
] + excluded_qt_modules

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
    optimize=2,  # Use Python optimization level 2
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='FM26AttributeCustomizer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,  # Strip disabled on Windows (requires Unix strip tool)
    upx=True,  # Use UPX compression
    upx_exclude=['vcruntime140.dll', 'python*.dll'],  # Don't compress critical DLLs
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon,
)
