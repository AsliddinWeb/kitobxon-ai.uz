"""
OpenAI API bilan ishlash servisi
"""

from openai import OpenAI
from django.conf import settings


class AIService:
    """AI yordamchi servisi"""

    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4o-mini"

    def chat_with_book(self, book_content: str, user_message: str, chat_history: list = None) -> str:
        """Kitob kontekstida AI bilan suhbat"""

        if chat_history is None:
            chat_history = []

        system_prompt = f"""Sen "Kitobxon AI" - aqlli kitob yordamchisisan.
Foydalanuvchi senga kitob haqida savollar beradi.

📚 KITOB MAZMUNI:
{book_content[:8000]}

📋 QOIDALAR:
1. Faqat shu kitob haqida gapir
2. O'zbek tilida javob ber
3. Qisqa va aniq javob ber
4. Kitobda yo'q ma'lumot so'ralsa, shuni ayt
5. Do'stona tonda gapir"""

        messages = [{"role": "system", "content": system_prompt}]

        for msg in chat_history[-10:]:
            messages.append({
                "role": msg['role'],
                "content": msg['content']
            })

        messages.append({"role": "user", "content": user_message})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Xatolik yuz berdi: {str(e)}"

    def generate_summary(self, book_content: str) -> str:
        """Kitob summarini generatsiya qilish"""

        prompt = f"""Quyidagi kitobni o'zbek tilida qisqacha summarla.

📚 KITOB:
{book_content[:10000]}

📋 FORMAT:
1. 📖 ASOSIY G'OYA (2-3 gap)
2. 🎯 MUHIM FIKRLAR (5 ta punkt)
3. 👤 KIM O'QISHI KERAK (1 gap)

Qisqa va tushunarli yoz."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Xatolik yuz berdi: {str(e)}"

    def generate_quiz(self, book_content: str, num_questions: int = 5) -> list:
        """Kitob bo'yicha test savollarini generatsiya qilish"""

        prompt = f"""Quyidagi kitob asosida {num_questions} ta test savoli yarat.

📚 KITOB:
{book_content[:8000]}

JSON formatda javob ber:
{{
    "questions": [
        {{
            "question": "Savol matni",
            "options": ["A variant", "B variant", "C variant", "D variant"],
            "correct": 0,
            "explanation": "Tushuntirish"
        }}
    ]
}}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.7,
                response_format={"type": "json_object"}
            )

            import json
            result = json.loads(response.choices[0].message.content)
            return result.get('questions', [])
        except Exception as e:
            return []

    def generate_book_content(self, title: str, author: str, source_text: str) -> str:
        """Kitob uchun AI content yaratish (Admin uchun)"""

        prompt = f"""Sen kitob tahlilchisisisan. Quyidagi kitob haqida to'liq ma'lumot yarat.

📚 KITOB: "{title}"
✍️ MUALLIF: {author}

📄 MANBA MATN:
{source_text[:12000]}

═══════════════════════════════════════════════════════════
VAZIFA: Quyidagi formatda kitob haqida batafsil content yoz (O'ZBEK TILIDA):
═══════════════════════════════════════════════════════════

1. KIRISH (3-4 gap)
   - Kitob nima haqida
   - Muallif haqida qisqacha

2. ASOSIY G'OYALAR (har biri 2-3 gap bilan)
   - Kamida 5-7 ta asosiy g'oya
   - Har bir g'oyani tushuntir
   - Amaliy misollar keltir

3. MUHIM IQTIBOSLAR
   - 5-10 ta eng yaxshi iqtiboslar
   - Har birining ma'nosini tushuntir

4. PERSONAJLAR (agar badiiy kitob bo'lsa)
   - Asosiy personajlar
   - Ularning xarakterlari

5. AMALIY MASLAHATLAR
   - Kitobdan olinadigan saboqlar
   - Hayotda qanday qo'llash mumkin

6. XULOSA
   - Kitobning asosiy xabari
   - Kim o'qishi kerak

To'liq, batafsil, foydali content yoz. Kamida 3000 so'z bo'lsin."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=4000,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Xatolik yuz berdi: {str(e)}"