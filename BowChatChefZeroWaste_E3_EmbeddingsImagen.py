#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
EJERCICIO 3: informacion extra con embeddings de imagen.
Equivale a BowChatCalculadora_E3_ExtraInfo.py del ejemplo de clase.
"""

from pathlib import Path

import numpy as np

from BowChatChefZeroWaste_E2_STM import BowChatChefZeroWaste_E2_STM
from ImageActionEmbedder import ImageActionEmbedder


class BowChatChefZeroWaste_E3_EmbeddingsImagen(BowChatChefZeroWaste_E2_STM):
    def __init__(self, fileVectors, fileVoc):
        BowChatChefZeroWaste_E2_STM.__init__(self, fileVectors, fileVoc)
        self.image_embedder = ImageActionEmbedder()
        self.STMultimaImagen = None
        self.STMultimaAccionVisual = None
        self.STMultimaConfianzaVisual = None

    def vectorize(self, normSen):
        """
        Anade la descripcion de imagen justo antes de la descripcion BoW.
        Es el mismo esquema que las emociones de clase:

            vector = [embedding_imagen, descripcion_BoW]
        """
        imgVec = self._image_embedding()

        quiet = getattr(self, "_quiet_vectorize", False)
        self._quiet_vectorize = True
        try:
            bowVector, entities = super().vectorize(normSen)
        finally:
            self._quiet_vectorize = quiet

        vector = np.concatenate([imgVec, bowVector])

        if not getattr(self, "_quiet_vectorize", False):
            print("Embedding imagen -> {}".format(list(imgVec)))
            print("Descripcion BoW {} -> {}".format(normSen, list(bowVector)))
            print("Descripcion completa (imagen + BoW) -> {}".format(self._plain_vector(vector)))

        return vector, entities

    def vectorFromStr(self, vectorStr):
        vector = super().vectorFromStr(vectorStr)
        legacy_image_dims = len(self.categories) - 1
        # Los ejemplos antiguos tienen 6 posiciones de imagen; la nueva accion anade una septima.
        if legacy_image_dims > 0 and legacy_image_dims < len(vector) <= 50:
            return vector[:legacy_image_dims] + [0.0] + vector[legacy_image_dims:]
        return vector

    def _image_embedding(self):
        image_path = self._extract_image_path(self._last_raw_sentence)
        if image_path is None:
            return [0.0] * len(self.categories)

        resolved = self._resolve_image_path(image_path)
        imgVec = self.image_embedder.action_vector(resolved, self.categories)
        best_action = self.image_embedder.best_action(resolved, self.categories)

        self.STMultimaImagen = str(resolved)
        if best_action is not None:
            self.STMultimaAccionVisual = best_action["accion"]
            self.STMultimaConfianzaVisual = best_action["similitud"]
        else:
            self.STMultimaAccionVisual = None
            self.STMultimaConfianzaVisual = None

        return [value * 5.0 for value in imgVec]

    def _resolve_image_path(self, image_path):
        path = Path(image_path)
        if path.exists():
            return path
        local = Path(__file__).resolve().parent / image_path
        if local.exists():
            return local
        return path

    def _plain_vector(self, vector):
        return [float(value) for value in vector]
