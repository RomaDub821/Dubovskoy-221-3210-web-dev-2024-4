from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import desc
from sqlalchemy.exc import IntegrityError
from models import db, Course, Category, User, Review, REVIEW_GRADES
from tools import CoursesFilter, ImageSaver, ReviewsFilter, ReviewSortType

bp = Blueprint('courses', __name__, url_prefix='/courses')

COURSE_PARAMS = [
    'author_id', 'name', 'category_id', 'short_desc', 'full_desc'
]


def params():
    return {p: request.form.get(p) or None for p in COURSE_PARAMS}


def search_params():
    return {
        'name': request.args.get('name'),
        'category_ids': [x for x in request.args.getlist('category_ids') if x],
    }


@bp.route('/')
def index():
    courses = CoursesFilter(**search_params()).perform()
    pagination = db.paginate(courses)
    courses = pagination.items
    categories = db.session.execute(db.select(Category)).scalars()
    return render_template('courses/index.html',
                           courses=courses,
                           categories=categories,
                           pagination=pagination,
                           search_params=search_params())


@bp.route('/new')
@login_required
def new():
    course = Course()
    categories = db.session.execute(db.select(Category)).scalars()
    users = db.session.execute(db.select(User)).scalars()
    return render_template('courses/new.html',
                           categories=categories,
                           users=users,
                           course=course)


@bp.route('/create', methods=['POST'])
@login_required
def create():
    f = request.files.get('background_img')
    img = None
    course = Course()
    try:
        if f and f.filename:
            img = ImageSaver(f).save()

        image_id = img.id if img else None
        course = Course(**params(), background_image_id=image_id)
        db.session.add(course)
        db.session.commit()
    except IntegrityError as err:
        flash(f'Возникла ошибка при записи данных в БД. Проверьте корректность введённых данных. ({err})', 'danger')
        db.session.rollback()
        categories = db.session.execute(db.select(Category)).scalars()
        users = db.session.execute(db.select(User)).scalars()
        return render_template('courses/new.html',
                               categories=categories,
                               users=users,
                               course=course)

    flash(f'Курс {course.name} был успешно добавлен!', 'success')

    return redirect(url_for('courses.index'))


@bp.route('/<int:course_id>')
def show(course_id):
    course = db.get_or_404(Course, course_id)
    reviews = db.session.execute(
        db.select(Review).filter_by(course_id=course_id).order_by(desc(Review.created_at)).limit(5)).scalars().all()
    user_review = db.session.execute(
        db.select(Review).filter_by(course_id=course_id, user_id=current_user.id)).scalar_one_or_none()

    return render_template('courses/show.html', course=course, reviews=reviews, user_review=user_review, grades=REVIEW_GRADES)


def reviews_search_params(course_id):
    return {
        "course_id": course_id,
        "type_sort": request.args.get("type_sort"),
    }


@bp.route('/<int:course_id>/reviews')
def reviews(course_id):
    course = db.get_or_404(Course, course_id)
    type_sort = request.args.get("type_sort")
    type_sort_id = ReviewSortType.NEWEST
    if type_sort is not None and type_sort != "":
        type_sort_id = ReviewSortType.get_by_value(int(type_sort))
    reviews = ReviewsFilter(course_id=course_id, type_sort_id=type_sort_id).perform()
    pagination = db.paginate(reviews)
    reviews = pagination.items
    user_review = db.session.execute(
        db.select(Review).filter_by(course_id=course_id, user_id=current_user.id)).scalar_one_or_none()
    return render_template('reviews/index.html',
                           reviews=reviews,
                           course=course,
                           sort_types=list(ReviewSortType),
                           user_review=user_review,
                           search_params=reviews_search_params(course.id),
                           grades=REVIEW_GRADES,
                           pagination=pagination
                           )


REVIEW_PARAMS = ["user_id", "rating", "text", "course_id"]


def create_review_params():
    return {p: request.form.get(p) or None for p in REVIEW_PARAMS}


@bp.route('/<int:course_id>/review/create', methods=["POST"])
@login_required
def create_review(course_id):
    review = Review(**create_review_params())
    try:
        db.session.add(review)
        course = db.get_or_404(Course, course_id)
        course.rating_num += 1
        course.rating_sum += int(review.rating)
        db.session.commit()
    except IntegrityError as err:
        flash(f'Возникла ошибка при записи данных в БД. Проверьте корректность введённых данных. ({err})', 'danger')
        db.session.rollback()
        course = db.get_or_404(Course, course_id)
        reviews = db.session.execute(
            db.select(Review).filter_by(course_id=course_id).order_by(desc(Review.created_at)).limit(5)).scalars().all()
        return render_template('courses/show.html',
                               course=course,
                               reviews=reviews,
                               user_review=review,
                               grades=REVIEW_GRADES,
                               )

    flash(f'Отзыв был успешно добавлен!', 'success')

    return redirect(url_for('courses.show', course_id=course_id))