import requests
from bs4 import BeautifulSoup
from openai import OpenAI

# ==========================================
# 1. Comment 클래스 (데이터 담당)
# ==========================================
class Comment:
    def __init__(self, original_text):
        self.original_text = original_text
        self.sanitized_text = None
        self.is_dirty = False

    def update_sanitized_text(self, clean_text):
        self.sanitized_text = clean_text
        self.is_dirty = (self.original_text != self.sanitized_text)

    def display(self):
        status = "[⚠️ 순화됨]" if self.is_dirty else "[✅ 깨끗함]"
        print(f"{status} 원문: {self.original_text} -> 순화: {self.sanitized_text}")


# ==========================================
# 2. CommentCrawler 클래스 (크롤링 담당) - NEW!
# ==========================================
class CommentCrawler:
    def __init__(self):
        # 봇(Bot)으로 오해받아 차단당하지 않도록 브라우저 정보(Headers) 설정
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def fetch_comments(self, url):
        """
        특정 URL에서 댓글 데이터를 크롤링해 리스트로 반환하는 함수
        (※ 아래 코드는 예시 사이트 구조 기준이며, 실제 타겟 사이트의 태그에 맞게 수정해야 합니다)
        """
        collected_comments = []
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 예시: 커뮤니티의 댓글 HTML 태그가 <span class="reply-content">일 경우
                reply_tags = soup.find_all("span", class_="reply-content")
                
                # 만약 태그를 찾았다면 텍스트만 추출
                for tag in reply_tags:
                    collected_comments.append(tag.text.strip())
                
                # 임시 테스트용 데이터 (크롤링 대상 사이트에 댓글이 없을 때를 대비한 가짜 데이터)
                if not collected_comments:
                    collected_comments = [
                        "진짜 무대 개판이네 연습 좀 해라 짜증나게",
                        "와 외모 미쳤다 존나 잘생겼네 진짜",
                        "오늘 노래방 라이브 좋았어요 응원합니다!"
                    ]
            return collected_comments
        except Exception as e:
            print(f"❌ 크롤링 중 오류 발생: {e}")
            return []


# ==========================================
# 3. AISanitizer 클래스 (AI 통신 담당)
# ==========================================
class AISanitizer:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)
        self.system_instruction = (
            "당신은 아이돌 커뮤니티의 친절한 댓글 관리자입니다. "
            "비속어나 공격성이 있다면 문맥을 살려 부드럽게 순화하고, 문제가 없다면 원문을 그대로 출력하세요."
        )

    def sanitize(self, text):
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": self.system_instruction},
                    {"role": "user", "content": f"댓글: {text}"}
                ],
                temperature=0.3,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"[에러]: {e}"


# ==========================================
# 4. CommentManager 클래스 (전체 흐름 제어)
# ==========================================
class CommentManager:
    def __init__(self, crawler, sanitizer):
        self.crawler = crawler        # 크롤러 객체 주입
        self.sanitizer = sanitizer    # AI 엔진 객체 주입
        self.comments = []            # Comment 객체들을 저장할 리스트

    def collect_and_process(self, target_url):
        """크롤링부터 순화까지 한 번에 처리하는 메인 프로세스"""
        print(f"🌐 {target_url} 에서 댓글 수집 중...")
        raw_comments = self.crawler.fetch_comments(target_url)
        
        # 1. 수집한 문자열을 Comment 객체로 만들어 리스트에 저장
        for text in raw_comments:
            self.comments.append(Comment(text))
            
        # 2. AI 순화 진행
        print("🔄 AI 비속어 순화 작업 시작...")
        for comment in self.comments:
            clean_text = self.sanitizer.sanitize(comment.original_text)
            comment.update_sanitized_text(clean_text)
            
        # 3. 결과 출력
        print("\n=== ✨ 모니터링 및 순화 완료 결과 ===")
        for comment in self.comments:
            comment.display()


# ==========================================
# 🚀 시스템 실행
# ==========================================
if __name__ == "__main__":
    API_KEY = "YOUR_OPENAI_API_KEY"
    TARGET_URL = "https://example-idol-community.com/post/123" # 크롤링할 대상 주소
    
    # 각각의 클래스 객체 생성
    crawler_instance = CommentCrawler()
    sanitizer_instance = AISanitizer(api_key=API_KEY)
    
    # 매니저에게 크롤러와 AI를 쥐어주고 가동
    manager = CommentManager(crawler=crawler_instance, sanitizer=sanitizer_instance)
    manager.collect_and_process(TARGET_URL)