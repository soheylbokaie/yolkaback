from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from shop.models import Category, Product, Wood

CATEGORIES = [
    ("furniture", "مبلمان", 1),
    ("kitchen", "آشپزخانه", 2),
    ("decor", "دکوراتیو", 3),
    ("office", "کار و مطالعه", 4),
]

WOODS = [
    ("oak", "بلوط", "Oak", "رگه باز و درشت",
     "سخت، مقاوم و با رگه‌های روشن؛ انتخابی ابدی برای میز و کابینت.", "/img/oak.jpg"),
    ("walnut", "گردو", "Walnut", "رگه موّاج و مخملی",
     "عمق رنگی تیره و اشرافی؛ چوبی برای قطعات شاخص و ماندگار.", "/img/walnut.jpg"),
    ("ash", "زبان گنجشک", "Ash", "رگه مستقیم و کشیده",
     "روشن و انعطاف‌پذیر؛ مناسب فرم‌های خمیده و طراحی مدرن.", "/img/ash.jpg"),
    ("pine", "کاج", "Pine", "رگه نرم با گره",
     "سبک و گرم با گره‌های طبیعی؛ حس صمیمی فضاهای روستایی مدرن.", "/img/pine.jpg"),
]

PRODUCTS = [
    dict(slug="walnut-coffee-table", title="میز جلومبلی لبه‌طبیعی", category="furniture", wood="walnut",
         price=48_000_000, old_price=56_000_000, badge="پرفروش", stock=3, image_url="/img/shop-1.jpg",
         alt="میز جلومبلی چوب گردو با لبه طبیعی",
         description="اسلب یکپارچه گردو با پرداخت روغن گیاهی و پایه فلزی مشکی."),
    dict(slug="oak-board-set", title="ست تخته سرو بلوط", category="kitchen", wood="oak",
         price=3_900_000, badge="دست‌ساز", stock=12, image_url="/img/shop-2.jpg",
         alt="ست تخته سرو و کاسه چوبی بلوط دست‌ساز",
         description="سه تخته در اندازه‌های مختلف، بهداشتی و مقاوم در برابر رطوبت."),
    dict(slug="ash-chair", title="صندلی ناهارخوری آش", category="furniture", wood="ash",
         price=12_500_000, stock=8, image_url="/img/shop-3.jpg",
         alt="صندلی ناهارخوری مینیمال از چوب زبان گنجشک",
         description="فرم ارگونومیک با اتصالات فاق و زبانه، بدون پیچ نمایان."),
    dict(slug="oak-shelf", title="شلف دیواری معلق", category="decor", wood="oak",
         price=5_400_000, stock=15, image_url="/img/shop-4.jpg",
         alt="شلف دیواری چوب بلوط با نصب مخفی",
         description="نصب مخفی، ضخامت ۴ سانتی‌متر و لبه‌های نرم پخ‌خورده."),
    dict(slug="desk-organizer", title="ست رومیزی گردو", category="office", wood="walnut",
         price=2_800_000, badge="جدید", stock=20, image_url="/img/shop-5.jpg",
         alt="ست نظم‌دهنده رومیزی و جاقلمی چوب گردو",
         description="جاقلمی، نگه‌دارنده موبایل و جای کارت در یک مجموعه هماهنگ."),
    dict(slug="pine-nightstand", title="پاتختی تک‌کشو کاج", category="furniture", wood="pine",
         price=8_600_000, stock=0, image_url="/img/shop-6.jpg",
         alt="پاتختی چوب کاج با یک کشو",
         description="کشوی ریل آرام‌بند با بدنه چوب ماسیو کاج شمال."),
]


class Command(BaseCommand):
    help = "ایجاد داده‌های اولیه فروشگاه یولکا وود و کاربر ادمین"

    def handle(self, *args, **options):
        cats = {}
        for slug, name, order in CATEGORIES:
            cats[slug], _ = Category.objects.update_or_create(
                slug=slug, defaults={"name": name, "order": order}
            )

        woods = {}
        for slug, fa, en, texture, desc, img in WOODS:
            woods[slug], _ = Wood.objects.update_or_create(
                slug=slug,
                defaults={"name_fa": fa, "name_en": en, "texture": texture,
                          "description": desc, "image_url": img},
            )

        for i, row in enumerate(PRODUCTS):
            data = dict(row)
            data["category"] = cats[data["category"]]
            data["wood"] = woods[data["wood"]]
            data["order"] = i
            slug = data.pop("slug")
            Product.objects.update_or_create(slug=slug, defaults=data)

        User = get_user_model()
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@yolkawood.ir", "yolka1234")
            self.stdout.write("کاربر ادمین ساخته شد: admin / yolka1234")

        self.stdout.write(self.style.SUCCESS(
            f"داده اولیه ثبت شد: {Product.objects.count()} محصول، {Category.objects.count()} دسته."
        ))
