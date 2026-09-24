import re,unicodedata
class EngineReframer:
    def reframe_input(self,raw_prompt):
        text=unicodedata.normalize('NFKC',raw_prompt)
        text=re.sub(r'[ \t]+',' ',text).strip()
        if len(text)<8:raise ValueError('Describe the app in at least eight characters')
        return text
