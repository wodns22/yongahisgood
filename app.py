import streamlit as st
import google.generativeai as genai
import os

# 1. API 키 설정 (보안을 위해 스트림릿 시스템 설정에서 불러옵니다)
# 로컬 테스트 시에는 직접 입력하거나 환경변수를 세팅해야 합니다.
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    # 만약 배포 설정 전이라면 웹 화면에서 직접 입력할 수 있는 임시 창을 띄웁니다.
    api_key = st.sidebar.text_input("Gemini API Key", type="password")

if api_key:
    genai.configure(api_key=api_key)
else:
    st.warning("API 키가 설정되지 않았습니다. 사이트 관리자 설정을 확인하거나 왼쪽 사이드바에 API 키를 입력해 주세요.")

# 사용할 AI 모델 설정 (빠르고 안정적인 gemini-1.5-flash 추천)
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. 웹페이지 UI 디자인
st.set_page_config(page_title="교사 인수인계 AI 조수", page_icon="📋", layout="centered")

st.title("📋 학년 말/학기 초 교사 인수인계서 생성기")
st.write("선생님의 담당 업무에 맞게 아래 내용을 자유롭게 **수정**하신 후, 하단의 **[인수인계서 생성]** 버튼을 눌러주세요.")
st.markdown("---")

# 3. 선생님들이 웹페이지에서 직접 고칠 수 있는 입력창들
st.subheader("🔍 업무 및 학급 정보 수정")

# 행 구조로 깔끔하게 배치하기 위해 columns 활용
col1, col2 = st.columns(2)
with col1:
    grade_info = st.text_input("담당 학년 및 교과", value="2학년 과학")
with col2:
    duty_info = st.text_input("담당 업무 (행정)", value="AI 자율동아리 지도, 에듀테크 정산")

col3, col4 = st.columns(2)
with col3:
    student_count = st.number_input("학급 학생 수 (명)", min_value=0, max_value=50, value=28)
with col4:
    class_atmosphere = st.text_input("학급/동아리 전반적 분위기", value="남학생 위주, 활동적이고 긍정적임")

st.subheader("💡 세부 인수인계 사항")
key_notes = st.text_area(
    "다음 선생님께 꼭 전달해야 할 내용을 자유롭게 수정/추가하세요:", 
    value="- 2학기 MBL(컴퓨터 기반) 실험 장비 세팅 및 관리 요령 확인 필요\n- AI 선도학교 예산 집행 관련 기안문 및 정산서 위치 인계\n- 신임 원어민/교생 선생님 방문 시 래포 형성을 위한 아이스브레이킹 미션 팁 전달 예정",
    height=150
)

st.markdown("---")

# 4. 실행 버튼 및 AI 작동
if st.button("✨ 이 내용으로 인수인계서 생성하기", use_container_width=True):
    if not api_key:
        st.error("API Key가 없어 인수인계서를 생성할 수 없습니다.")
    else:
        # 개발자가 미리 심어놓은 고정 프롬프트 (선생님들에겐 보이지 않고 입력값만 조합됨)
        system_prompt = f"""
        당신은 학교 행정 및 학급 경영 전문가이자 베테랑 교사입니다. 
        선생님이 제공한 다음 정보를 바탕으로, 후임 교사가 다음 학기에 업무를 착오 없이 
        즉시 파악하고 수행할 수 있도록 전문적이고 깔끔한 형태의 '교사 업무 인수인계서'를 작성해 주세요.
        
        [교사가 수정한 기본 정보]
        - 담당 학년/교과: {grade_info}
        - 담당 행정 업무: {duty_info}
        - 학생 수 및 분위기: {student_count}명 / {class_atmosphere}
        
        [교사가 수정한 세부 전달 사항]
        {key_notes}
        
        [작성 지침]
        1. 개조식(문장 명사형 마감)과 표 등을 적절히 섞어 가독성을 극대화할 것.
        2. 공문서처럼 깔끔하고 격식 있는 어조를 사용할 것.
        3. '학급 경영', '행정 업무', '기타 특이사항 및 팁'으로 섹션을 명확히 나눌 것.
        """
        
        with st.spinner("AI가 입력하신 내용을 바탕으로 인수인계서를 정밀 작성 중입니다..."):
            try:
                response = model.generate_content(system_prompt)
                
                st.success("🎉 인수인계서 초안 생성이 완료되었습니다!")
                
                # 결과 출력 창
                st.subheader("📌 생성된 인수인계서 내용")
                st.text_area("결과 복사하기", value=response.text, height=400)
                
                st.balloons() # 성공 축하 효과
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}\n구글 AI 스튜디오의 무료 티어 제한(RPM)에 도달했을 수 있으니 잠시 후 다시 시도해 주세요.")
