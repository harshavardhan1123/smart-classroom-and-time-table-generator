import os
import requests
import json

def call_claude(system_prompt, messages, max_tokens=1000):
    api_key = os.environ.get('OPENROUTER_API_KEY')
    if not api_key:
        return {"error": "OpenRouter API key missing in .env"}
    
    # OpenRouter expects the system prompt as a message with role 'system'
    formatted_messages = [{"role": "system", "content": system_prompt}] + messages

    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:5000",
                "X-Title": "UniSchedule"
            },
            data=json.dumps({
                "model": "anthropic/claude-3.7-sonnet",
                "messages": formatted_messages,
                "max_tokens": max_tokens
            }),
            timeout=30
        )
        
        result = response.json()
        if "error" in result:
            return {"error": result["error"].get("message", "Unknown OpenRouter error")}
            
        return {"reply": result["choices"][0]["message"]["content"]}
    except Exception as e:
        return {"error": str(e)}

def format_timetable_for_prompt(entries):
    if not entries:
        return "No classes scheduled."
    
    lines = []
    for e in entries:
        faculty_name = e.faculty.name if e.faculty else "N/A"
        course_name = e.course.name if e.course else "N/A"
        room = e.room.room_number if e.room else "N/A"
        lines.append(f"- {e.day} {e.timeslot}: {course_name} ({e.course.code}) by {faculty_name} in Room {room}")
    return "\n".join(lines)

def format_attendance_for_prompt(attendance_summary):
    # attendance_summary is expected to be a list of dicts: 
    # [{"course": "CSE101", "percent": 85.5, "held": 10}, ...]
    if not attendance_summary:
        return "No attendance records found."
    
    lines = []
    for item in attendance_summary:
        status = " (BELOW 75%!)" if item['percent'] < 75 else ""
        lines.append(f"- {item['course']}: {item['percent']:.1f}% ({item['held']} sessions){status}")
    return "\n".join(lines)
