from __future__ import annotations

from pathlib import Path

POST_PROCESSORS = {
    "resizeIdolCard": "resize_idol_card",
    "resizeDrink": "resize_drink",
}


def resize_idol_card(path: Path) -> None:
    import cv2

    if not path.exists():
        return
    img = cv2.imread(str(path))
    if img is not None:
        img = cv2.resize(img, (140, 188), interpolation=cv2.INTER_AREA)
        cv2.imwrite(str(path), img)


def resize_drink(path: Path) -> None:
    import cv2

    if not path.exists():
        return
    img = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
    if img is not None and len(img.shape) == 3 and img.shape[2] == 4:
        img = cv2.resize(img, (68, 68), interpolation=cv2.INTER_AREA)
        b, g, r, a = cv2.split(img)
        mask = a == 0
        b[mask] = 255
        g[mask] = 255
        r[mask] = 255
        cv2.imwrite(str(path), cv2.merge([b, g, r]))
    elif img is not None:
        img = cv2.resize(img, (68, 68), interpolation=cv2.INTER_AREA)
        cv2.imwrite(str(path), img)


def apply_post_process(name: str | None, path: Path) -> None:
    if not name:
        return
    if name == "resizeIdolCard":
        resize_idol_card(path)
    elif name == "resizeDrink":
        resize_drink(path)