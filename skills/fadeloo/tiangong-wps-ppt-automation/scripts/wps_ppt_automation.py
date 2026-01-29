import argparse
import os
from pathlib import Path

APP_PROGIDS = {
    "powerpoint": ["PowerPoint.Application"],
    "wps": ["KWPP.Application", "WPP.Application"],
}

PP_SAVE_AS_PDF = 32
PP_LAYOUT_TEXT = 1


def get_app(app_name: str, visible: bool):
    import win32com.client  # type: ignore

    progids = APP_PROGIDS.get(app_name, [])
    for pid in progids:
        try:
            app = win32com.client.Dispatch(pid)
            try:
                app.Visible = bool(visible)
            except Exception:
                pass
            return app
        except Exception:
            continue
    # fallback to PowerPoint
    app = win32com.client.Dispatch("PowerPoint.Application")
    try:
        app.Visible = bool(visible)
    except Exception:
        pass
    return app


def open_ppt(app, path: str, visible: bool):
    ap = os.path.abspath(path)
    # Open(FileName, ReadOnly, Untitled, WithWindow)
    try:
        return app.Presentations.Open(ap, False, False, visible)
    except Exception:
        return app.Presentations.Open(ap)


def save_as(pres, out_path: str, fmt=None):
    if fmt is None:
        pres.SaveAs(out_path)
    else:
        pres.SaveAs(out_path, fmt)


def iter_text(shapes):
    for shape in shapes:
        try:
            if shape.HasTextFrame and shape.TextFrame.HasText:
                yield shape.TextFrame.TextRange.Text
        except Exception:
            continue


def cmd_read(args):
    app = get_app(args.app, args.visible)
    pres = open_ppt(app, args.input, args.visible)
    lines = []
    for i, slide in enumerate(pres.Slides, 1):
        lines.append(f"# Slide {i}")
        for txt in iter_text(slide.Shapes):
            if txt:
                lines.append(txt.strip())
    content = "\n".join(lines)
    if args.output:
        Path(args.output).write_text(content, encoding="utf-8")
    else:
        print(content)
    pres.Close()
    app.Quit()


def cmd_notes(args):
    app = get_app(args.app, args.visible)
    pres = open_ppt(app, args.input, args.visible)
    lines = []
    for i, slide in enumerate(pres.Slides, 1):
        lines.append(f"# Slide {i} Notes")
        try:
            notes = slide.NotesPage.Shapes
            for txt in iter_text(notes):
                if txt:
                    lines.append(txt.strip())
        except Exception:
            pass
    content = "\n".join(lines)
    if args.output:
        Path(args.output).write_text(content, encoding="utf-8")
    else:
        print(content)
    pres.Close()
    app.Quit()


def cmd_outline(args):
    app = get_app(args.app, args.visible)
    pres = open_ppt(app, args.input, args.visible)
    lines = []
    for i, slide in enumerate(pres.Slides, 1):
        title = ""
        try:
            if slide.Shapes.HasTitle:
                title = slide.Shapes.Title.TextFrame.TextRange.Text.strip()
        except Exception:
            pass
        lines.append(f"{i}. {title}")
    content = "\n".join(lines)
    if args.output:
        Path(args.output).write_text(content, encoding="utf-8")
    else:
        print(content)
    pres.Close()
    app.Quit()


def cmd_export(args):
    app = get_app(args.app, args.visible)
    pres = open_ppt(app, args.input, args.visible)
    if args.format == "pdf":
        save_as(pres, args.output, PP_SAVE_AS_PDF)
    else:
        outdir = Path(args.outdir)
        outdir.mkdir(parents=True, exist_ok=True)
        pres.Export(str(outdir), "PNG")
    pres.Close()
    app.Quit()


def cmd_replace(args):
    app = get_app(args.app, args.visible)
    pres = open_ppt(app, args.input, args.visible)
    for slide in pres.Slides:
        for shape in slide.Shapes:
            try:
                if shape.HasTextFrame and shape.TextFrame.HasText:
                    tr = shape.TextFrame.TextRange
                    tr.Text = tr.Text.replace(args.find, args.replace)
            except Exception:
                continue
    save_as(pres, args.save)
    pres.Close()
    app.Quit()


def cmd_insert_slide(args):
    app = get_app(args.app, args.visible)
    pres = open_ppt(app, args.input, args.visible)
    pres.Slides.Add(args.index, PP_LAYOUT_TEXT)
    save_as(pres, args.save)
    pres.Close()
    app.Quit()


def cmd_delete_slide(args):
    app = get_app(args.app, args.visible)
    pres = open_ppt(app, args.input, args.visible)
    pres.Slides(args.index).Delete()
    save_as(pres, args.save)
    pres.Close()
    app.Quit()


def cmd_font(args):
    app = get_app(args.app, args.visible)
    pres = open_ppt(app, args.input, args.visible)
    for slide in pres.Slides:
        for shape in slide.Shapes:
            try:
                if shape.HasTextFrame and shape.TextFrame.HasText:
                    tr = shape.TextFrame.TextRange
                    if args.name:
                        tr.Font.Name = args.name
                    if args.size:
                        tr.Font.Size = args.size
            except Exception:
                continue
    save_as(pres, args.save)
    pres.Close()
    app.Quit()


def cmd_theme(args):
    app = get_app(args.app, args.visible)
    pres = open_ppt(app, args.input, args.visible)
    pres.ApplyTheme(args.theme)
    save_as(pres, args.save)
    pres.Close()
    app.Quit()


def cmd_extract_images(args):
    app = get_app(args.app, args.visible)
    pres = open_ppt(app, args.input, args.visible)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    idx = 1
    for slide in pres.Slides:
        for shape in slide.Shapes:
            try:
                if shape.Type in (11, 13):  # linked picture / picture
                    out = outdir / f"img_{idx}.png"
                    shape.Export(str(out), 2)
                    idx += 1
            except Exception:
                continue
    pres.Close()
    app.Quit()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--app", default="powerpoint", choices=["powerpoint", "wps"])
    parser.add_argument("--visible", default=False, action="store_true")

    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("read")
    p.add_argument("--input", required=True)
    p.add_argument("--output")
    p.set_defaults(func=cmd_read)

    p = sub.add_parser("notes")
    p.add_argument("--input", required=True)
    p.add_argument("--output")
    p.set_defaults(func=cmd_notes)

    p = sub.add_parser("outline")
    p.add_argument("--input", required=True)
    p.add_argument("--output")
    p.set_defaults(func=cmd_outline)

    p = sub.add_parser("export")
    p.add_argument("--input", required=True)
    p.add_argument("--format", choices=["pdf", "images"], required=True)
    p.add_argument("--output")
    p.add_argument("--outdir")
    p.set_defaults(func=cmd_export)

    p = sub.add_parser("replace")
    p.add_argument("--input", required=True)
    p.add_argument("--find", required=True)
    p.add_argument("--replace", required=True)
    p.add_argument("--save", required=True)
    p.set_defaults(func=cmd_replace)

    p = sub.add_parser("insert-slide")
    p.add_argument("--input", required=True)
    p.add_argument("--index", type=int, required=True)
    p.add_argument("--save", required=True)
    p.set_defaults(func=cmd_insert_slide)

    p = sub.add_parser("delete-slide")
    p.add_argument("--input", required=True)
    p.add_argument("--index", type=int, required=True)
    p.add_argument("--save", required=True)
    p.set_defaults(func=cmd_delete_slide)

    p = sub.add_parser("font")
    p.add_argument("--input", required=True)
    p.add_argument("--name")
    p.add_argument("--size", type=int)
    p.add_argument("--save", required=True)
    p.set_defaults(func=cmd_font)

    p = sub.add_parser("theme")
    p.add_argument("--input", required=True)
    p.add_argument("--theme", required=True)
    p.add_argument("--save", required=True)
    p.set_defaults(func=cmd_theme)

    p = sub.add_parser("extract-images")
    p.add_argument("--input", required=True)
    p.add_argument("--outdir", required=True)
    p.set_defaults(func=cmd_extract_images)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
