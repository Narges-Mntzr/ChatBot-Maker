## چت‌بات‌ساز (Chatbot Maker)

در این پروژه قصد داریم یک سایت توسعه دهیم که در آن تعدادی از کاربران بتوانند برای دیتای مورد نظر خودشون chatBot بسازن. به این ترتیب که ابتدا دیتای مورد نظرشون رو در نرم‌افزار وارد میکنن (knowledge base) و بعد بتونن چت باتی بسازن که با توجه به دیتای وارد شده در مرحله قبل به سوالات کاربرها جواب بده.
و همچنین بقیه کاربران می‌توانند گفت و گوهایی با این بات‌های ساخته شده ایجاد کنند و با توجه به محتوای آن‌ها از آن‌ها سوال بپرسند.

## تکنولوژی‌های استفاده شده در پروژه:

1.قسمت اصلی و بدنه پروژه با فریمورک django پیاده‌سازی شده است.<br />
2.پایگاه‌داده مورد استفاده در پروژه postgres می‌باشد. (برای استفاده از اکتنشن pgvector از ایمیج ankane/pgvector استفاده شده است)<br /><br />

## کاربران پروژه:

### Torob Admin

ادمین سایت که دسترسی به اطلاعات تمامی کاربران، بات‌ها، محتواها و گفتگوهای ساخته شده را دارد و می‌تواند آن‌ها را اضافه، حذف و یا ویرایش کند.

### Chatbot Maker

گروهی از کاربران که ادمین سایت به آنها دسترسی ساخت بات‌های جدیدی را داده است. این گروه از کاربران می‌توانند بات‌ها و محتواهایی که توسط آن‌ها ایجاد شده است را ببینند و در صورت نیاز آن‌ها را ویرایش کنند.

### Normal User

این دسته تمامی کاربران سایت را شامل می‌شود که می‌توانند در سایت ثبت‌نام کنند و پس از ورود به سایت با بات‌هایی که در سایت موجود است گفت و گوی جدیدی را آغاز کنند.

همچنین می‌توانند گفتگو‌های قبلی خود را دیده و در صورت فعال بودن بات گفتگو را ادامه دهند. این کاربران در صورت نیاز می‌توانند روی چت‌های خود براساس عنوان و متن پیام‌ها Full Text Search انجام دهند.

## معماری پروژه اصلی:

این پروژه شامل یک اپ chatbot است که در آن برای هر یک از نیازمندی‌ها فایلی جدا در نظر گرفته شده است که توضیح آن به شرح زیر می‌باشد.

- **data:** دیتاست مورد استفاده برای تست عملکرد بررسی شباهت سوال و محتوا
- **migrations:** مایگرشن‌های ساخته شده برای پایگاه‌داده
- **templates**: تمپلیت‌های مورد استفاده در برنامه که پایه‌ همه‌ی آنها base.html است.
- **admin.py:** توابع و مدل‌های مرتبط با شخصی‌سازی پنل ادمین
- **functions.py:** توابع مورد استفاده در ویوها (به‌طور خاص توابع مورد نیاز برای ارتباط با اپن‌ای‌آی)
- **models.py:** مدل‌های مورد استفاده در برنامه
- **signals.py:** سیگنال‌های مورد استفاده
- **tests.py:** تست‌های نوشته شده شامل تست عملکرد شباهت و تست‌های ویو‌ها
- **urls.py:** اندپوینت‌های برنامه
- **views.py:** ویو‌های مورد استفاده

## مدل‌های مورد استفاده

### 1. User

مدل user پیش‌فرض خود django که برای کاربران مقدار email برای username در نظرگرفته شده است.
و هم چنین هر کاربر یک username، password و group دارد.

### 2. Bot:

    user: ForeignKey(User) #کاربری که بات را ساخته
    title: CharField(20)
    detail: TextField(1000)
    img: ImageField # در ولمی که برای کانتیرها ساخته شده ذخیره می‌شود
    prompt: TextField(1000) #سیستم پرامپت‌های درخواست‌های مرتبط با این بات
    is_active: BooleanField

### 3. BotContent

    bot: ForeignKey(Bot)
    text: TextField(800)
    embedding = VectorField(dimensions=1536) #در قسمت بعدی بیشتر توضیح داده می‌شود

### 4. Chat

    user: ForeignKey(User) #کاربری که گفت‌و‌گو را ساخته
    bot: ForeignKey(Bot)
    title: CharField(30) #به صورت خودکار بعد از اولین پیام ایجاد می‌شود.
    preview: TextField(50) #مرتبط با اولین پیام
    create_date: DateTimeField
    last_message_date: models.DateTimeField #به صورت خودکار به کمک سیگنال‌ها بعد از هر پیام به‌روز می‌شود.

### 5. Message

    class Reaction: TextChoices(LIKE, DISLIKE, NONE)
    class Role: TextChoices(BOT, USER)

    chat: ForeignKey(Chat)
    previous_message: ForeignKey(Message)
    text: TextField(800)
    pub_date: DateTimeField
    role: CharField(choices=Role.choices)
    reaction: CharField(choices=Reaction.choices)
    related_botcontent: ForeignKey(BotContent) #به‌دست آمد به کمک تابع امبدینگ و بررسی میزان شباهت

    def get_prompt(self):
        f'''
        "{self.related_botcontent.text}"
        Based on the above document and your own information, give a step-by-step and acceptable answer to the following question.
        Question: {self.text}
        '''

### Endpoint های مورد استفاده

| Endpoint | Method | Params | Task | Login |
| -------- | ------ | ------ | ---- | ----- |
| /admin/  | -- | -- | ادمین پنل | X |
| /chatbot/ | GET | 'searchChat', 'page' | چت‌های مطابق با فیلد سرچ شده به صورت صفحه به صفحه | X |
| /chatbot/createchat/ | GET | -- | لیست بات‌های فعال | X |
| /chatbot/createchat/ | POST | 'bot' | ایجاد چت جدید | X |
| /chatbot/chat/\<int:chat_id> | GET | -- | لیست پیام‌های چت | X |
| /chatbot/chat/\<int:chat_id> | POST | 'msg-text' | ایجاد پیام جدید در چت | X |
| /chatbot/login/ | GET | -- | صفحه ورود | |
| /chatbot/login/ | POST | 'username', 'password' | بررسی ورود کاربر | |
| /chatbot/logout/ | GET | -- | خروج کاربر | | 
| /chatbot/register/ | GET | -- | صفحه ثبت‌نام | |
| /chatbot/register/ | POST | 'username', 'password', 'password-confirm' | بررسی ثبت کاربر جدید | |
| /chatbot/\<int:msg_id>/reaction/ | POST | 'reaction' | ثبت نظر کاربر روی پیام | X |

* صفحاتی که نیاز به ورود کاربر پیش از آن دارند در صورتی که کاربر وارد نشده باشد آن را به صفحه Landing منتقل می‌کنند.

## OpenAI
### embedding
محتواهای ذخیره شده برای بات و پیام‌ها بعد از ایجاد به کمک مدل "text-embedding-ada-002" به یک آرایه با 1536 درایه و نرم ۱ نظیر می‌شوند. سپس این آرایه به کمک اکستنشن pfvector ذخیره می‌شود.

### similarity
شباهت سوالات کاربر و محتواها به کمک تابع CosineDistance بررسی و شبیه‌ترین محتوا در کنار سوال قرار می‌گیرد.



### prompts
بعد از پیدا کردن شبیه‌ترین محتوا ریکوستی به مدل gpt-3.5-turbo زده‌می‌شود که شامل سیستم پرامپت ذخیره شده در بات، سوال قبلی کاربر، محتوای نظیر آن، پاسخ مدل، سوال کنونی کاربر و محتوای مرتبط با آن است.

سوالات و محتواهای مرتبط با آن‌ها با قالب زیر برای مدل فرستاده می‌شود.

    "{self.related_botcontent.text}"
    Based on the above document and your own information, give a step-by-step and acceptable answer to the following question.
    Question: {self.text}
### test similarity
 عملکرد تابع شباهت به کمک یک دیتاست با ۵۸۴ محتوا و سوال اندازه‌گیری می‌شود. به این صورت که یک کلاس تست نوشته شده است که ۱۰۰ عدد از محتواها را به صورت تصادفی انتخاب می‌کند و آن‌ها را به باتی اضافه می‌کند سپس شروع به پرسیدن این ۱۰۰ سوال می‌کند و به ازای هر سوال که محتوای خروجی تابع similar_content و محتوا درون دیتاست یکسان بود مقدار trueAnswers را یکی افزایش می‌دهد.

 بعد از اتمام صد سوال مقدار trueAnswers را در فایل django.log لاگ می‌اندازد.که عملکرد این تابع در سه بار اجرای تابع تست به صورت زیر می‌باشد.

 | trueAnswers | 97/100 | 97/100 | 99/100 |
 | ----------- | ------ | ------ | ------ |

 ## اجرای برنامه
 1. docker build -t DOCKER_IMAGE .
 2. set DOCKER_IMAGE and OPENAI_API_KEY in docker compose
 3. docker compose up -d

see: https://chatbotmaker.darkube.app/