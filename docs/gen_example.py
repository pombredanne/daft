#!/usr/bin/env python

from __future__ import print_function

import os
import sys
from subprocess import check_call


this_path = os.path.dirname(os.path.abspath(__file__))
daft_path = os.path.dirname(this_path)
sys.path.insert(0, daft_path)

example_dir = os.path.join(daft_path, "examples")
out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "examples")
img_out_dir = os.path.join(this_path, "_static", "examples")

try:
    os.makedirs(out_dir)
except os.error:
    pass

try:
    os.makedirs(img_out_dir)
except os.error:
    pass

example_template = """.. _{example}:

{title}

.. figure:: /_static/examples/{example}.png

{doc}

::

{src}

"""


def main(fn):
    # Get the thumbnail info from './examples.info'.
    thumb_info = None
    with open(os.path.join(this_path, "examples.info")) as f:
        for line in f:
            if line[:len(fn)] == fn:
                thumb_info = [int(t) for t in line.split()[1:]]
                break

    assert thumb_info is not None, "Add {0} to ./examples.info".format(fn)

    # Run the code.
    pyfn = os.path.join(example_dir, fn + ".py")
    src = open(pyfn).read()
    print("Executing: " + pyfn)
    exec src

    # Generate the RST source file.
    src = src.split("\n")
    if __doc__ is None:
        title = fn.title() + "\n" + "=" * len(fn)
        doc = ""
    else:
        doc = __doc__.split("\n")
        title = "\n".join(doc[:3])
        doc = "\n".join(doc)
        src = src[len(__doc__.split("\n")):]

    fmt_src = "\n".join(["    " + l for l in src])
    img_path = os.path.join(img_out_dir, fn + ".png")
    thumb_path = os.path.join(img_out_dir, fn + "-thumb.png")

    rst = example_template.format(title=title, doc=doc, example=fn,
            src=fmt_src, img_path=img_path)

    # Write the RST file.
    rstfn = os.path.join(out_dir, fn + ".rst")
    print("Writing: " + rstfn)
    with open(rstfn, "w") as f:
        f.write(rst)

    # Remove the generated plots.
    try:
        os.remove(fn + ".png")
    except os.error:
        pass
    try:
        os.remove(fn + ".pdf")
    except os.error:
        pass

    # Save the new figure.
    print("Saving: " + img_path)
    pgm.figure.savefig(img_path, dpi=150)

    # Crop the thumbnail.
    cmd = " ".join(["convert",
                    "-crop 190x190+{0[0]:d}+{0[1]:d}".format(thumb_info),
                    img_path, thumb_path])
    print(cmd)
    check_call(cmd, shell=True)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        # Build all the examples.
        argv = [l.split()[0] for l in
                            open(os.path.join(this_path, "examples.info"))]
    else:
        argv = sys.argv[1:]

    for fn in argv:
        main(fn)
