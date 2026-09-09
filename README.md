# یولکا وود — بک‌اند فروشگاه (Django + DRF)

## اجرا
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py seed          # داده اولیه + کاربر admin / yolka1234
python manage.py runserver 0.0.0.0:8000
```

پنل مدیریت: `/admin/`  (admin / yolka1234)

## API
| متد | مسیر | توضیح |
|---|---|---|
| GET | `/api/products/` | لیست محصولات فعال — `?category=furniture&search=میز&in_stock=1` |
| GET | `/api/products/<slug>/` | جزئیات محصول |
| GET | `/api/categories/` | دسته‌بندی‌ها |
| GET | `/api/woods/` | انواع چوب |
| POST | `/api/orders/` | ثبت سفارش (کاهش خودکار موجودی) |
| POST | `/api/consults/` | ثبت درخواست مشاوره/سفارش ساخت |
| GET | `/api/health/` | بررسی سلامت سرویس |

### نمونه ثبت سفارش
```json
POST /api/orders/
{
  "full_name": "محمد رضایی",
  "phone": "09120000000",
  "address": "تهران، ...",
  "items": [{ "product": "oak-shelf", "quantity": 2 }]
}
```

## اتصال فرانت
Vite درخواست‌های `/api` و `/media` را به `http://127.0.0.1:8000` پراکسی می‌کند
(تنظیم در `choobban/vite.config.ts`). اگر بک‌اند بالا نباشد فروشگاه به‌صورت
خودکار روی داده محلی `src/data/products.ts` کار می‌کند.
