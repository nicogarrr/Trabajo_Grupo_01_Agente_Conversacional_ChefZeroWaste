#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Crea un embedding medio de gesto a partir de varias fotos.

Uso:
    python crear_embedding_gesto.py imagenes_acciones/gesto gestos/gesto_grupo.emb.vec
"""

from pathlib import Path
import sys

import numpy as np

from ImageActionEmbedder import ImageActionEmbedder


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def main():
    input_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("imagenes_acciones/gesto")
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("gestos/gesto_grupo.emb.vec")

    images = sorted(
        path for path in input_dir.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    )
    if len(images) == 0:
        raise SystemExit("No se han encontrado fotos en {}".format(input_dir))

    embedder = ImageActionEmbedder()
    vectors = [embedder.embedding_from_image(path) for path in images]
    mean_vector = np.mean(vectors, axis=0)
    norm = np.linalg.norm(mean_vector)
    if norm != 0:
        mean_vector = mean_vector / norm

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        " ".join("{:.6f}".format(float(value)) for value in mean_vector) + "\n",
        encoding="utf-8",
    )

    print("Embedding creado: {}".format(output_path))
    print("Fotos usadas: {}".format(len(images)))


if __name__ == "__main__":
    main()
