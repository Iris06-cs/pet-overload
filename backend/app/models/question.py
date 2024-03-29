import datetime
from typing import Any, Union, Dict
from werkzeug import Response
from .db import db, environment, SCHEMA, add_prefix_for_prod
from .utils import ValidationException, NotFoundException, ForbiddenException
from .user import User
import re
from sqlalchemy import or_


class Question(db.Model):
    """
    Question Model
    """

    __tablename__ = "questions"

    if environment == "production":
        __table_args__ = {"schema": SCHEMA}

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    details = db.Column(db.String(), nullable=False)
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow(),
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow(),
    )
    user_id = db.Column(
        db.Integer, db.ForeignKey(add_prefix_for_prod("users.id")), nullable=False
    )

    user = db.relationship("User", back_populates="user_questions")
    question_answers = db.relationship(
        "Answer", back_populates="question", cascade="all, delete"
    )
    question_votes = db.relationship(
        "QuestionVote", back_populates="question", cascade="all, delete"
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "details": self.details,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "user_id": self.user_id,
            "answers_count": len(self.question_answers),
            "votes_score": self.question_vote_score,
            # added user and answers to question response
            "user": self.user.to_dict(),
            "answers": [answer.to_dict() for answer in self.question_answers],
        }

    @classmethod
    def get_all_questions(cls) -> list[Any]:
        """
        Returns a list of all questions on the app
        """
        question_records = cls.query.all()

        return [question.to_dict() for question in question_records]

    @classmethod
    def filter_questions(cls, username=None, score=None, keyword=None) -> list[Any]:
        """
        Returns questions filtered by query parameters
        """
        if username:
            # query questions belongs to username
            question_records = cls._filter_question_by_username(username)

        elif score:
            #  query question_score>= score
            question_records = cls._filter_question_by_score(score)
        elif keyword:
            #  query question title include keyword
            question_records = cls._filter_question_by_keyword(keyword)
        else:
            question_records = cls.get_all_questions()
            return question_records

        return [question.to_dict() for question in question_records]

    @classmethod
    def _filter_question_by_username(cls, username=None):
        # query questions belongs to username
        if len(username) > 40:
            raise ValidationException("Author name cannot exceed 40 letters")
        user = User.query.filter(User.username == username).first()
        if user:
            question_records = cls.query.filter(cls.user_id == user.id).all()
        else:
            question_records = []
        return question_records

    @classmethod
    def _filter_question_by_score(cls, score=None):
        #  query question_score>= score
        try:
            score = int(score)
        except (TypeError, ValueError):
            raise ValidationException("Score must be integer")
        question_records = [
            q for q in cls.query.all() if q.question_vote_score >= int(score)
        ]
        return question_records

    @classmethod
    def _filter_question_by_keyword(cls, keyword=None):
        #  query question title include keyword
        words = keyword.split()
        if any(re.search(r"[^\w\s]", word) for word in words):
            raise ValidationException("Keywords should not contain special symbols.")

        all_words = [cls.title.ilike(f"%{word}%") for word in words]
        question_records = cls.query.filter(or_(*all_words)).all()
        return question_records

    @classmethod
    def get_question_by_id(cls, id: int) -> Union[dict[str, Any], None]:
        """
        Returns a question by id and all answers on that question
        """
        question = cls.query.filter_by(id=id).first()

        if not question:
            raise NotFoundException("Question not found.")

        answers = question.question_answers
        votes_score = question.question_vote_score

        return {
            "id": question.id,
            "title": question.title,
            "details": question.details,
            "created_at": question.created_at,
            "updated_at": question.updated_at,
            "author": question.user.username,
            "answers": [answer.to_dict() for answer in answers],
            "answers_count": len(answers),
            "votes_score": votes_score,
        }

    @classmethod
    def create_question(
        cls, title: str, details: str, user_id: int
    ) -> Union[Response, dict[str, Any]]:
        """
        Creates a new question
        """
        if not title:
            raise ValidationException("Title is required.")
        if not details:
            raise ValidationException("Details are required")

        question = cls(title=title, details=details, user_id=user_id)
        db.session.add(question)
        db.session.commit()

        return question.to_dict()

    @classmethod
    def update_question(
        cls, id: int, title: str, details: str, user_id: int
    ) -> Union[Response, dict]:
        """
        Updates a question by id, if the user is the author of the question
        """
        question = cls.query.filter_by(id=id).first()

        if not question:
            raise NotFoundException("Question couldn't found.")
        if not title:
            raise ValidationException("Title is required.")
        if not details:
            raise ValidationException("Details are required.")

        if int(user_id) != int(question.user_id):
            raise ForbiddenException("You are not the author of this question.")

        question.title = title
        question.details = details
        question.updated_at = datetime.datetime.utcnow()

        db.session.commit()

        return question.to_dict()

    @classmethod
    def delete_question(cls, id: int, user_id: int) -> bool:
        """
        Deletes a question by id if the current user is the author of the question
        """
        question = cls.query.filter_by(id=id).first()

        if not question:
            raise NotFoundException("Question couldn't be found.")

        if int(user_id) != int(question.user_id):
            raise ForbiddenException("You are not the author of this question.")

        db.session.delete(question)
        db.session.commit()

        return True

    @property
    def question_vote_score(self) -> int:
        """
        Returns vote score for this question
        """
        votes = self.question_votes

        if not votes:
            return 0

        return sum([1 if vote.is_liked else -1 for vote in votes])
