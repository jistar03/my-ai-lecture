import streamlit as st
import whisper
import google.generativeai as genai
from pypdf import PdfReader
import io

# 1. 페이지 기본 설정
st.set_page_config(page_title="슈퍼 학습 비서", page_icon="📝", layout="wide")
st.title("🎓 AI 통합 학습 지원 시스템")

# 2. 사이드바 설정 (API 키 및 퀴즈 개수)
with st.sidebar:
    st.header("⚙️ 설정")
    api_key = st.secrets["AIzaSyBcJYAt867C5FSKtFcJthT24puFHKnt1MA"]
    st.divider()
    quiz_count = st.slider("생성할 퀴즈 개수", 5, 50, 10)
    st.info("퀴즈 개수가 많을수록 생성 시간이 조금 더 걸릴 수 있습니다.")

# 3. 메인 탭 구성
tab1, tab2 = st.tabs(["📄 파일 업로드 및 요약", "🧠 퀴즈 생성기"])

# 세션 상태 초기화 (요약 내용을 저장하기 위함)
if "summary_text" not in st.session_state:
    st.session_state.summary_text = ""

with tab1:
    st.subheader("📁 강의 자료 올리기")
    uploaded_file = st.file_uploader("녹음 파일(mp3, wav) 또는 PDF 파일을 올려주세요.", type=['mp3', 'wav', 'm4a', 'pdf'])

    if uploaded_file is not None and api_key:
        if st.button("🚀 분석 및 요약 시작"):
            with st.spinner("내용을 분석하고 요약 리포트를 작성 중입니다..."):
                full_text = ""
                
                # PDF 파일 처리
                if uploaded_file.type == "application/pdf":
                    reader = PdfReader(uploaded_file)
                    for page in reader.pages:
                        full_text += page.extract_text()
                
                # 음성 파일 처리
                else:
                    with open("temp_audio", "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    model = whisper.load_model("base")
                    result = model.transcribe("temp_audio")
                    full_text = result["text"]

                # Gemini를 이용한 요약
                genai.configure(api_key=api_key)
                ai_model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = f"""
                다음 자료를 바탕으로 전문적인 학습 요약본을 만들어줘. 
                의학 및 물리치료 전공 용어는 정확하게 교정하고, 핵심 개념과 임상 적용점을 중심으로 정리해줘.
                자료 내용: {full_text}
                """
                response = ai_model.generate_content(prompt)
                st.session_state.summary_text = response.text
                
                st.success("✅ 분석 완료!")
                st.markdown(st.session_state.summary_text)

with tab2:
    st.subheader("📝 맞춤형 자가 테스트")
    if not st.session_state.summary_text:
        st.warning("먼저 [파일 업로드 및 요약] 탭에서 자료를 요약해 주세요.")
    else:
        if st.button(f"🔥 새로운 퀴즈 {quiz_count}개 만들기"):
            with st.spinner("중복되지 않는 새로운 문제를 출제 중입니다..."):
                genai.configure(api_key=api_key)
                ai_model = genai.GenerativeModel('gemini-1.5-flash')
                
                # '새로운 문제'를 강조하는 프롬프트
                quiz_prompt = f"""
                다음 요약본을 바탕으로 중복되지 않는 새로운 객관식 퀴즈 {quiz_count}문제를 만들어줘.
                이전과는 다른 세부적인 개념이나 사례 중심의 문제를 출제해줘.
                각 문제 뒤에는 정답과 상세한 해설을 포함해줘.
                
                [학습 요약본]
                {st.session_state.summary_text}
                """
                quiz_response = ai_model.generate_content(quiz_prompt)
                st.markdown(quiz_response.text)
