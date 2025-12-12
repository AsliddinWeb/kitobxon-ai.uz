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

    def chat_with_book(self, book, user_message):
        """Kitob haqida GPT bilan suhbat"""

        # Xavfsiz ma'lumot olish
        author_name = book.author.name if book.author else "Noma'lum"
        category_name = book.category.name if book.category else "Umumiy"

        system_prompt = f"""Sen "{book.title}" ({author_name}) kitobi bo'yicha ekspertsan.

Kitob haqida ma'lumot:
- Kitob nomi: {book.title}
- Muallif: {author_name}
- Kategoriya: {category_name}
- Tavsif: {book.description}

Foydalanuvchi savollariga shu kitob kontekstida javob ber.
O'zbek tilida javob ber.
Kitobdagi g'oyalar, boblar, misollar haqida batafsil gapir.
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=1000,
            temperature=0.7
        )

        return response.choices[0].message.content

    def generate_summary(self, book) -> str:
        """Kitob summarini generatsiya qilish"""

        # Xavfsiz ma'lumot olish
        author_name = book.author.name if book.author else "Noma'lum"
        category_name = book.category.name if book.category else "Umumiy"

        prompt = f"""Sen "{book.title}" ({author_name}) kitobi bo'yicha ekspertsan.

📚 KITOB MA'LUMOTLARI:
- Kitob nomi: {book.title}
- Muallif: {author_name}
- Kategoriya: {category_name}
- Tavsif: {book.description}

📋 VAZIFA:
Bu kitobning o'zbek tilida batafsil xulosasini yoz.

📋 FORMAT:
1. 📖 ASOSIY G'OYA (3-4 gap)
   - Kitob nima haqida
   - Asosiy maqsadi

2. 🎯 MUHIM FIKRLAR (5-7 ta punkt)
   - Har bir fikrni 2-3 gapda tushuntir
   - Amaliy misollar keltir

3. 💡 ASOSIY SABOQLAR
   - Kitobdan nimalarni o'rganish mumkin
   - Hayotda qanday qo'llash mumkin

4. 👤 KIM O'QISHI KERAK
   - Qaysi odamlarga foydali

Batafsil va foydali xulosa yoz."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Xatolik yuz berdi: {str(e)}"

    def generate_quiz(self, book, num_questions: int = 5) -> list:
        """Kitob bo'yicha test savollarini generatsiya qilish"""

        # Xavfsiz ma'lumot olish
        author_name = book.author.name if book.author else "Noma'lum"
        category_name = book.category.name if book.category else "Umumiy"

        prompt = f"""Sen "{book.title}" ({author_name}) kitobi bo'yicha ekspertsan.

📚 KITOB MA'LUMOTLARI:
- Kitob nomi: {book.title}
- Muallif: {author_name}
- Kategoriya: {category_name}
- Tavsif: {book.description}

📋 VAZIFA:
Bu kitob asosida {num_questions} ta test savoli yarat.

Savollar kitobning asosiy g'oyalari, muhim fikrlari va amaliy maslahatlari haqida bo'lsin.

JSON formatda javob ber:
{{
    "questions": [
        {{
            "question": "Savol matni",
            "options": ["A variant", "B variant", "C variant", "D variant"],
            "correct": 0,
            "explanation": "Nima uchun bu javob to'g'ri - tushuntirish"
        }}
    ]
}}

Savollar qiziqarli va o'rgatuvchi bo'lsin."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2500,
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