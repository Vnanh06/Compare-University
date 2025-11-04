import chromadb
from chromadb.utils import embedding_functions
from django.conf import settings
from django.db.models import Avg
from ..models import University, UniversityProgram, Ranking
import google.generativeai as genai
import logging

logger = logging.getLogger(__name__)

class GeminiChatbotRAG:
    """RAG chatbot sử dụng Google Gemini - Hoàn toàn MIỄN PHÍ"""

    def __init__(self):
        # 1. Cấu hình Gemini
        genai.configure(api_key=settings.GEMINI_API_KEY)
        # Sử dụng Gemini 2.5 Flash (mới nhất, FREE)
        self.model = genai.GenerativeModel('models/gemini-2.5-flash')

        # 2. ChromaDB với Sentence Transformers (FREE embedding)
        # Use lighter model: distiluse (220MB) vs MiniLM-L12 (420MB)
        self.client = chromadb.PersistentClient(path="./chromadb_data")
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="distiluse-base-multilingual-cased-v2"  # 50% lighter, still multilingual
        )

        # 3. Tạo collection
        try:
            self.collection = self.client.get_collection(
                name="universities_gemini",
                embedding_function=self.embedding_fn
            )
            logger.info("Đã tải collection có sẵn")
        except:
            self.collection = self.client.create_collection(
                name="universities_gemini",
                embedding_function=self.embedding_fn
            )
            self._build_initial_data()

    def _build_initial_data(self):
        """Tạo dữ liệu vector lần đầu"""
        logger.info("Đang tạo vector database...")

        universities = University.objects.select_related('country').all()  # LẤY TẤT CẢ

        documents = []
        metadatas = []
        ids = []

        for uni in universities:
            # Lấy thông tin
            programs = uni.universityprogram_set.all()[:5]
            majors = ", ".join([p.major.name for p in programs if p.major])
            ranking = uni.ranking_set.order_by('-fyear').first()
            avg_tuition = uni.universityprogram_set.aggregate(
                avg_fee=Avg('tuition_fee')
            )['avg_fee']

            # Tạo document text
            doc = f"""
            Tên trường: {uni.name}
            Tên viết tắt: {uni.short_name or 'N/A'}
            Quốc gia: {uni.country.name if uni.country else 'Không xác định'}
            Mô tả: {uni.description or 'Chưa có mô tả'}
            Chuyên ngành đào tạo: {majors or 'Chưa cập nhật'}
            Xếp hạng thế giới: {ranking.frank if ranking else 'Chưa có xếp hạng'}
            Nguồn xếp hạng: {ranking.ranking_sources.name if ranking and ranking.ranking_sources else 'N/A'}
            Năm thành lập: {uni.founded_year or 'Không rõ'}
            Học phí trung bình: {f'${avg_tuition:,.0f}/năm' if avg_tuition else 'Chưa có thông tin'}
            Website: {uni.website or 'Chưa có'}
            """

            documents.append(doc)
            metadatas.append({
                'name': uni.name,
                'country': uni.country.name if uni.country else 'Unknown',
                'id': uni.id,
                'ranking': ranking.frank if ranking else 9999
            })
            ids.append(f"uni_{uni.id}")

        # Thêm vào ChromaDB
        if documents:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Đã tạo embeddings cho {len(documents)} trường đại học")

    def chat(self, user_message: str) -> str:
        """
        Hàm chính - Nhận câu hỏi, trả về câu trả lời

        Args:
            user_message: Câu hỏi của người dùng

        Returns:
            Câu trả lời từ Gemini dựa trên dữ liệu DB
        """
        try:
            # 1. Tìm kiếm semantic trong vector DB
            results = self.collection.query(
                query_texts=[user_message],
                n_results=5
            )

            # 2. Lấy thông tin chi tiết từ SQL Database
            context = ""
            universities_found = []

            if results['ids'] and results['ids'][0]:
                uni_ids = [meta['id'] for meta in results['metadatas'][0]]
                universities = University.objects.filter(
                    id__in=uni_ids
                ).select_related('country').prefetch_related(
                    'ranking_set__ranking_sources',
                    'universityprogram_set__major',
                    'universityprogram_set__program'
                )

                for uni in universities:
                    # Xếp hạng
                    ranking = uni.ranking_set.order_by('-fyear').first()

                    # Chương trình học
                    programs = uni.universityprogram_set.all()[:3]
                    program_details = []
                    for prog in programs:
                        if prog.major and prog.program:
                            fee_str = f"${prog.tuition_fee:,.0f}/năm" if prog.tuition_fee else "N/A"
                            program_details.append(
                                f"{prog.major.name} ({prog.program.level}): {fee_str}"
                            )

                    # Yêu cầu tuyển sinh
                    requirements = uni.universityadmissionrequirement_set.all()[:3]
                    req_details = []
                    for req in requirements:
                        if req.criteria:
                            req_details.append(f"{req.criteria.name}: {req.value}")

                    context += f"""
========================================
TRƯỜNG: {uni.name}
========================================
Quốc gia: {uni.country.name if uni.country else 'N/A'}
Xếp hạng thế giới: #{ranking.frank if ranking else 'N/A'} ({ranking.ranking_sources.name if ranking and ranking.ranking_sources else 'N/A'})
Năm thành lập: {uni.founded_year or 'N/A'}
Website: {uni.website or 'N/A'}

Chương trình đào tạo:
{chr(10).join(['  - ' + p for p in program_details]) if program_details else '  Chưa có thông tin'}

Yêu cầu tuyển sinh:
{chr(10).join(['  - ' + r for r in req_details]) if req_details else '  Chưa có thông tin'}

Mô tả: {(uni.description or 'Chưa có mô tả')[:200]}...

"""
                    universities_found.append(uni.name)

            # 3. Kiểm tra có dữ liệu không
            if not context.strip():
                return """
Xin lỗi, tôi không tìm thấy thông tin liên quan trong cơ sở dữ liệu.

Gợi ý:
- Thử hỏi về trường cụ thể (VD: "Thông tin về MIT")
- Hỏi về chuyên ngành (VD: "Trường nào tốt cho Computer Science?")
- Hỏi về quốc gia (VD: "Các trường đại học ở Mỹ")
"""

            # 4. Tạo prompt cho Gemini
            prompt = f"""
Bạn là trợ lý tư vấn giáo dục thông minh, chuyên về các trường đại học trên thế giới.

DỮ LIỆU CÁC TRƯỜNG LIÊN QUAN:
{context}

CÂU HỎI CỦA NGƯỜI DÙNG:
{user_message}

YÊU CẦU TRẢ LỜI:
1. Trả lời bằng tiếng Việt có dấu, rõ ràng, dễ hiểu
2. CHỈ sử dụng thông tin từ dữ liệu trên, KHÔNG bịa thêm
3. Nếu thiếu thông tin, nói rõ "Chưa có dữ liệu về..."
4. Trình bày có cấu trúc, dễ đọc (dùng bullet points nếu cần)
5. Nếu người dùng hỏi so sánh, hãy so sánh chi tiết các tiêu chí
6. Đề xuất xem thêm website chính thức nếu cần thông tin chi tiết hơn

Hãy trả lời một cách chuyên nghiệp và hữu ích!
"""

            # 5. Gọi Gemini API (FREE)
            response = self.model.generate_content(prompt)
            answer = response.text

            # 6. Thêm thông tin tham khảo
            footer = f"\n\n📚 Thông tin dựa trên: {', '.join(universities_found[:3])}"
            if len(universities_found) > 3:
                footer += f" và {len(universities_found) - 3} trường khác"

            return answer + footer

        except Exception as e:
            logger.error(f"Lỗi chatbot Gemini: {str(e)}")
            return f"""
Xin lỗi, có lỗi xảy ra khi xử lý câu hỏi của bạn.

Chi tiết lỗi: {str(e)}

Vui lòng thử lại hoặc liên hệ quản trị viên nếu lỗi vẫn tiếp tục.
"""

    def get_suggestions(self) -> list:
        """Trả về danh sách câu hỏi gợi ý"""
        return [
            "Trường nào tốt cho Computer Science?",
            "So sánh MIT và Stanford",
            "Các trường đại học ở Mỹ xếp hạng cao",
            "Học phí trung bình của các trường top 10",
            "Trường nào có chương trình AI/Machine Learning?",
            "Yêu cầu tuyển sinh vào Harvard"
        ]

    def rebuild_database(self):
        """Xóa và tái tạo lại vector database (khi có dữ liệu mới)"""
        try:
            # Xóa collection cũ
            self.client.delete_collection(name="universities_gemini")
            logger.info("Đã xóa collection cũ")

            # Tạo collection mới
            self.collection = self.client.create_collection(
                name="universities_gemini",
                embedding_function=self.embedding_fn
            )

            # Build lại data
            self._build_initial_data()
            logger.info("Đã rebuild vector database thành công")
            return True
        except Exception as e:
            logger.error(f"Lỗi khi rebuild database: {str(e)}")
            return False

    def get_stats(self):
        """Lấy thống kê về vector database"""
        try:
            count = self.collection.count()
            return {
                'total_universities': count,
                'collection_name': 'universities_gemini',
                'embedding_model': 'distiluse-base-multilingual-cased-v2'
            }
        except Exception as e:
            logger.error(f"Lỗi khi lấy thống kê: {str(e)}")
            return None
