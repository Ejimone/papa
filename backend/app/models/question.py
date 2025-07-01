from sqlalchemy import Column, String, Integer, Float, Text, ForeignKey, Table, DateTime, JSON, Boolean
from sqlalchemy.orm import relationship
from app.models.base import Base # Assuming Base has id, created_at, updated_at

# Association table for question_tags (Many-to-Many)
# Placeholder: Actual Tag model would be needed
# question_tags_table = Table(
#     "question_tags_association",
#     Base.metadata,
#     Column("question_id", Integer, ForeignKey("questions.id"), primary_key=True),
#     Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
# )

class Question(Base):
    __tablename__ = "questions"

    # Core fields from documentation
    title = Column(String(255), nullable=True) # Optional title
    content = Column(Text, nullable=False) # Main text content of the question
    question_type = Column(String(50), nullable=True) # MCQ, Short Answer, Essay, Numerical (from MetadataExtractor)

    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=True) # Link to Subject model
    # subject = relationship("Subject", back_populates="questions") # Define in Subject model too

    difficulty_level_label = Column(String(50), nullable=True) # e.g., Easy, Medium, Hard (from MetadataExtractor)
    difficulty_level_score = Column(Float, nullable=True) # e.g., 0.0 to 1.0 (from MetadataExtractor)

    # Metadata from documentation (question_metadata table in original SQL schema)
    # These could be columns directly on the Question table or in a related JSONB/JSON column,
    # or a separate QuestionMetadata one-to-one table.
    # For simplicity in this conceptual model, let's add some directly or use JSON.

    source = Column(String(255), nullable=True) # e.g., "Exam 2021", "Textbook Chapter 5"
    year = Column(Integer, nullable=True) # Year of the exam/source
    priority_score = Column(Float, nullable=True) # Calculated score for importance/frequency

    # keywords = Column(JSON, nullable=True) # Store as list of strings: ["keyword1", "keyword2"] (from TextProcessor/MetadataExtractor)
    # tags = relationship("Tag", secondary=question_tags_table, back_populates="questions") # If using a Tag model

    # AI-Generated Content / Fields (Conceptual - not necessarily direct DB columns without thought)
    # ai_explanation_id = Column(Integer, ForeignKey("explanations.id"), nullable=True) # If explanations are separate
    # ai_explanation_text = Column(Text, nullable=True) # Or store directly if simple

    # raw_ocr_text = Column(Text, nullable=True) # If question originated from an image
    # image_url = Column(String, nullable=True) # If an image is associated

    # For vector storage, the actual embedding vector is usually NOT stored in PostgreSQL.
    # It's stored in a vector database like ChromaDB.
    # PostgreSQL would store the ID that links to the vector in ChromaDB.
    # vector_id = Column(String, unique=True, index=True, nullable=True) # ID used in ChromaDB

    # Fields for tracking processing status
    is_processed_for_embedding = Column(Boolean, default=False)
    processing_error_log = Column(Text, nullable=True)


    # Relationships (examples)
    # images = relationship("QuestionImage", back_populates="question") # If QuestionImage model exists
    # attempts = relationship("UserAttempt", back_populates="question") # If UserAttempt model exists
    # original_for_similars = relationship("SimilarQuestion", foreign_keys="[SimilarQuestion.similar_question_id]", back_populates="similar_question_obj")
    # similars_generated = relationship("SimilarQuestion", foreign_keys="[SimilarQuestion.original_question_id]", back_populates="original_question_obj")


    def __repr__(self):
        return f"<Question(id={self.id}, title='{self.title[:30]}...')>"


# Example for related models if defined (conceptual)
# class Subject(Base):
#     __tablename__ = "subjects"
#     name = Column(String, unique=True, index=True)
#     questions = relationship("Question", back_populates="subject")

# class Tag(Base):
#     __tablename__ = "tags"
#     name = Column(String, unique=True, index=True)
#     questions = relationship("Question", secondary=question_tags_table, back_populates="tags")

# class QuestionImage(Base):
#     __tablename__ = "question_images"
#     question_id = Column(Integer, ForeignKey("questions.id"))
#     image_url = Column(String, nullable=False)
#     ocr_text = Column(Text, nullable=True)
#     question = relationship("Question", back_populates="images")

# class Explanation(Base):
# __tablename__ = "explanations"
#    question_id = Column(Integer, ForeignKey("questions.id"), unique=True) # One-to-one or one-to-many if multiple explanation types
#    content = Column(Text, nullable=False)
#    type = Column(String(50), default="ai_generated") # e.g., "ai_generated", "manual"
#    # question = relationship("Question", back_populates="explanation")

# class SimilarQuestion(Base): # Association object for self-referential many-to-many
#     __tablename__ = "similar_questions"
#     original_question_id = Column(Integer, ForeignKey("questions.id"), primary_key=True)
#     similar_question_id = Column(Integer, ForeignKey("questions.id"), primary_key=True)
#     similarity_score = Column(Float, nullable=True)
#
#     original_question_obj = relationship("Question", foreign_keys=[original_question_id], back_populates="similars_generated")
#     similar_question_obj = relationship("Question", foreign_keys=[similar_question_id], back_populates="original_for_similars")
