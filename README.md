# Yazılım Lab II - Web Arayüzünden Otomatik Ders Programı Oluşturma

Bu proje, **Yazılım Lab II** dersi kapsamında geliştirilmiş web tabanlı bir haftalık ders programı oluşturma uygulamasıdır. Uygulama; ders, derslik, öğretim üyesi ve bölüm bilgilerini kullanarak Yazılım Mühendisliği ve Bilgisayar Mühendisliği bölümleri için haftalık ders programı üretir.

İlk hâlindeki tek dosyalı ve doğrudan veritabanına bağlı yapı, bu sürümde daha düzenli bir Flask proje yapısına dönüştürülmüştür. Ders programı oluşturma mantığı ayrı modüllere ayrılmış, Excel çıktı üretimi düzenlenmiş ve test edilebilir hâle getirilmiştir.

## Özellikler

- Flask tabanlı web arayüzü
- Ders, derslik ve kullanıcı/öğretim üyesi yönetimi
- Yazılım Mühendisliği ve Bilgisayar Mühendisliği için ayrı program oluşturma
- Ortak dersleri ilgili bölüm programına dahil etme
- Aynı öğretim üyesi, derslik ve sınıf için saat çakışmasını engelleme
- Dersleri mümkün olduğunca blok saatler hâlinde yerleştirme
- `Yönetici` öğretim üyesi olarak görünüyorsa Excel çıktısında öğretim üyesi alanını boş bırakma
- Haftalık ders programını web arayüzünde Excel benzeri çizelge olarak görüntüleme
- Haftalık ders programını Excel dosyası olarak dışa aktarma
- Modüler Python proje yapısı
- Birim testleri ile yerleşim ve çıktı mantığını kontrol etme

## Proje Yapısı

```text
yazilim-lab-2-web-ders-programi/
├── README.md
├── pyproject.toml
├── .gitignore
├── data/
│   └── ornek_veriler.json
├── src/
│   └── web_ders_programi/
│       ├── __init__.py
│       ├── app.py
│       ├── cli.py
│       ├── excel_exporter.py
│       ├── models.py
│       ├── repository.py
│       ├── scheduler.py
│       └── templates/
│           ├── base.html
│           ├── index.html
│           ├── courses.html
│           ├── course_form.html
│           ├── rooms.html
│           ├── instructors.html
│           └── schedule.html
└── tests/
    ├── test_excel_exporter.py
    └── test_scheduler.py
```

## Kullanılan Teknolojiler

- Python
- Flask
- openpyxl
- unittest

## Kurulum

Python 3.10 veya üzeri önerilir.

Proje klasöründe aşağıdaki komut çalıştırılır:

```bash
python -m pip install -e .
```

## Çalıştırma

Web uygulamasını başlatmak için:

```bash
python -m web_ders_programi.app
```

veya paket kurulumundan sonra:

```bash
web-ders-programi
```

Uygulama varsayılan olarak şu adreste çalışır:

```text
http://127.0.0.1:5000
```

## Ders Programı Oluşturma Mantığı

Program, dersleri bölüm ve dönem bilgisine göre haftalık çizelgeye yerleştirir. Bir ders yerleştirilirken aşağıdaki kurallar kontrol edilir:

- Aynı sınıfın aynı saat aralığında birden fazla dersi olamaz.
- Aynı öğretim üyesi aynı saat aralığında birden fazla derse atanamaz.
- Aynı derslik aynı saat aralığında birden fazla ders için kullanılamaz.
- Ortak dersler, ilgili bölüm programına dahil edilir.
- Dersler mümkün olduğunca aynı gün içinde blok hâlinde yerleştirilir.

Örneğin 3 saatlik bir ders için önce 3 saatlik kesintisiz blok aranır. Uygun blok bulunamazsa 2+1 gibi daha düzenli parçalara ayrılarak yerleştirme denenir. Böylece derslerin dağınık ve mantıksız saatlere bölünmesi azaltılır.

## Yönetici Öğretim Üyesi Kuralı

Veri içinde öğretim üyesi alanı `Yönetici` olarak gelirse, bu değer gerçek öğretim üyesi adı gibi gösterilmez. Excel çıktısında öğretim üyesi satırı boş bırakılır. Bu sayede geçici veya sistemsel kullanıcı bilgileri ders programında hoca adı gibi görünmez.

## Web Arayüzü Görüntüleme Mantığı

Program oluşturulduğunda web arayüzünde yalnızca dolu ders satırları listelenmez. Bunun yerine gün-saat satırları ve 1, 2, 3, 4. sınıf sütunlarından oluşan haftalık çizelge gösterilir. Böylece ekranda görünen yapı Excel çıktısıyla aynı mantığa sahip olur. Boş saatler boş hücre olarak kalır; dolu hücrelerde ders kodu, ders adı, öğretim üyesi ve derslik bilgisi gösterilir.

## Excel Çıktıları

Web arayüzünde program oluşturulduğunda `downloads/` klasöründe aşağıdaki dosyalar üretilebilir:

```text
output_yazilim.xlsx
output_bilgisayar.xlsx
```

Her Excel dosyasında gün-saat satırları ve 1, 2, 3, 4. sınıf sütunları bulunur. Ders hücrelerinde ders kodu, ders adı, öğretim üyesi ve derslik bilgisi gösterilir.

## Testler

Testleri çalıştırmak için:

```bash
python -m unittest discover -s tests -v
```

## Geliştirme Notları

Bu sürümde eski yapıdaki tekrar eden dosyalar, önceden oluşturulmuş Excel çıktıları ve `__pycache__` klasörleri repodan çıkarılmıştır. Uygulamanın temel hesaplama ve yerleştirme mantığı Flask arayüzünden ayrılmıştır. Böylece ders programı algoritması, web arayüzünden bağımsız olarak test edilebilir.

## Hazırlayanlar

- Gürel BİLGİN
- Gizem YALÇIN
- Berkay ARAS
- Ali AKSOY

