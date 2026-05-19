#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
EJERCICIO 3 y 4: informacion extra con embeddings de imagen y gesto.
Equivale a BowChatCalculadora_E3_ExtraInfo.py del ejemplo de clase.
"""

from pathlib import Path
import re

import numpy as np

from BowChatChefZeroWaste_E2_STM import BowChatChefZeroWaste_E2_STM
from ImageActionEmbedder import ImageActionEmbedder


class BowChatChefZeroWaste_E3_EmbeddingsImagen(BowChatChefZeroWaste_E2_STM):
    def __init__(self, fileVectors, fileVoc):
        BowChatChefZeroWaste_E2_STM.__init__(self, fileVectors, fileVoc)
        self.image_embedder = ImageActionEmbedder()
        # Este gesto nuevo refuerza dos operaciones nuevas del proyecto.
        self.gesture_actions = ["planificar_menu", "calcular_caducidad"]
        self.gesture_reference_path = Path(__file__).resolve().parent / "gestos" / "gesto_grupo.emb.vec"
        self.STMultimaImagen = None
        self.STMultimaAccionVisual = None
        self.STMultimaConfianzaVisual = None

    def vectorize(self, normSen):
        """
        Anade la descripcion de imagen justo antes de la descripcion BoW.
        Es el mismo esquema que las emociones de clase:

            vector = [embedding_gesto, embedding_imagen, descripcion_BoW]
        """
        gestureVec = self._gesture_embedding()
        imgVec = self._image_embedding()

        quiet = getattr(self, "_quiet_vectorize", False)
        self._quiet_vectorize = True
        try:
            bowVector, entities = super().vectorize(normSen)
        finally:
            self._quiet_vectorize = quiet

        vector = np.concatenate([gestureVec, imgVec, bowVector])

        if not getattr(self, "_quiet_vectorize", False):
            print("Embedding gesto -> {}".format(list(gestureVec)))
            print("Embedding imagen -> {}".format(list(imgVec)))
            print("Descripcion BoW {} -> {}".format(normSen, list(bowVector)))
            print("Descripcion completa (gesto + imagen + BoW) -> {}".format(self._plain_vector(vector)))

        return vector, entities

    def vectorFromStr(self, vectorStr):
        vector = super().vectorFromStr(vectorStr)
        ncat = len(self.categories)
        expected = (2 * ncat) + len(self.Vec.vocabulary)
        if len(vector) == expected:
            return vector
        # Ejemplos antiguos: 6 acciones visuales y sin bloque de gesto.
        if ncat == 9 and 6 < len(vector) <= 50:
            return [0.0] * ncat + vector[:6] + [0.0, 0.0, 0.0] + vector[6:]
        # Ejemplos con planificar_menu y caducidad: 8 acciones visuales y sin bloque de gesto.
        if ncat == 9 and 50 < len(vector) <= 65:
            return [0.0] * ncat + vector[:8] + [0.0] + vector[8:]
        # Ejemplos actuales previos a esta rama: 9 acciones visuales y sin bloque de gesto.
        if ncat < len(vector) < expected:
            return [0.0] * ncat + vector
        return vector

    def _gesture_embedding(self):
        embedding_path = self._extract_embedding_path(self._last_raw_sentence)
        if embedding_path is None:
            return [0.0] * len(self.categories)

        resolved = self._resolve_image_path(embedding_path)
        values = self._read_named_or_numeric_embedding(resolved)
        if len(values) == 0:
            return [0.0] * len(self.categories)
        if len(values) > len(self.categories):
            # Si el .emb.vec viene de fotos reales, lo comparamos con el gesto de referencia.
            return self._raw_gesture_embedding(values)

        if len(values) < len(self.categories):
            values = values + [0.0] * (len(self.categories) - len(values))
        values = values[: len(self.categories)]
        return [float(value) * 5.0 for value in values]

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

    def _extract_embedding_path(self, sentence):
        suffix = r"(?:emb|embedding|gesto)\.vec"
        patterns = [
            rf'"([^"]*{suffix})"',
            rf"'([^']*{suffix})'",
            rf"(?:embedding|emb|gesto)\s+([^\s]*{suffix})",
            rf"([^\s]*{suffix})",
        ]
        for pattern in patterns:
            match = re.search(pattern, sentence, flags=re.IGNORECASE)
            if match:
                return match.group(1)
        return None

    def _read_named_or_numeric_embedding(self, path):
        path = Path(path)
        if not path.exists():
            return []

        named = [0.0] * len(self.categories)
        numeric = []
        has_named = False
        for line in path.read_text(encoding="utf-8").splitlines():
            clean = line.split("#", 1)[0].strip()
            if len(clean) == 0:
                continue
            parts = clean.replace(",", " ").replace(";", " ").split()
            if len(parts) == 2 and parts[0] in self.categories:
                try:
                    named[self.categories.index(parts[0])] = float(parts[1])
                    has_named = True
                except ValueError:
                    pass
            else:
                for part in parts:
                    try:
                        numeric.append(float(part))
                    except ValueError:
                        pass

        return named if has_named else numeric

    def _raw_gesture_embedding(self, values):
        reference = self._read_named_or_numeric_embedding(self.gesture_reference_path)
        if len(reference) == 0 or len(reference) != len(values):
            return [0.0] * len(self.categories)

        similarity = self._cosine(values, reference)
        if similarity < 0.55:
            return [0.0] * len(self.categories)

        gesture = [0.0] * len(self.categories)
        for action in self.gesture_actions:
            if action in self.categories:
                # El mismo gesto suma fuerza a las dos operaciones visuales.
                gesture[self.categories.index(action)] = round(similarity * 5.0, 4)
        return gesture

    def _cosine(self, a, b):
        a = np.asarray(a, dtype=np.float32)
        b = np.asarray(b, dtype=np.float32)
        denom = np.linalg.norm(a) * np.linalg.norm(b)
        if denom == 0:
            return 0.0
        return float(np.dot(a, b) / denom)

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
