from sentence_transformers import SentenceTransformer


MODEL_NAME = "all-MiniLM-L6-v2"


_model = None


def get_embedding_model():

    global _model

    if _model is None:

        _model = SentenceTransformer(
            MODEL_NAME
        )

    return _model


def embed_text(
    text: str,
) -> list[float]:

    model = get_embedding_model()

    embedding = model.encode(
        text,
        normalize_embeddings=True,
    )

    return embedding.tolist()


def embed_texts(
    texts: list[str],
) -> list[list[float]]:

    model = get_embedding_model()

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
    )

    return embeddings.tolist()