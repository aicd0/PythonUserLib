from typing import Any

last_text_length = 0

def put(obj: Any, end: str='\n', same_line: bool=False):
    global last_text_length
    text = str(obj)
    text_length = len(text)
    space_count = max(0, last_text_length - text_length)
    text += ' ' * space_count

    if same_line:
        end = end.replace('\n', '')
        last_text_length = text_length
        print(text, end=end + '\r')
    else:
        last_text_length = 0
        print(text, end=end)