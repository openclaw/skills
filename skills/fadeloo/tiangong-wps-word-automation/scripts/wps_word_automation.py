import argparse
import os
from pathlib import Path

APP_PROGIDS = {
    "word": ["Word.Application"],
    "wps": ["KWPS.Application", "WPS.Application"],
}

WD_FORMAT_PDF = 17
WD_FORMAT_TEXT = 2
WD_PAGE_BREAK = 7


def get_app(app_name: str, visible: bool):
    import win32com.client  # type: ignore

    progids = APP_PROGIDS.get(app_name, [])
    for pid in progids:
        try:
            app = win32com.client.Dispatch(pid)
            app.Visible = bool(visible)
            return app
        except Exception:
            continue
    # fallback to Word
    app = win32com.client.Dispatch("Word.Application")
    app.Visible = bool(visible)
    return app


def open_doc(app, path: str):
    return app.Documents.Open(path, ReadOnly=False)


def save_as(doc, out_path: str, fmt=None):
    if fmt is None:
        doc.SaveAs(out_path)
    else:
        doc.SaveAs(out_path, fmt)


def cmd_read(args):
    app = get_app(args.app, args.visible)
    doc = open_doc(app, args.input)
    text = doc.Content.Text
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    else:
        print(text)
    doc.Close()
    app.Quit()


def cmd_replace(args):
    app = get_app(args.app, args.visible)
    doc = open_doc(app, args.input)
    find = doc.Content.Find
    find.Text = args.find
    find.Replacement.Text = args.replace
    find.Execute(Replace=2)
    save_as(doc, args.save)
    doc.Close()
    app.Quit()


def cmd_insert(args):
    app = get_app(args.app, args.visible)
    doc = open_doc(app, args.input)
    if args.where == "start":
        rng = doc.Range(0, 0)
        rng.InsertBefore(args.text)
    else:
        doc.Content.InsertAfter(args.text)
    save_as(doc, args.save)
    doc.Close()
    app.Quit()


def cmd_headings(args):
    app = get_app(args.app, args.visible)
    doc = open_doc(app, args.input)
    prefix = args.prefix
    for p in doc.Paragraphs:
        txt = p.Range.Text.strip()
        if txt.startswith(prefix):
            p.Range.Text = txt[len(prefix) :]
            p.Style = f"Heading {args.level}"
    save_as(doc, args.save)
    doc.Close()
    app.Quit()


def cmd_header_footer(args):
    app = get_app(args.app, args.visible)
    doc = open_doc(app, args.input)
    for section in doc.Sections:
        if args.header:
            section.Headers(1).Range.Text = args.header
        if args.footer:
            section.Footers(1).Range.Text = args.footer
    save_as(doc, args.save)
    doc.Close()
    app.Quit()


def cmd_page_break(args):
    app = get_app(args.app, args.visible)
    doc = open_doc(app, args.input)
    rng = doc.Range(doc.Content.End - 1, doc.Content.End - 1)
    rng.InsertBreak(WD_PAGE_BREAK)
    save_as(doc, args.save)
    doc.Close()
    app.Quit()


def cmd_merge(args):
    app = get_app(args.app, args.visible)
    base = open_doc(app, args.inputs[0])
    for p in args.inputs[1:]:
        base.Range(base.Content.End - 1).InsertFile(p)
        base.Range(base.Content.End - 1).InsertBreak(WD_PAGE_BREAK)
    save_as(base, args.output)
    base.Close()
    app.Quit()


def parse_ranges(s: str):
    ranges = []
    for part in s.split(","):
        a, b = part.split("-")
        ranges.append((int(a), int(b)))
    return ranges


def cmd_split(args):
    app = get_app(args.app, args.visible)
    doc = open_doc(app, args.input)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    ranges = parse_ranges(args.pages)
    for i, (a, b) in enumerate(ranges, 1):
        new = app.Documents.Add()
        rng = doc.Range(doc.GoTo(What=1, Which=1, Count=a), doc.GoTo(What=1, Which=1, Count=b + 1))
        rng.Copy()
        new.Range(0, 0).Paste()
        out = outdir / f"part_{i}.docx"
        save_as(new, str(out))
        new.Close()
    doc.Close()
    app.Quit()


def cmd_export(args):
    app = get_app(args.app, args.visible)
    doc = open_doc(app, args.input)
    fmt = WD_FORMAT_PDF if args.format == "pdf" else WD_FORMAT_TEXT
    save_as(doc, args.output, fmt)
    doc.Close()
    app.Quit()


def cmd_image(args):
    app = get_app(args.app, args.visible)
    doc = open_doc(app, args.input)
    rng = doc.Range(doc.Content.End - 1, doc.Content.End - 1)
    doc.InlineShapes.AddPicture(os.path.abspath(args.image), False, True, rng)
    save_as(doc, args.save)
    doc.Close()
    app.Quit()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--app", default="word", choices=["word", "wps"])
    parser.add_argument("--visible", default=False, action="store_true")

    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("read")
    p.add_argument("--input", required=True)
    p.add_argument("--output")
    p.set_defaults(func=cmd_read)

    p = sub.add_parser("replace")
    p.add_argument("--input", required=True)
    p.add_argument("--find", required=True)
    p.add_argument("--replace", required=True)
    p.add_argument("--save", required=True)
    p.set_defaults(func=cmd_replace)

    p = sub.add_parser("insert")
    p.add_argument("--input", required=True)
    p.add_argument("--text", required=True)
    p.add_argument("--where", choices=["start", "end"], default="end")
    p.add_argument("--save", required=True)
    p.set_defaults(func=cmd_insert)

    p = sub.add_parser("headings")
    p.add_argument("--input", required=True)
    p.add_argument("--level", type=int, choices=[1, 2, 3], default=1)
    p.add_argument("--prefix", required=True)
    p.add_argument("--save", required=True)
    p.set_defaults(func=cmd_headings)

    p = sub.add_parser("header-footer")
    p.add_argument("--input", required=True)
    p.add_argument("--header")
    p.add_argument("--footer")
    p.add_argument("--save", required=True)
    p.set_defaults(func=cmd_header_footer)

    p = sub.add_parser("page-break")
    p.add_argument("--input", required=True)
    p.add_argument("--save", required=True)
    p.set_defaults(func=cmd_page_break)

    p = sub.add_parser("merge")
    p.add_argument("--inputs", nargs="+", required=True)
    p.add_argument("--output", required=True)
    p.set_defaults(func=cmd_merge)

    p = sub.add_parser("split")
    p.add_argument("--input", required=True)
    p.add_argument("--pages", required=True)
    p.add_argument("--outdir", required=True)
    p.set_defaults(func=cmd_split)

    p = sub.add_parser("export")
    p.add_argument("--input", required=True)
    p.add_argument("--format", choices=["pdf", "txt"], required=True)
    p.add_argument("--output", required=True)
    p.set_defaults(func=cmd_export)

    p = sub.add_parser("image")
    p.add_argument("--input", required=True)
    p.add_argument("--image", required=True)
    p.add_argument("--save", required=True)
    p.set_defaults(func=cmd_image)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
