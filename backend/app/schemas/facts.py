from pydantic import BaseModel, Field


class Evidence(BaseModel):

    page: int | None = None

    quote: str = Field(
        description=(
            "Exact supporting text from "
            "the document."
        )
    )


class ExtractedFact(BaseModel):

    fact_type: str

    value: str

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )

    evidence: Evidence


class FactExtractionResult(BaseModel):

    facts: list[ExtractedFact]