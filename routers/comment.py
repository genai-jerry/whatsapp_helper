from flask import Blueprint, render_template, request, jsonify, abort
from flask_login import login_required, current_user
from store.comments_store import *

comment_blueprint = Blueprint('comment', __name__)

@comment_blueprint.route('/')
@login_required
def get_comments_api():
    opportunity_id = request.args.get("opportunity_id")
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))
    if opportunity_id:
        comments, total_comments = get_comments_for_opportunity(opportunity_id, page, per_page)
        return jsonify({
            "comments": comments,
            "total_comments": total_comments,
            "page": page,
            "per_page": per_page
        })
    else:
        abort(400, description="Opportunity ID is required")

@comment_blueprint.route('/create', methods=['GET'])
@login_required
def get_create_comment_modal_api():
    opportunity_id = request.args.get("opportunity_id")
    return render_template('comment/comment_modals.html', opportunity_id=opportunity_id)

@comment_blueprint.route('/', methods=['POST'])
@login_required
def create_comment_api():
    opportunity_id = request.form.get("opportunity_id")
    content = request.form.get("content")
    
    if not opportunity_id or not content:
        abort(400, description="Opportunity ID and content are required")
    
    success = create_comment(opportunity_id, content, current_user.id)
    
    if success:
        return jsonify({"message": "Comment created successfully"}), 201
    else:
        abort(500, description="Failed to create comment")
