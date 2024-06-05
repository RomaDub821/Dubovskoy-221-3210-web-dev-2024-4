import hashlib
import uuid
import os
from enum import Enum

from werkzeug.utils import secure_filename
from flask import current_app
from models import db, Course, Image, Review


class CoursesFilter:
    def __init__(self, name, category_ids):
        self.name = name
        self.category_ids = category_ids
        self.query = db.select(Course)

    def perform(self):
        self.__filter_by_name()
        self.__filter_by_category_ids()
        return self.query.order_by(Course.created_at.desc())

    def __filter_by_name(self):
        if self.name:
            self.query = self.query.filter(
                Course.name.ilike('%' + self.name + '%'))

    def __filter_by_category_ids(self):
        if self.category_ids:
            self.query = self.query.filter(
                Course.category_id.in_(self.category_ids))


class ImageSaver:
    def __init__(self, file):
        self.file = file

    def save(self):
        self.img = self.__find_by_md5_hash()
        if self.img is not None:
            return self.img
        file_name = secure_filename(self.file.filename)
        self.img = Image(
            id=str(uuid.uuid4()),
            file_name=file_name,
            mime_type=self.file.mimetype,
            md5_hash=self.md5_hash)
        self.file.save(
            os.path.join(current_app.config['UPLOAD_FOLDER'],
                         self.img.storage_filename))
        db.session.add(self.img)
        db.session.commit()
        return self.img

    def __find_by_md5_hash(self):
        self.md5_hash = hashlib.md5(self.file.read()).hexdigest()
        self.file.seek(0)
        return db.session.execute(db.select(Image).filter(Image.md5_hash == self.md5_hash)).scalar()


class ReviewSortType(Enum):
    NEWEST = (1, "Сначала новые")
    OLDEST = (2, "Сначала старые")
    MOSTPOSITIVE = (3, "Сначала позитивные")
    MOSTNEGATIVE = (4, "Сначала негативные")

    @staticmethod
    def get_by_value(value):
        for sort_type in ReviewSortType:
            if sort_type.value[0] == value:
                return sort_type
        raise ValueError(f"{value} is not a valid ReviewSortType")


class ReviewsFilter:
    def __init__(self, course_id, type_sort_id: ReviewSortType):
        self.course_id = course_id
        self.type_sort_id = type_sort_id
        self.query = db.select(Review)

    def perform(self):
        self.__order_by_sort_id()
        return self.query.filter_by(course_id=self.course_id)

    def __order_by_sort_id(self):
        match self.type_sort_id:
            case ReviewSortType.NEWEST:
                self.query = self.query.order_by(Review.created_at.desc())
            case ReviewSortType.OLDEST:
                self.query = self.query.order_by(Review.created_at.asc())
            case ReviewSortType.MOSTPOSITIVE:
                self.query = self.query.order_by(Review.rating.desc())
            case ReviewSortType.MOSTNEGATIVE:
                self.query = self.query.order_by(Review.rating.asc())