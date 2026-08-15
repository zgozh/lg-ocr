import os
import builtins
import importlib.util
import sys
from pathlib import Path

os.environ.setdefault("DISABLE_MODEL_SOURCE_CHECK", "True")


def _configure_runtime_dll_paths():
    roots = []
    if getattr(sys, "frozen", False):
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            roots.append(Path(meipass))
        roots.append(Path(sys.executable).resolve().parent)

    added_dirs = []
    for root in roots:
        if not root.exists():
            continue

        candidate_dirs = [
            root,
            root / "paddle",
            root / "paddle" / "libs",
            root / "Library" / "bin",
        ]

        for dll_name in ("mklml.dll", "libiomp5md.dll"):
            candidate_dirs.extend(path.parent for path in root.rglob(dll_name))

        seen = set()
        for directory in candidate_dirs:
            directory = directory.resolve()
            if not directory.exists():
                continue
            key = str(directory).lower()
            if key in seen:
                continue
            seen.add(key)
            added_dirs.append(str(directory))
            if hasattr(os, "add_dll_directory"):
                try:
                    os.add_dll_directory(str(directory))
                except OSError:
                    pass

    if added_dirs:
        current_path = os.environ.get("PATH", "")
        os.environ["PATH"] = os.pathsep.join(added_dirs + [current_path])


_configure_runtime_dll_paths()

from paddleocr import TableRecognitionPipelineV2
from paddlex.utils import deps as paddlex_deps

from config import build_pipeline_kwargs, build_predict_flags


_ORIGINAL_REQUIRE_EXTRA = paddlex_deps.require_extra
_ORIGINAL_IS_DEP_AVAILABLE = paddlex_deps.is_dep_available

_DEP_IMPORT_FALLBACKS = {
    "opencv-contrib-python": "cv2",
    "pypdfium2": "pypdfium2",
    "scikit-learn": "sklearn",
    "python-bidi": "bidi",
    "Jinja2": "jinja2",
    "shapely": "shapely",
    "sentencepiece": "sentencepiece",
    "tokenizers": "tokenizers",
    "regex": "regex",
    "pyclipper": "pyclipper",
}


def _patched_require_extra(extra, *, obj_name=None, alt=None):
    # PyInstaller onefile packaging may miss Python package metadata, which causes
    # PaddleX to mis-detect `paddlex[ocr]` as unavailable even when runtime modules exist.
    if extra == "ocr":
        return
    return _ORIGINAL_REQUIRE_EXTRA(extra, obj_name=obj_name, alt=alt)


def _patched_is_dep_available(dep, /, check_version=False):
    if _ORIGINAL_IS_DEP_AVAILABLE(dep, check_version=check_version):
        return True

    candidate_module_names = []

    mapped_name = _DEP_IMPORT_FALLBACKS.get(dep)
    if mapped_name:
        candidate_module_names.append(mapped_name)

    normalized_names = {
        dep,
        dep.replace("-", "_"),
        dep.replace("-", ""),
    }
    candidate_module_names.extend(normalized_names)

    for module_name in candidate_module_names:
        if module_name and importlib.util.find_spec(module_name) is not None:
            return True

    return False


paddlex_deps.is_dep_available = _patched_is_dep_available
paddlex_deps.require_extra = _patched_require_extra


def _patch_paddlex_runtime_imports():
    try:
        import cv2
        from paddlex.inference.common.reader import image_reader
        from paddlex.inference.utils.io import readers

        builtins.cv2 = cv2
        image_reader.cv2 = cv2
        readers.cv2 = cv2
    except Exception:
        pass

    try:
        import pypdfium2 as pdfium
        from paddlex.inference.utils.io import readers

        builtins.pdfium = pdfium
        readers.pdfium = pdfium
    except Exception:
        pass


_patch_paddlex_runtime_imports()


def build_pipeline(config):
    return TableRecognitionPipelineV2(**build_pipeline_kwargs(config))


def run_table_ocr(pipeline, image_path, device):
    return pipeline.predict(
        input=image_path,
        device=device,
        **build_predict_flags(),
    )
