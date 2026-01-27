# PyMuPDF Notes

- Fast local parsing via PyMuPDF (`fitz`).
- Less robust than specialized PDF parsers; table extraction is minimal.
- `page.get_text("markdown")` gives quick Markdown output.
- `page.get_text("text")` provides plain text for JSON.
- Image extraction uses `page.get_images(full=True)` and `Pixmap`.

Install:
```bash
pip install pymupdf
```

Nix note (if import fails with libstdc++ missing):
```bash
# Find a gcc lib path and export it:
ls /nix/store/*gcc*/lib/libstdc++.so.6 2>/dev/null | head -1
export LD_LIBRARY_PATH=/nix/store/<your-gcc-lib-hash>-gcc-<version>-lib/lib
```
