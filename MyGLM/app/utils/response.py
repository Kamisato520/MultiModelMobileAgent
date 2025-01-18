from flask import jsonify

def success_response(data=None, message="Success"):
    response = {
        "success": True,
        "message": message
    }
    if data is not None:
        response["data"] = data
    return jsonify(response)

def error_response(message="Error", code=400):
    return jsonify({
        "success": False,
        "message": message
    }), code

def validation_error(errors):
    return jsonify({
        "success": False,
        "message": "Validation error",
        "errors": errors
    }), 422
