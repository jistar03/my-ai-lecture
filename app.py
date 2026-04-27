import streamlit as st
import whisper
import os

# 페이지 설정
st.set_page_config(page_title="강의 기록기", page_icon="🎤")
st.title("🎤 강의 소리 -> 텍스트 변환기")
st.write("녹음 파일을 올리면 인공지능이 그대로 글자로 적어줍니다.")

# 파일 업로더 (오디오만)
uploaded_file = st.file_uploader("녹음 파일(mp3, wav, m4a)을 선택하세요.", type=['mp3', 'wav', 'm4a'])

if uploaded_file is not None:
    st.audio(uploaded_file) # 올린 파일 들어보기
    
    if st.button("📝 글자로 바꾸기 시작"):
        with st.spinner("AI가 열심히 듣고 적는 중입니다... 잠시만 기다려주세요."):
            try:
                # 임시 파일 저장
                with open("temp_audio", "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Whisper 모델 로드 (가장 가벼운 base 모델 사용)
                model = whisper.load_model("base")
                
                # 받아쓰기 시작
                result = model.transcribe("temp_audio")
                extracted_text = result["text"]
                
                # 결과 출력
                st.success("✅ 변환 완료!")
                st.text_area("추출된 내용", extracted_text, height=400)
                
                # 메모장 파일로 다운로드 버튼
                st.download_button(
                    label="💾 메모장 파일로 저장",
                    data=extracted_text,
                    file_name="강의기록.txt",
                    mime="text/plain"
                )
                
                # 임시 파일 삭제
                os.remove("temp_audio")
                
            except Exception as e:
                st.error(f"변환 중 오류가 발생했습니다: {e}")
