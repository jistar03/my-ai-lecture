import streamlit as st
import whisper
import google.generativeai as genai
import os

# 1. 화면 구성
st.set_page_config(page_title="나의 AI 강의 비서", page_icon="🎓")
st.title("🎓 스마트 강의 요약 서비스")
st.write("스마트폰으로 녹음한 파일을 올리면 AI가 요약해 드립니다.")

# 2. 설정 (API 키 입력)
with st.sidebar:
    st.header("설정")
    api_key = st.text_input("Gemini API Key", type="password")
    st.info("실습 중에도 틈틈이 활용해 보세요! 💪")

# 3. 파일 업로드 부품
uploaded_file = st.file_uploader("녹음 파일 선택 (mp3, m4a, wav 등)", type=['mp3', 'm4a', 'wav'])

if uploaded_file is not None:
    if not api_key:
        st.error("왼쪽 사이드바에 API 키를 입력해 주세요!")
    else:
        if st.button("📝 요약 시작하기"):
            with st.spinner("AI가 녹음 내용을 분석하고 있습니다..."):
                # 임시 파일 저장
                with open("temp_audio", "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Whisper 실행 (음성 -> 글자)
                model = whisper.load_model("base")
                result = model.transcribe("temp_audio")
                script = result["text"]
                
                # Gemini 실행 (요약)
                genai.configure(api_key=api_key)
                ai_model = genai.GenerativeModel('gemini-1.5-flash')
                prompt = f"다음 강의 내용을 전문 용어를 살려 핵심 위주로 요약해줘: {script}"
                response = ai_model.generate_content(prompt)
                
                # 결과 출력
                st.success("✅ 요약 완료!")
                st.markdown("### 📋 요약 리포트")
                st.info(response.text)