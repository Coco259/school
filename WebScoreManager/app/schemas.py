from flask import jsonify, request
from pydantic import BaseModel, Field, ValidationError, field_validator

from .security import require_csrf


class AdminLoginModel(BaseModel):
    username: str
    password: str


class StudentCreateModel(BaseModel):
    student_id: int | None = None
    name: str
    gender: str | None = None
    age: int | None = None
    class_: str | None = Field(default=None, alias='class')
    password: str | None = None

    @field_validator('age')
    @classmethod
    def age_range(cls, value: int | None) -> int | None:
        if value is None:
            return value
        if not (1 <= value <= 100):
            raise ValueError('age must be between 1 and 100')
        return value


class CourseCreateModel(BaseModel):
    course_name: str
    teacher: str | None = None


class ScoreCreateModel(BaseModel):
    student_id: int
    course_id: int
    score: float

    @field_validator('score')
    @classmethod
    def score_range(cls, value: float) -> float:
        if value < 0 or value > 100:
            raise ValueError('score must be between 0 and 100')
        return value


class StudentLoginModel(BaseModel):
    student_id: int | str
    password: str | None = None


class StudentUpdateModel(BaseModel):
    name: str | None = None
    gender: str | None = None
    age: int | None = None
    class_: str | None = Field(default=None, alias='class')


class CourseUpdateModel(BaseModel):
    course_name: str | None = None
    teacher: str | None = None


class ScoreUpdateModel(BaseModel):
    student_id: int | None = None
    course_id: int | None = None
    score: float | None = None


class AdminPasswordChangeModel(BaseModel):
    old_password: str
    new_password: str


class StudentPasswordChangeModel(BaseModel):
    old_password: str | None = None
    new_password: str


class AdminResetStudentModel(BaseModel):
    pass


def validate_json(model):
    def decorator(fn):
        def wrapper(*args, **kwargs):
            try:
                err = require_csrf()
                if err:
                    return err
            except Exception:
                pass
            try:
                data = request.get_json(force=True)
            except Exception:
                return jsonify({'success': False, 'message': 'Invalid JSON'}), 400
            try:
                parsed = model(**data)
            except ValidationError as exc:
                details = []
                for err in exc.errors():
                    sanitized = dict(err)
                    ctx = sanitized.get('ctx')
                    if isinstance(ctx, dict):
                        sanitized['ctx'] = {key: str(value) for key, value in ctx.items()}
                    details.append(sanitized)
                return (
                    jsonify(
                        {
                            'success': False,
                            'message': 'validation error',
                            'errors': details,
                        }
                    ),
                    400,
                )
            request.parsed = parsed
            return fn(*args, **kwargs)

        wrapper.__name__ = fn.__name__
        return wrapper

    return decorator
