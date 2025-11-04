# from dotenv import load_dotenv
# load_dotenv()   # .env 내용을 읽어서 환경변수로 설정

# streamlit-cloud에서는 .env를 사용할 수 없으므로, 
# secrets 설정 (TOML 방식)에 OPEN_API_KEY를 설정해야 한다.
# OPEN_API_KEY="api키 입력" (토글 방식) 

from openai import OpenAI
import os
import base64

client = OpenAI()   # secrets 설정 시 정상적으로 작동

def stt(audio):
    # 파일로 변환
    filename = 'prompt.mp3'   # 저장되는 것이 아닌 메모리상 파일(임시 mp3파일로 변환)
    audio.export(filename, format='mp3')

    # whisper-1 모델로 stt
    with open(filename, 'rb') as f:
        transcription = client.audio.transcriptions.create(
            model='whisper-1',
            file=f
        )

    # 음원파일 삭제
    os.remove(filename)         # 이미 추출이 되어있기 때문에 파일은 삭제
    return transcription.text   # 텍스트만 반환

def ask_gpt(messages, model):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=1,
        top_p=1,
        max_tokens=4096
    )
    return response.choices[0].message.content

def tts(response):   # GPT 응답 전달
    filename = 'voice.mp3'
    with client.audio.speech.with_streaming_response.create(   # tts 작업
        model='tts-1',
        voice='nova',
        input=response
    ) as stream:
        stream.stream_to_file(filename)   # tts 작업된 파일

    # 음원을 base64 문자열로 인코딩
    with open(filename, 'rb') as f:   # 이진 데이터
        data = f.read()
        base64_encoded = base64.b64encode(data).decode() # 텍스트로 나올 수 있도록 디코딩

    # 음원 파일 삭제
    os.remove(filename)
    return base64_encoded