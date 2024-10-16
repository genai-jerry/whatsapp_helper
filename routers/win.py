from datetime import datetime
from flask import Blueprint, request, jsonify, render_template
from flask_login import current_user, login_required

from store.win_store import get_all_wins_for_date, store_win, get_win_types

win_blueprint = Blueprint('win', __name__)

@win_blueprint.route('/', methods=['GET'])
@login_required
def get_wins():
    current_date = datetime.now().strftime('%Y-%m-%d')
    wins = get_all_wins_for_date(current_date)
    return render_template('review/_wins.html', wins=wins)

@win_blueprint.route('/', methods=['POST'])
@login_required
def create_new_win():
    data = request.form
    win_type = data.get('win_type')
    description = data.get('description')
    current_date = datetime.now().strftime('%Y-%m-%d')
    store_win(current_date, current_user.id, win_type, description)
    return jsonify({'message': 'Win created successfully'}), 201

@win_blueprint.route('/types', methods=['GET'])
@login_required
def get_all_win_types():
    win_types = get_win_types()
    return jsonify(win_types)
