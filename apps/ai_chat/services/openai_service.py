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


    # Kitob taqqoslash metodi
    def compare_books(self, book1, book2) -> str:
        """Ikki kitobni AI bilan taqqoslash - HTML formatda"""

        # Book 1 ma'lumotlari
        author1 = book1.author.name if book1.author else "Noma'lum"
        category1 = book1.category.name if book1.category else "Umumiy"

        # Book 2 ma'lumotlari
        author2 = book2.author.name if book2.author else "Noma'lum"
        category2 = book2.category.name if book2.category else "Umumiy"

        prompt = f"""Sen kitob ekspertisan. Quyidagi 2 ta kitobni taqqosla.

    📚 KITOB 1:
    - Nomi: {book1.title}
    - Muallif: {author1}
    - Kategoriya: {category1}
    - Tavsif: {book1.description}

    📚 KITOB 2:
    - Nomi: {book2.title}
    - Muallif: {author2}
    - Kategoriya: {category2}
    - Tavsif: {book2.description}

    📋 VAZIFA:
    Quyidagi HTML formatda taqqoslash yoz (O'zbek tilida, faqat HTML kod, hech qanday qo'shimcha matn yoki tushuntirish yo'q):

    <div class="space-y-6">
        <!-- Umumiy taqqoslash -->
        <div class="bg-gradient-to-br from-purple-50 to-pink-50 rounded-2xl p-6 border-2 border-purple-200">
            <h2 class="text-2xl font-bold text-slate-800 mb-4 flex items-center gap-2">
                <span>📊</span> Umumiy taqqoslash
            </h2>
            <div class="overflow-x-auto">
                <table class="w-full">
                    <thead>
                        <tr>
                            <th class="text-left py-3 px-4">Xususiyat</th>
                            <th class="text-left py-3 px-4">{book1.title}</th>
                            <th class="text-left py-3 px-4">{book2.title}</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td class="py-3 px-4 font-semibold">Mavzu</td>
                            <td class="py-3 px-4">...</td>
                            <td class="py-3 px-4">...</td>
                        </tr>
                        <tr>
                            <td class="py-3 px-4 font-semibold">Qiyinlik</td>
                            <td class="py-3 px-4">...</td>
                            <td class="py-3 px-4">...</td>
                        </tr>
                        <tr>
                            <td class="py-3 px-4 font-semibold">O'qish vaqti</td>
                            <td class="py-3 px-4">...</td>
                            <td class="py-3 px-4">...</td>
                        </tr>
                        <tr>
                            <td class="py-3 px-4 font-semibold">Amaliylik</td>
                            <td class="py-3 px-4">...</td>
                            <td class="py-3 px-4">...</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Asosiy farqlar -->
        <div class="bg-white rounded-2xl p-6 border-2 border-slate-200">
            <h2 class="text-2xl font-bold text-slate-800 mb-4 flex items-center gap-2">
                <span>🎯</span> Asosiy farqlar
            </h2>
            <ul class="space-y-3">
                <li class="flex items-start gap-3">
                    <span class="text-purple-500 text-xl flex-shrink-0">•</span>
                    <span class="text-slate-700">...</span>
                </li>
                <li class="flex items-start gap-3">
                    <span class="text-purple-500 text-xl flex-shrink-0">•</span>
                    <span class="text-slate-700">...</span>
                </li>
                <li class="flex items-start gap-3">
                    <span class="text-purple-500 text-xl flex-shrink-0">•</span>
                    <span class="text-slate-700">...</span>
                </li>
            </ul>
        </div>

        <!-- Kim uchun mos -->
        <div class="grid md:grid-cols-2 gap-6">
            <div class="bg-purple-50 rounded-2xl p-6 border-2 border-purple-200">
                <h3 class="text-xl font-bold text-purple-700 mb-3 flex items-center gap-2">
                    <span>📚</span> {book1.title}
                </h3>
                <p class="text-slate-700 leading-relaxed">...</p>
            </div>
            <div class="bg-pink-50 rounded-2xl p-6 border-2 border-pink-200">
                <h3 class="text-xl font-bold text-pink-700 mb-3 flex items-center gap-2">
                    <span>📖</span> {book2.title}
                </h3>
                <p class="text-slate-700 leading-relaxed">...</p>
            </div>
        </div>

        <!-- Tavsiya -->
        <div class="bg-gradient-to-r from-amber-50 to-orange-50 rounded-2xl p-6 border-2 border-amber-200">
            <h2 class="text-2xl font-bold text-slate-800 mb-4 flex items-center gap-2">
                <span>⭐</span> Tavsiya
            </h2>
            <p class="text-slate-700 leading-relaxed">...</p>
        </div>

        <!-- Xulosa -->
        <div class="bg-gradient-to-br from-slate-50 to-slate-100 rounded-2xl p-6 border-2 border-slate-300">
            <h2 class="text-2xl font-bold text-slate-800 mb-4 flex items-center gap-2">
                <span>🏆</span> Xulosa
            </h2>
            <p class="text-slate-700 leading-relaxed text-lg">...</p>
        </div>
    </div>

    MUHIM: Faqat HTML kod yoz, hech qanday qo'shimcha matn, tushuntirish yoki markdown yo'q. To'g'ridan-to'g'ri <div> dan boshla va </div> bilan tugat."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2500,
                temperature=0.7
            )

            html_content = response.choices[0].message.content.strip()

            # Agar markdown kod bloki bilan kelgan bo'lsa, uni olib tashlash
            if html_content.startswith('```html'):
                html_content = html_content.replace('```html', '').replace('```', '').strip()
            elif html_content.startswith('```'):
                html_content = html_content.replace('```', '').strip()

            return html_content

        except Exception as e:
            return f"""
            <div class="bg-red-50 border-2 border-red-200 rounded-2xl p-6">
                <h3 class="text-xl font-bold text-red-700 mb-2">❌ Xatolik</h3>
                <p class="text-red-600">Taqqoslashda xatolik yuz berdi: {str(e)}</p>
            </div>
            """



