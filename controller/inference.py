from litestar import Controller, post, get, put
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_200_OK
from litestar.params import Body, Parameter
from litestar.di import Provide

from app.Database.connection import get_session
from services.auth_service import auth_service

from langchain_openai import ChatOpenAI
import json
import re
from utils.schema import InferenceModelInput

class InferenceModel(Controller):
    path = "/api"

    @post("/inference")
    async def inference(self, data: InferenceModelInput = Body()) -> dict:
        try:
            llm = ChatOpenAI(
                model="gpt-4o",
                temperature=0.1,
                max_tokens=1500,
                top_p=0.85,
            )

            mbti_types = [
                "INTJ", "INTP", "ENTJ", "ENTP",
                "INFJ", "INFP", "ENFJ", "ENFP",
                "ISTJ", "ISFJ", "ESTJ", "ESFJ",
                "ISTP", "ISFP", "ESTP", "ESFP"
            ]

            plutchik_emotions = [
                "anger", "anticipation", "disgust", "fear",
                "joy", "sadness", "surprise", "trust"
            ]

            prompt = f"""
                Kamu adalah seorang analis kepribadian dan emosi berdasarkan teks.

                Berikut adalah input dari pengguna:
                "{data.text}"

                Berikut adalah catatan riwayat pengguna:
                "{data.history_notes}"

                Tugasmu adalah melakukan dua hal berikut:

                1. Tentukan tipe kepribadian MBTI pengguna yang paling sesuai dari daftar berikut, berdasarkan pola berpikir, ekspresi, dan catatan historis:
                {", ".join(mbti_types)}

                2. Berdasarkan tipe kepribadian MBTI tersebut, analisis bagaimana tipe tersebut biasanya mengekspresikan emosi. Gunakan pemahaman tersebut untuk menafsirkan emosi dominan yang sedang dialami pengguna saat ini berdasarkan ekspresi teks mereka.

                Pilih satu emosi utama dari daftar berikut:
                {", ".join(plutchik_emotions)}

                ⚠️ Catatan penting:
                Jangan menilai emosi hanya dari kata-kata literal dalam input, tetapi sesuaikan juga dengan kecenderungan ekspresif dari tipe kepribadian yang telah kamu identifikasi. Misalnya, tipe INTJ mungkin menunjukkan kesedihan dengan kalimat yang tampak netral, sementara ENFP mungkin menunjukkannya dengan cara yang lebih ekspresif.

                Berikan hasil akhir dalam format JSON **tanpa tambahan penjelasan atau blok markdown**, seperti berikut:
                {{
                "mbti": "<tipe MBTI>",
                "emotion": "<emosi dominan>"
                }}
            """


            response = llm.invoke(prompt)

            try:
                cleaned = re.sub(r"```json|```", "", response.content).strip()

                parsed_result = json.loads(cleaned)

                return {
                    "message": "Analisis berhasil",
                    "data": {
                        "status": 200,
                        "result": parsed_result
                    }
                }

            except json.JSONDecodeError as e:
                return {
                    "message": "Gagal memproses hasil dari LLM",
                    "data": {
                        "status": 500,
                        "error": str(e),
                        "raw_response": response.content
                    }
                }
        except Exception as e:
            return {
                "message": "Terjadi kesalahan saat melakukan inferensi",
                "data": {
                    "status": 500,
                    "error": str(e)
                }
            }