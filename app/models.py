from . import db
from sqlalchemy import text


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    password = db.Column(db.String(256), nullable=False)

    records = db.relationship("Record", back_populates="user", cascade="all, delete-orphan")
    owner_of_category = db.relationship("Category", back_populates="owner", cascade="all, delete-orphan")


class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    owner = db.relationship("User", back_populates="owner_of_category")
    records = db.relationship("Record", back_populates="category", cascade="all, delete-orphan")
    __table_args__ = (
        db.UniqueConstraint("owner_id", "name", name="uq_category_user_name"),
        db.Index(
            "Index_category_global_name",
            "name",
            unique=True,
            postgresql_where=text("owner_id IS NULL"),
        ),
    )


class Record(db.Model):
    __tablename__ = "records"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    category_id = db.Column(
        db.Integer,
        db.ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    datetime = db.Column(db.DateTime(timezone=True), nullable=False, index=True)
    amount = db.Column(db.Float, nullable=False)

    user = db.relationship("User", back_populates="records")
    category = db.relationship("Category", back_populates="records")

    __table_args__ = (
        db.Index("ix_records_user_cat_dt", "user_id", "category_id", "datetime"),
        db.CheckConstraint("amount >= 0", name="ck_record_amount_nonnegative"),
    )
