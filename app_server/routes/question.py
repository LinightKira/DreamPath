from http import HTTPStatus

from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import desc

from app_server import db
from app_server.models.question import Question
from app_server.vaildate.vaildate_question import validate_question_data

question_bp = Blueprint('question', __name__)


@question_bp.route('/question', methods=['POST'])
@jwt_required()
def create_question():
    try:
        data = request.get_json()

        # 参数校验
        err = validate_question_data(data)
        # 如果err有内容
        if err is not None:
            return jsonify({"code": HTTPStatus.BAD_REQUEST, "msg": err})
        else:
            question = Question(**data)
            uid = get_jwt_identity()
            question.user_id = uid

            question.create()
            return jsonify({"code": HTTPStatus.OK, "msg": "success", "datas": question.to_dict()})

    except Exception as e:
        db.session.rollback()
        return jsonify({"code": HTTPStatus.INTERNAL_SERVER_ERROR, "msg": str(e)})


@question_bp.route('/question/<int:aid>', methods=['GET'])
@jwt_required()
def get_question(aid):
    try:
        question = Question.query.get(aid)

        if not question or question.status == 0:
            return jsonify({
                "code": HTTPStatus.NOT_FOUND,
                "msg": "question not found."
            })

        data = question.to_dict()

        uid = get_jwt_identity()
        if question.user_id == uid:
            # 可以进行编辑
            data['is_edit'] = True

        return jsonify({
            "code": HTTPStatus.OK,
            "msg": "success",
            "datas": data
        })

    except Exception as e:
        return jsonify({
            "code": HTTPStatus.INTERNAL_SERVER_ERROR,
            "msg": str(e)
        })


@question_bp.route('/question/', methods=['PUT'])
@jwt_required()
def update_question():
    try:
        data = request.get_json()
        aid = data.get('id')
        question = Question.query.get(aid)

        if not question or question.status == 0:
            return jsonify({
                "code": HTTPStatus.NOT_FOUND,
                "msg": "question not found."
            })

        err = ""
        uid = get_jwt_identity()
        if uid != question.user_id:
            err = "uid error."

        if uid != data.get('user_id'):
            err = "user_id error"

        if len(err) != 0:
            return jsonify({"code": HTTPStatus.BAD_REQUEST, "msg": err})

        # 必填校验
        err = validate_question_data(data)
        # 如果err有内容
        if err is not None:
            return jsonify({"code": HTTPStatus.BAD_REQUEST, "msg": err})

        # Exclude create_time and update_time from the update
        data.pop("create_time", None)
        data.pop("update_time", None)

        question.query.filter_by(id=data.pop("id")).update(data)
        db.session.commit()

        return jsonify({
            "code": HTTPStatus.OK,
            "msg": "success",
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"code": HTTPStatus.INTERNAL_SERVER_ERROR, "msg": str(e)})


@question_bp.route('/question/<int:cid>', methods=['DELETE'])
@jwt_required()
def delete_question(aid):
    try:
        question = Question.query.get(aid)
        uid = get_jwt_identity()
        if not question or question.user_id != uid:
            return jsonify({"code": HTTPStatus.FORBIDDEN, "msg": "Permission denied"})

        # 逻辑删除角色
        question.status = 0
        db.session.commit()

        return jsonify({'code': HTTPStatus.OK, 'msg': 'question deleted'})

    except Exception as e:

        db.session.rollback()

        return jsonify({"code": HTTPStatus.INTERNAL_SERVER_ERROR, "msg": str(e)})


@question_bp.route('/questions/<int:tid>', methods=['GET'])
@jwt_required()
def get_questions(tid):
    try:
        uid = get_jwt_identity()
        last_id = request.args.get('last_id')
        page = request.args.get('page', 1, type=int)

        # 查询条件应始终过滤状态
        query = Question.query.filter(Question.theme_id == tid, Question.status > 0)

        # 设置排序方式为id降序
        query = query.order_by(desc(Question.id))

        if last_id:
            # 根据last_id分页
            query = query.filter(Question.id < last_id)
            # 分页
        pagination = query.paginate(page=page, per_page=10)

        question = pagination.items

        return jsonify({
            "code": HTTPStatus.OK,
            "msg": "success",
            "datas": {
                'question': [c.to_dict() for c in question],
                'page': page,
                'total': pagination.pages
            }
        })
    except Exception as e:
        return jsonify({"code": HTTPStatus.INTERNAL_SERVER_ERROR, "msg": str(e)})
