async def validate_request(request: dict) -> dict:
    user_id = "anonymous"
    if "user_query" not in request or not request.get("user_query"):
        return {"error": "You need to provide me something you want me to help with!"}
    
    session_context = request.get("session_context")
    if session_context and 'user' in session_context and 'id' in session_context.get('user', {}):
        user_id = session_context['user']['id']
    else:
        # This logic can be adjusted based on whether an anonymous user is allowed
        pass

    user_query = {
        "id": user_id,
        "request": request["user_query"]
    }
    return user_query