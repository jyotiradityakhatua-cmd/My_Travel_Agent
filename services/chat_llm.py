from app.llm.llm_client import generate_full
 
 
def run_chat_llm(ctx, user_query):
    messages = [
        {
            "role": "system",
            "content": f"""
Current Trip Context
 
Intent: {ctx.intent}
Source: {ctx.source}
Destination: {ctx.destination}
Departure Date: {ctx.departure_date}
Return Date: {ctx.return_date}
Days: {ctx.days}
 
Use existing values.
Never ask again for values already known.
"""
        },
        {
            "role": "user",
            "content": user_query
        }
    ]
 
    return generate_full(messages)