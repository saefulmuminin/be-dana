from flask import jsonify

class Response:
    @staticmethod
    def success(data=None, message="Success", statusCode=200):
        response = {
            "status_code": statusCode,
            "status": "success",
            "message": message
        }
        if data is not None:
            response["data"] = data
        return jsonify(response), statusCode

    @staticmethod
    def error(message="Error", statusCode=400, errors=None):
        response = {
            "status_code": statusCode,
            "status": "error",
            "message": message
        }
        if errors:
            response["errors"] = errors
        return jsonify(response), statusCode
