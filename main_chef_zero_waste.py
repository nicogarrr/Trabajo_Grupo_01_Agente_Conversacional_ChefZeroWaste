#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path

from BowChatChefZeroWaste_E3_EmbeddingsImagen import BowChatChefZeroWaste_E3_EmbeddingsImagen


if __name__ == "__main__":
    base = Path(__file__).resolve().parent
    data = base / "datos"
    chat = BowChatChefZeroWaste_E3_EmbeddingsImagen(
        fileVectors=str(data / "ChefZeroWaste.vec"),
        fileVoc=str(data / "ChefZeroWaste.voc"),
    )
    chat.run()
