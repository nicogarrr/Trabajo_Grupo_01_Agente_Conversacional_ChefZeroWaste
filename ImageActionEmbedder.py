#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path

import numpy as np
from PIL import Image


class ImageActionEmbedder:
    """
    Embeddings de imagen para ayudar a detectar la accion del agente.
    La imagen no aporta parametros; solo refuerza la categoria/operador.
    """

    ACTION_IMAGES = {
        "instrucciones": "instrucciones.png",
        "anadir_ingredientes": "anadir_ingredientes.png",
        "recomendar_receta": "recomendar_receta.png",
        "sustituir_ingrediente": "sustituir_ingrediente.png",
        "ajustar_raciones": "ajustar_raciones.png",
        "lista_compra": "lista_compra.png",
    }

    def __init__(self, reference_dir=None):
        if reference_dir is None:
            reference_dir = Path(__file__).resolve().parent / "imagenes_acciones"
        self.reference_dir = Path(reference_dir)
        self.reference = self._load_reference_embeddings()

    def action_vector(self, image_path, categories):
        """
        Devuelve un vector con una similitud por categoria.
        El orden coincide con la lista categories del agente.
        """
        scores = self._raw_scores(image_path, categories)
        if len(scores) == 0:
            return [0.0] * len(categories)

        best_index = int(np.argmax(scores))
        if scores[best_index] < 0.55:
            return [0.0] * len(categories)

        visual = [0.0] * len(categories)
        visual[best_index] = round(scores[best_index], 4)
        return visual

    def best_action(self, image_path, categories):
        scores = self._raw_scores(image_path, categories)
        if len(scores) == 0:
            return None
        index = int(np.argmax(scores))
        return {
            "accion": categories[index],
            "similitud": round(scores[index], 4),
            "vector": [round(score, 4) for score in scores],
        }

    def _raw_scores(self, image_path, categories):
        path = Path(image_path)
        if not path.exists():
            local = Path(__file__).resolve().parent / image_path
            path = local if local.exists() else path
        if not path.exists():
            return []

        embedding = self.embedding_from_image(path)
        scores = []
        for category in categories:
            reference_embedding = self.reference.get(category)
            if reference_embedding is None:
                scores.append(0.0)
            else:
                scores.append(self._cosine(embedding, reference_embedding))
        return scores

    def embedding_from_image(self, image_path):
        image = Image.open(image_path).convert("RGB").resize((48, 48))
        arr = np.asarray(image, dtype=np.float32) / 255.0
        gray = arr.mean(axis=2)

        mean_rgb = arr.mean(axis=(0, 1))
        std_rgb = arr.std(axis=(0, 1))

        # Forma simple: imagen en baja resolucion mas bordes horizontales/verticales.
        small = np.asarray(image.convert("L").resize((12, 12)), dtype=np.float32) / 255.0
        dx = np.abs(gray[:, 1:] - gray[:, :-1]).mean(axis=0)
        dy = np.abs(gray[1:, :] - gray[:-1, :]).mean(axis=1)

        features = np.concatenate([mean_rgb, std_rgb, small.flatten(), dx, dy])
        return self._safe_unit(features)

    def _load_reference_embeddings(self):
        reference = {}
        for action, filename in self.ACTION_IMAGES.items():
            path = self.reference_dir / filename
            if path.exists():
                reference[action] = self.embedding_from_image(path)
        return reference

    def _safe_unit(self, vector):
        vector = np.asarray(vector, dtype=np.float32)
        norm = np.linalg.norm(vector)
        if norm == 0:
            return vector
        return vector / norm

    def _cosine(self, a, b):
        denom = np.linalg.norm(a) * np.linalg.norm(b)
        if denom == 0:
            return 0.0
        return float(np.dot(a, b) / denom)
