# app/api/work_archive.py
from __future__ import annotations
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path
from typing import List, Optional, Dict
import mimetypes
import urllib.parse
import datetime

router = APIRouter()

# 项目根目录：.../Mural-Restoration-System
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# 允许被浏览的根目录（按需增减）
CANDIDATE_ROOTS: Dict[str, Path] = {
    "doc": PROJECT_ROOT / "doc",
    "img": PROJECT_ROOT / "img",
    "static": PROJECT_ROOT / "static",
}

# 只保留存在的目录
ALLOWED_ROOTS = {k: v for k, v in CANDIDATE_ROOTS.items() if v.exists()}

# ----- 工具 -----
def is_inside(parent: Path, child: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except Exception:
        return False

def norm_rel(path: Path) -> str:
    return path.as_posix()

def ext_category(ext: str) -> str:
    e = ext.lower()
    if e in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".tiff", ".svg"}:
        return "image"
    if e in {".mp4", ".mov", ".avi", ".mkv", ".webm"}:
        return "video"
    if e in {".pdf", ".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx", ".csv", ".txt", ".md"}:
        return "document"
    if e in {".py", ".js", ".ts", ".vue", ".html", ".css", ".json", ".yaml", ".yml"}:
        return "code"
    return "other"

class FolderNode(BaseModel):
    label: str              # 展示名
    key: str                # 唯一键（相对路径，如 "img/xxx"）
    children: List["FolderNode"] = []

FolderNode.update_forward_refs()

class FileItem(BaseModel):
    name: str
    path: str               # 相对路径（如 img/a/b.png）
    ext: str
    size: int
    mtime: str              # ISO 字符串
    category: str           # image/video/document/code/other
    url: str                # 预览/下载用

def build_tree(root_name: str, root_path: Path) -> FolderNode:
    def walk_dir(base: Path) -> List[FolderNode]:
        nodes: List[FolderNode] = []
        for p in sorted(base.iterdir()):
            if p.is_dir() and not p.name.startswith("."):
                rel = norm_rel(p.relative_to(PROJECT_ROOT))
                nodes.append(FolderNode(label=p.name, key=rel, children=walk_dir(p)))
        return nodes
    return FolderNode(label=root_name, key=norm_rel(root_path.relative_to(PROJECT_ROOT)), children=walk_dir(root_path))

def list_files_in(dir_rel: Optional[str], q: str, category: Optional[str]) -> List[FileItem]:
    roots = ALLOWED_ROOTS.values()
    targets: List[Path] = []

    if dir_rel:
        candidate = (PROJECT_ROOT / dir_rel).resolve()
        # 必须在允许的根目录里
        if not any(is_inside(root, candidate) for root in roots):
            raise HTTPException(status_code=400, detail="Illegal directory path.")
        if not candidate.exists() or not candidate.is_dir():
            return []
        targets = [candidate]
    else:
        targets = [r for r in roots]

    result: List[FileItem] = []
    for base in targets:
        # 只列出当前目录下一层文件（不递归）
        for p in sorted(base.iterdir()):
            if p.is_file():
                ext = p.suffix or ""
                cat = ext_category(ext)
                if category and cat != category:
                    continue
                if q and q.lower() not in p.name.lower():
                    continue
                st = p.stat()
                rel = norm_rel(p.relative_to(PROJECT_ROOT))
                url = f"/api/work-archive/file?path={urllib.parse.quote(rel)}"
                result.append(FileItem(
                    name=p.name,
                    path=rel,
                    ext=ext,
                    size=st.st_size,
                    mtime=datetime.datetime.fromtimestamp(st.st_mtime).isoformat(timespec="seconds"),
                    category=cat,
                    url=url
                ))
    return result

# ----- API -----

@router.get("/folders", response_model=List[FolderNode])
def get_folders():
    if not ALLOWED_ROOTS:
        return []
    trees = [build_tree(name, path) for name, path in ALLOWED_ROOTS.items()]
    return trees

@router.get("/files", response_model=List[FileItem])
def get_files(
    dir: Optional[str] = Query(default=None, description="相对路径，如 img 或 img/sub"),
    q: str = Query(default="", description="关键词"),
    category: Optional[str] = Query(default=None, description="image/video/document/code/other"),
):
    return list_files_in(dir, q, category)

@router.get("/file")
def get_file(path: str = Query(..., description="相对路径，如 img/a.png")):
    file_path = (PROJECT_ROOT / path).resolve()
    if not any(is_inside(root, file_path) for root in ALLOWED_ROOTS.values()):
        raise HTTPException(status_code=400, detail="Illegal file path.")
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found.")
    media_type, _ = mimetypes.guess_type(str(file_path))
    return FileResponse(str(file_path), media_type=media_type or "application/octet-stream")
