"""
NutriLens AI — Scan History ORM Model
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, String, Text, JSON, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base

JSON_TYPE = JSON().with_variant(JSONB, "postgresql")
UUID_TYPE = Uuid(as_uuid=True)


class ScanHistory(Base):
    __tablename__ = "scan_history"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID_TYPE, primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID_TYPE,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    # ── Product Info ────────────────────────────────────────────────────────
    barcode: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    product_name: Mapped[str] = mapped_column(String(500), nullable=True)
    brand: Mapped[str] = mapped_column(String(255), nullable=True)
    product_image_url: Mapped[str] = mapped_column(Text, nullable=True)

    # ── Full Analysis Result ─────────────────────────────────────────────────
    scan_result: Mapped[dict] = mapped_column(JSON_TYPE, nullable=False)
    overall_health_score: Mapped[float] = mapped_column(Float, nullable=True)
    language: Mapped[str] = mapped_column(String(10), default="en")

    # ── Metadata ────────────────────────────────────────────────────────────
    scanned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    def __repr__(self) -> str:
        return f"<ScanHistory id={self.id} barcode={self.barcode}>"
