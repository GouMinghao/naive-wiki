def matchcase(word):
    def replace(m):
        text = m.group()
        if text.isupper():
            return '<em><font color="red">{}</font></em>'.format(word.upper())
        elif text.islower():
            return '<em><font color="red">{}</font></em>'.format(word.lower())
        elif text[0].isupper():
            return '<em><font color="red">{}</font></em>'.format(word.capitalize())
        else:
            return '<em><font color="red">{}</font></em>'.format(word)
    return replace


import re
s = 'Social History'
s=re.sub('history', matchcase('history'), s, flags=re.IGNORECASE)
print(s)