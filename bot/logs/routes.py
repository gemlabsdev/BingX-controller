from ..logs import bp


@bp.route('/logs', methods=['GET'])
def get_logs():
    with open('logs.log', 'r') as f:
        logs = f.read()
    return logs


@bp.route('/logs', methods=['DELETE'])
def delete_logs():
    with open('logs.log', 'w') as f:
        f.close()
    return {'status': 'DELETED'}
