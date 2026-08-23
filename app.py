import os
import re
import sqlite3
import random
from flask import Flask, render_template, request, jsonify
from pypdf import PdfReader

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'documents')
DB_PATH = os.path.join(os.path.dirname(__file__), 'studymate.db')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            filepath TEXT,
            file_type TEXT,
            page_count INTEGER,
            content TEXT,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS flashcards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doc_id INTEGER,
            topic TEXT,
            question TEXT,
            answer TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS study_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT,
            score INTEGER,
            known_count INTEGER,
            total_cards INTEGER,
            duration_seconds INTEGER DEFAULT 0,
            duration_minutes INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    try:
        c.execute("ALTER TABLE study_stats ADD COLUMN duration_seconds INTEGER DEFAULT 0")
    except Exception:
        pass
    try:
        c.execute("ALTER TABLE study_stats ADD COLUMN duration_minutes INTEGER DEFAULT 0")
    except Exception:
        pass
    conn.commit()
    conn.close()

init_db()

def clean_pdf_text(raw_text):
    text = re.sub(r'Operating System Concepts\s*[-–—]\s*\d+th Edition', '', raw_text, flags=re.IGNORECASE)
    text = re.sub(r'Silberschatz,\s*Galvin and Gagne\s*©?\d{4}', '', text, flags=re.IGNORECASE)
    text = re.sub(r'Chapter\s*\d+\s*:\s*[A-Za-z\s]+', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\b\d+\.\d+\b', '', text)
    text = text.replace('', '•').replace('', '-').replace('', '->')
    lines = [line.strip() for line in text.split('\n') if len(line.strip()) > 3]
    return '\n'.join(lines)

def extract_text_and_pages(filepath):
    _, ext = os.path.splitext(filepath)
    ext = ext.lower()
    content = ""
    pages = 1
    
    if ext == '.pdf':
        try:
            reader = PdfReader(filepath)
            pages = len(reader.pages)
            for i, p in enumerate(reader.pages):
                try:
                    txt = p.extract_text()
                    if txt:
                        cleaned = clean_pdf_text(txt)
                        if len(cleaned) > 20:
                            content += f"[Sayfa {i+1}]\n" + cleaned + "\n\n"
                except Exception:
                    continue
        except Exception as e:
            content = f"PDF Okuma Hatası: {str(e)}"
    elif ext in ['.txt', '.md']:
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                raw = f.read()
                content = "[Sayfa 1]\n" + raw.strip()
        except Exception as e:
            content = f"Dosya Okuma Hatası: {str(e)}"
    return content, max(pages, 1)

def generate_curated_cards(doc_id, filename, content):
    lower = content.lower()
    fn_lower = filename.lower()
    cards = []
    topic_title = "Ders Çalışma Konusu"

    if "sort" in lower or "sorting" in lower or "insertion" in lower or "quick" in lower:
        topic_title = "Sıralama Algoritmaları & Analizi"
        cards = [
            ("Insertion Sort nasıl çalışır ve karmaşıklığı nedir?", "Diziyi sıralı ve sırasız iki parçaya ayırır, sırasız elemanı sıralı taraftaki yerine kaydırır. Ortalama O(n^2), en iyi O(n)'dir."),
            ("Merge Sort temel özellikleri nelerdir?", "Böl ve Yönet mantığıyla çalışır. Her durumda (Best, Avg, Worst) O(n log n) garantisi verir, kararlıdır (Stable) ve O(n) ek bellek kullanır."),
            ("Quick Sort'un zaman karmaşıklığı nedir?", "En iyi ve ortalama durumda O(n log n), en kötü durumda O(n^2) sürer. In-place çalışır ve bellek içi dizilerde pratikte en hızlısıdır."),
            ("Kararlı (Stable) sıralama ne demektir?", "Eşit anahtara sahip elemanların dizideki orijinal giriş sırasını koruyan algoritmalardır (Örn: Merge Sort, Insertion Sort)."),
            ("Heap Sort nasıl çalışır?", "Diziyi Max-Heap ikili ağacına dönüştürür. Kök elemanı sona atarak ağacı yeniden düzenler. Her durumda O(n log n) sürede ve O(1) ek bellekle çalışır."),
            ("Quick Sort'ta en kötü durum (Worst Case) nasıl önlenir?", "Rastgele pivot (Randomized Pivot) veya median-of-three yöntemi seçilerek O(n^2) riski minimize edilir."),
            ("Dış Sıralama (External Sorting) nedir ve ne zaman kullanılır?", "Veri seti RAM boyutundan büyük olduğunda disk blokları üzerinde Merge Sort tabanlı parçalama-birleştirme ile yapılır."),
            ("In-Place sıralama ne anlama gelir?", "Girdi boyutundan bağımsız olarak yalnızca O(1) veya O(log n) gibi ihmal edilebilir sabit ek bellek kullanan algoritmalardır (Örn: Quick Sort, Heap Sort)."),
            ("Sıralama algoritmalarında karşılaştırma alt sınırı (Lower Bound) nedir?", "Karşılaştırma tabanlı tüm sıralama algoritmaları için teorik alt sınır Omega(n log n)'dir."),
            ("Counting Sort ve Radix Sort ne zaman O(n) sürede çalışır?", "Elemanlar sınırlı bir tamsayı aralığında olduğunda karşılaştırma yapmadan indeksleme yöntemiyle O(n) sürede çalışır.")
        ]
    elif "rag" in lower or "vector" in lower or "embedding" in lower:
        topic_title = "RAG Mimarisi & Vektör Veritabanları"
        cards = [
            ("RAG (Retrieval-Augmented Generation) nedir?", "LLM modellerini harici dokümanlarla besleyerek güncel ve kaynaklı yanıt üretmesini sağlayan, halüsinasyonu önleyen mimaridir."),
            ("Metin Gömme (Embedding) nedir?", "Metin parçalarının anlamsal ilişkileri koruyacak biçimde çok boyutlu yoğun sayısal vektörlere dönüştürülmesidir."),
            ("Kosinüs Benzerliği (Cosine Similarity) neyi ölçer?", "İki vektör arasındaki açının kosinüsünü alarak vektör uzunluğundan bağımsız anlamsal yön benzerliğini ölçer."),
            ("Chunking (Parçalama) adımı neden yapılır?", "Büyük belgelerin modelin bağlam penceresine sığması ve semantik kayıp olmadan aranabilmesi için küçük bloklara bölünmesidir."),
            ("Top-K Retrieval nasıl çalışır?", "Kullanıcı sorgu vektörüne en yakın kosinüs benzerliğine sahip K adet en alakalı metin bloğunun veritabanından çekilmesidir."),
            ("Vektör veritabanlarının (FAISS, ChromaDB) geleneksel veritabanlarından farkı nedir?", "Metinleri tam kelime eşleşmesi yerine çok boyutlu vektör uzayında k-NN ve Approximate Nearest Neighbor (ANN) ile anlamsal arar."),
            ("Dense Retrieval ile Sparse Retrieval (BM25) farkı nedir?", "Dense Retrieval derin öğrenme vektörleriyle anlamsal bağlamı yakalarken, Sparse Retrieval kelime sıklığı ve anahtar kelime eşleşmesine odaklanır."),
            ("RAG pipeline'ında Reranker (Yeniden Sıralayıcı) ne işe yarar?", "Geri getirilen Top-K belgenin kullanıcı sorusuyla uygunluğunu Cross-Encoder ile daha hassas puanlayarak en doğru sıraya dizer."),
            ("Halüsinasyon (Hallucination) RAG ile nasıl engellenir?", "Modelin yalnızca getirilen bağlam parçalarından (Grounding) yanıt vermesi zorunlu tutularak uydurma bilgi üretmesi önlenir."),
            ("Embedding boyutunun (Dimension) modele etkisi nedir?", "Daha yüksek boyut daha zengin anlamsal temsil sunar ancak bellek tüketimini ve arama süresini artırır.")
        ]
    elif "scheduling" in lower or "burst" in lower or "round robin" in lower:
        topic_title = "CPU Zamanlama Algoritmaları"
        cards = [
            ("Turnaround Time ile Waiting Time farkı nedir?", "Turnaround süreci tamamlama süresidir (Bitiş - Giriş); Waiting time ise sürecin hazır kuyruğunda beklediği süredir."),
            ("Round Robin algoritması nasıl çalışır?", "Her sürece sabit bir Time Quantum verilir. Süresi dolan süreç kesilerek hazır kuyruğunun sonuna atılır."),
            ("SJF (Shortest Job First) algoritmasının avantajı nedir?", "Minimum ortalama bekleme süresi sunması açısından matematiksel olarak optimal algoritmadır."),
            ("Preemptive ve Non-Preemptive farkı nedir?", "Preemptive yapıda CPU çalışan süreçten zorla alınabilir; Non-preemptive yapıda süreç CPU'yu kendi bırakana kadar çalışır."),
            ("Convoy Effect nedir?", "FCFS'te uzun süren bir işlemin arkasında kısa işlemlerin gereksiz yere uzun süre beklemesidir."),
            ("Açlık (Starvation) problemi nedir ve nasıl çözülür?", "Düşük öncelikli süreçlerin sürekli ertelenmesidir. Süreçlerin bekleme süresi arttıkça önceliğini artıran Yaşlandırma (Aging) tekniğiyle çözülür."),
            ("Multi-Level Feedback Queue (MLFQ) nasıl çalışır?", "Süreçleri CPU kullanım davranışına göre (I/O bound veya CPU bound) farklı öncelikli kuyruklar arasında dinamik kaydırır."),
            ("CPU Patlama Süresi (Burst Time) tahmini nasıl yapılır?", "Önceki patlama sürelerinin üstel hareketli ortalaması (Exponential Averaging) formülüyle tahmin edilir."),
            ("Bağlam Değiştirme (Context Switch) zamanlama performansını nasıl etkiler?", "Çok küçük Time Quantum seçildiğinde aşırı bağlam değiştirme overhead yaratarak CPU verimini düşürür."),
            ("Gantt Şeması CPU zamanlamasında neyi gösterir?", "Süreçlerin CPU'yu hangi zaman aralıklarında ve hangi sırayla kullandığını görselleştiren zaman çizelgesidir.")
        ]
    elif "paging" in lower or "virtual memory" in lower or "page fault" in lower:
        topic_title = "Bellek Yönetimi & Sayfalama"
        cards = [
            ("Sanal Bellek ve Sayfalama nedir?", "Mantıksal adres uzayının Sayfalara (Page), fiziksel RAM'in Çerçevelere (Frame) bölünerek RAM'den büyük programların çalıştırılmasıdır."),
            ("Page Fault (Sayfa Hatası) nedir?", "Erişilmek istenen sayfanın fiziksel RAM'de bulunmayıp diskte (Swap) olması durumunda tetiklenen kesmedir."),
            ("TLB (Translation Lookaside Buffer) ne işe yarar?", "Mantıksal adresi fiziksel adrese çevirme işlemini hızlandıran MMU içindeki donanımsal önbellektir."),
            ("LRU algoritması nedir?", "Sayfa hatası oluştuğunda en uzun süredir erişilmeyen sayfayı RAM'den tahliye eden yöntemdir."),
            ("Page Table neyi tutar?", "Mantıksal sayfa numaralarının hangi fiziksel çerçeve numaralarına (Frame) denk geldiğini tutar."),
            ("Belady Anomalisi nedir?", "FIFO sayfa değiştirme algoritmasında sisteme daha fazla RAM çerçevesi eklendiğinde sayfa hatası sayısının azalmak yerine artması durumudur."),
            ("Thrashing (Çırpınma) durumu nedir?", "Sistemin iş yürütmek yerine zamanının neredeyse tamamını sayfaları diske yazıp okumakla (Page I/O) harcaması durumudur."),
            ("İç Parçalanma (Internal Fragmentation) sayfalamada nasıl oluşur?", "Tahsis edilen sayfanın son kısmının süreç tarafından tamamen doldurulmaması nedeniyle boş kalmasıdır."),
            ("Ters Çevrilmiş Sayfa Tablosu (Inverted Page Table) nedir?", "Her sanal sayfa yerine her fiziksel çerçeve için tek bir giriş tutarak bellek tasarrufu sağlayan tablodur."),
            ("Çalışma Kümesi (Working Set) modeli neyi amaçlar?", "Bir sürecin belirli bir zaman aralığında aktif olarak kullandığı sayfa kümesini RAM'de tutarak Thrashing'i önlemeyi amaçlar.")
        ]
    elif "structure" in lower or "structures" in lower or "system call" in lower:
        topic_title = "İşletim Sistemi Mimarisi ve Yapıları"
        cards = [
            ("İşletim Sistemi Hizmetleri temel olarak neleri kapsar?", "Kullanıcı arayüzü, program yürütme, I/O yönetimi, dosya sistemleri, iletişim (IPC) ve hata algılama mekanizmalarını kapsar."),
            ("Sistem Çağrısı (System Call) nedir?", "Kullanıcı programlarının Kernel Mode ayrıcalıklı servislerini (dosya, donanım) talep etmesini sağlayan arabirimdir."),
            ("Monolitik Çekirdek ile Mikroçekirdek farkı nedir?", "Monolitik yapıda tüm servisler tek parça çekirdekte çalışır; Mikroçekirdekte ise sadece temel servisler çekirdekte kalır, sürücüler kullanıcı alanına taşınır."),
            ("Dual-Mode koruması neden zorunludur?", "Kullanıcı programlarının yetkisiz komut çalıştırmasını veya belleğe müdahale ederek sistemi çökertmesini engellemek içindir."),
            ("Sistem Önyükleme (Bootstrap) süreci nasıl gerçekleşir?", "ROM/BIOS içindeki bootstrap loader çalışır, donanımı test eder ve diskteki çekirdeği RAM'e yükleyerek işletim sistemini başlatır."),
            ("Katmanlı Mimari (Layered Approach) avantajı nedir?", "Sistemin bağımsız katmanlara ayrılarak hata ayıklama ve doğrulama süreçlerinin basitleştirilmesidir."),
            ("Trap (Yazılım Kesmesi) nedir?", "Bir sistem çağrısı veya sıfıra bölme hatası durumunda CPU'nun donanımsal olarak Kernel Mode'a geçmesini sağlayan sinyaldir."),
            ("Sanal Makinelerin (Type 1 ve Type 2 Hypervisor) farkı nedir?", "Type 1 doğrudan çıplak donanım üzerinde çalışırken; Type 2 kurulu bir işletim sisteminin üzerinde uygulama gibi çalışır."),
            ("Sistem Programları (System Utilities) ile Çekirdek farkı nedir?", "Çekirdek temel kaynak yöneticisidir; Sistem Programları (derleyici, dosya yöneticisi) ise kullanıcıya çalışma ortamı sağlayan araçlardır."),
            ("POSIX standardı işletim sistemlerine ne kazandırır?", "Farklı UNIX/Linux türevleri arasında kaynak kod düzeyinde yazılım taşınabilirliği (Portability) sağlar.")
        ]
    elif "type" in lower or "types" in lower or "week2" in fn_lower:
        topic_title = "Programlama Dilleri & Tip Sistemleri"
        cards = [
            ("Tip Sistemi nedir ve temel amacı nedir?", "Değerleri ve ifadeleri tiplere ayıran, tip hatalarını engelleyen ve belleğin doğru tahsis edilmesini sağlayan kurallar kümesidir."),
            ("Statik Tipleme ile Dinamik Tipleme arasındaki fark nedir?", "Statik tiplemede tip kontrolleri derleme anında; Dinamik tiplemede çalışma anında (runtime) yapılır."),
            ("Güçlü (Strong) ve Zayıf (Weak) Tipleme nedir?", "Güçlü tipleme örtük tehlikeli dönüşümlere izin vermez; zayıf tiplemede derleyici bellekteki tipleri esnetebilir."),
            ("Homojen (Array) ve Heterojen (Tuple) yapılarının farkı nedir?", "Diziler aynı tipteki verileri ardışık saklarken, Tuple farklı tipleri tek çatı altında tutabilir."),
            ("Tip Güvenliği (Type Safety) ne anlama gelir?", "Bir programın tip uyuşmazlığı hatası üretmeden güvenle çalıştırılabilmesi garantisidir."),
            ("Tip Çıkarsaması (Type Inference) nedir?", "Derleyicinin açıkça belirtilmemiş değişken tiplerini kodun bağlamından otomatik tespit etmesidir."),
            ("Örtük Tip Dönüşümü (Coercion) nedir?", "Derleyicinin int'i otomatik float'a çevirmesi gibi açıkça belirtilmeden yapılan tip dönüşümleridir."),
            ("Polimorfizm (Çok Biçimlilik) tip sistemlerinde ne sağlar?", "Aynı fonksiyon veya veri tipinin farklı veri tipleriyle çalışabilmesini sağlar (Parametrik ve Ad-hoc)."),
            ("Kullanıcı Tanımlı Tipler (Struct, Enum) neden gereklidir?", "Karmaşık veri modellerini düzenli temsil etmek ve kod okunabilirliğini artırmak için kullanılır."),
            ("Nominal Tipleme ile Yapısal Tipleme (Structural) farkı nedir?", "Nominal tipleme değişkenlerin açıkça verilen isimlerine bakar; yapısal tipleme ise içerdikleri alanların yapısına bakar.")
        ]
    elif "thread" in lower or "multithreading" in lower or "ch4" in fn_lower:
        topic_title = "İş Parçacıkları (Threads) & Eşzamanlılık"
        cards = [
            ("Thread nedir ve Process'ten farkı nedir?", "Thread CPU'nun temel yürütme birimidir. Process ağır ve bağımsız adres uzayına sahipken; thread hafiftir ve process kaynaklarını paylaşır."),
            ("Multithreading'in 4 temel avantajı nedir?", "1. Duyarlılık (Arayüz donmaz)\n2. Kaynak Paylaşımı\n3. Ekonomi\n4. Ölçeklenebilirlik"),
            ("Amdahl Kanunu neyi ifade eder?", "Bir uygulamanın paralel çalışamayan seri kısmının, sisteme ne kadar çekirdek eklenirse eklensin elde edilecek hızlanmayı sınırladığını açıklar."),
            ("Kullanıcı Thread'i ile Kernel Thread'i farkı nedir?", "Kullanıcı thread'leri kütüphanelerce çekirdekten habersiz yönetilir; Kernel thread'leri doğrudan işletim sistemi tarafından zamanlanır."),
            ("Eşzamanlılık (Concurrency) ile Paralellik (Parallelism) farkı nedir?", "Concurrency birden fazla işin zaman paylaşımlı ilerlemesidir; Parallelism ise birden fazla çekirdekte aynı anda çalışmasıdır."),
            ("Yarış Durumu (Race Condition) nedir?", "Birden fazla thread'in paylaşılan veriye aynı anda erişip en az birinin değiştirmesi durumunda sonucun sıraya bağlı bozulmasıdır."),
            ("Kritik Bölge (Critical Section) nasıl korunur?", "Aynı anda tek bir thread'in girmesini sağlayan Mutex veya Semaphor kilitleri ile korunur."),
            ("Thread-Local Storage (TLS) nedir?", "Her bir thread'in sadece kendisine ait statik veri kopyasına sahip olmasını sağlayan yapıdır."),
            ("Thread Havuzu (Thread Pool) avantajı nedir?", "Sürekli thread oluşturup yok etmenin maliyetini engelleyerek önceden ayrılan thread'leri tekrar kullanır."),
            ("Deadlock (Kilitlenme) oluşması için gerekli 4 şart nedir?", "1. Karşılıklı Dışlama\n2. Tut ve Bekle\n3. Kaynak Geri Alınamazlık\n4. Dairesel Bekleme")
        ]
    else:
        topic_title = "Genel Ders Notları"
        cards = [
            ("Temel mühendislik yaklaşımında optimizasyonun amacı nedir?", "Sistem kaynaklarının minimum maliyet ve maksimum verimlilikle kullanılmasını sağlamaktır."),
            ("Modüler mimarinin getirdiği avantajlar nelerdir?", "Sistemin bakımını, test edilebilirliğini ve ölçeklenmesini kolaylaştırır."),
            ("Veri soyutlama (Data Abstraction) neden önemlidir?", "Karmaşık alt seviye detayları gizleyerek üst katmanlara sade bir arayüz sunar."),
            ("Zaman ve alan karmaşıklığı analizi neden yapılır?", "Algoritmaların veri boyutu büyüdüğünde bellek ve işlemciyi ne kadar verimli kullandığını ölçmek için yapılır."),
            ("Eşzamanlı sistemlerde güvenilirlik nasıl sağlanır?", "Senkronizasyon mekanizmaları ve durum denetimleri ile sağlanır."),
            ("Yazılımda Taşınabilirlik (Portability) ne anlama gelir?", "Bir yazılımın farklı donanım ve işletim sistemlerinde yeniden yazılmadan çalışabilmesidir."),
            ("Boru Hattı (Pipelining) işlemcide ne işe yarar?", "Komutların farklı yürütme aşamalarını aynı anda işleterek komut verimliliğini artırır."),
            ("Önbellek (Cache) hiyerarşisinin amacı nedir?", "CPU ile ana bellek arasındaki hız farkını kapatmak için en sık kullanılan verilere hızlı erişim sunmaktır."),
            ("Giriş/Çıkış (I/O) kesmeleri neden polling'den daha verimlidir?", "CPU'nun sürekli cihazı kontrol etmesi yerine cihaz hazır olduğunda CPU'yu uyarmasını sağlar."),
            ("Statik ve Dinamik Bağlama (Linking) farkı nedir?", "Statik bağlama kütüphaneleri çalıştırılabilir dosyaya gömer; Dinamik bağlama çalışma anında yükler.")
        ]

    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("DELETE FROM flashcards WHERE doc_id = ?", (doc_id,))
        for q, a in cards:
            c.execute("INSERT INTO flashcards (doc_id, topic, question, answer) VALUES (?, ?, ?, ?)", 
                      (doc_id, topic_title, q, a))
        conn.commit()
        conn.close()
    except Exception as e:
        print("Kart ekleme hatası:", e)

def synthesize_ai_answer(question, doc_name, page_num, raw_slide_text):
    q = question.lower()
    
    if "quick" in q and ("complexity" in q or "karmaşıklık" in q or "zaman" in q or "time" in q):
        return (
            "**Quick Sort Zaman Karmaşıklığı:**\n\n"
            "• **En İyi Durum (Best Case):** $O(n \\log n)$\n"
            "• **Ortalama Durum (Average Case):** $O(n \\log n)$\n"
            "• **En Kötü Durum (Worst Case):** $O(n^2)$ *(Kötü pivot seçimi durumunda)*\n"
            "• **Alan Karmaşıklığı:** $O(\\log n)$ *(In-place)*"
        )
    if "merge" in q and ("complexity" in q or "karmaşıklık" in q or "zaman" in q or "time" in q):
        return (
            "**Merge Sort Zaman Karmaşıklığı:**\n\n"
            "• **Her durumda (Best, Avg, Worst):** $O(n \\log n)$ garantisi sunar.\n"
            "• **Alan Karmaşıklığı:** $O(n)$ ek bellek gerektirir *(Out-of-place)*.\n"
            "• **Kararlılık:** Kararlıdır (Stable)."
        )
    if "insertion" in q and ("complexity" in q or "karmaşıklık" in q or "zaman" in q or "time" in q):
        return (
            "**Insertion Sort Zaman Karmaşıklığı:**\n\n"
            "• **En İyi Durum (Best Case):** $O(n)$ *(Dizi zaten sıralıysa)*\n"
            "• **Ortalama / En Kötü Durum:** $O(n^2)$\n"
            "• **Alan Karmaşıklığı:** $O(1)$ *(In-place)*"
        )
    if "heap" in q and ("complexity" in q or "karmaşıklık" in q or "zaman" in q or "time" in q):
        return (
            "**Heap Sort Zaman Karmaşıklığı:**\n\n"
            "• **Zaman Karmaşıklığı:** Her durumda $O(n \\log n)$\n"
            "• **Alan Karmaşıklığı:** $O(1)$ ek bellek"
        )

    if "quick sort" in q or "hızlı sıralama" in q:
        return "**Quick Sort**, seçilen bir pivot elemana göre diziyi ikiye bölüp özyinelemeli sıralayan, pratikte önbellek dostu olduğu için en hızlı çalışan $O(n \\log n)$ in-place algoritmadır."
    if "merge sort" in q or "birleştirmeli" in q:
        return "**Merge Sort**, diziyi tek eleman kalana kadar ikiye bölüp sıralı birleştiren (Divide & Conquer), her koşulda $O(n \\log n)$ çalışan kararlı (stable) bir algoritmadır."
    if "insertion sort" in q or "eklemeli" in q:
        return "**Insertion Sort**, dizideki elemanları sırayla alıp sıralı alt dizideki doğru yerine kaydırarak ekleyen, küçük dizilerde çok hızlı ($O(n)$) çalışan basit bir algoritmadır."
    if "heap sort" in q or "yığın sıralaması" in q:
        return "**Heap Sort**, diziyi bir Max-Heap ikili ağaç yapısına çevirip en büyük elemanı sona atarak $O(n \\log n)$ sürede sıralayan algoritmadır."
    if "sıralama" in q or "sorting" in q:
        return "**Sıralama Algoritmaları:**\n• **Insertion Sort:** $O(n^2)$ ortalama, küçük diziler için ideal.\n• **Merge Sort:** Her durumda $O(n \\log n)$, kararlı.\n• **Quick Sort:** $O(n \\log n)$ ortalama, pratikte en hızlı.\n• **Heap Sort:** $O(n \\log n)$, $O(1)$ ek bellek."

    if "rag" in q and ("nedir" in q or "ne" in q or "amacı" in q):
        return "**RAG (Retrieval-Augmented Generation)**, LLM modellerinin kendi eğitim verilerinde olmayan harici belgelerden anlık bilgi çekerek halüsinasyonsuz ve kaynaklı yanıt üretmesini sağlayan mimaridir."
    if "embedding" in q or "gömme" in q:
        return "**Embedding (Gömme)**, metin parçalarının anlamsal benzerliklerini matematiksel olarak koruyacak şekilde çok boyutlu yoğun sayısal vektörlere dönüştürülmesidir."
    if "cosine" in q or "kosinüs" in q:
        return "**Kosinüs Benzerliği (Cosine Similarity)**, iki vektör arasındaki açının kosinüsünü ölçerek uzunluktan bağımsız sadece anlamsal yön benzerliğini karşılaştıran metriktir."
    if "chunking" in q or "parçalama" in q:
        return "**Chunking**, büyük dokümanların semantik bütünlüğü bozulmadan modelin okuma kapasitesine uygun küçük bloklara (örn: 500 token) ayrılması işlemidir."

    if "turnaround" in q:
        return "**Turnaround Time**, bir sürecin sisteme girdiği an ile tamamen bittiği an arasında geçen toplam süredir (Turnaround = Bitiş - Giriş)."
    if "waiting time" in q or "bekleme süresi" in q:
        return "**Waiting Time**, bir sürecin CPU'da işlem görmek için hazır kuyruğunda (Ready Queue) bekleyerek geçirdiği toplam süredir."
    if "round robin" in q:
        return "**Round Robin (RR)**, her sürece eşit bir Time Quantum veren ve süresi dolan süreci kuyruk sonuna atan, arayüz duyarlılığı yüksek kesintili (preemptive) algoritmadır."
    if "page fault" in q or "sayfa hatası" in q:
        return "**Page Fault**, erişilmek istenen mantıksal sayfanın fiziksel RAM'de olmayıp diskte (Swap) olması durumunda işletim sistemi tarafından tetiklenen donanımsal kesmedir."
    if "tlb" in q:
        return "**TLB (Translation Lookaside Buffer)**, mantıksal sayfa numaralarını fiziksel çerçevelere çevirme işlemini hızlandıran MMU içindeki çok hızlı donanımsal önbellektir."

    bullet_points = []
    for line in raw_slide_text.split('\n'):
        line = line.strip().replace('•', '').replace('-', '').strip()
        if len(line) > 5 and not line.startswith("http"):
            bullet_points.append(f"• {line}")
    summary_bullets = '\n'.join(bullet_points[:4])
    return f"**`{doc_name}` belgesindeki ilgili açıklama:**\n\n{summary_bullets}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard_data():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, filename, file_type, page_count, uploaded_at FROM documents ORDER BY id DESC")
    docs = [{"id": r[0], "filename": r[1], "type": r[2], "pages": r[3], "uploaded_at": r[4]} for r in c.fetchall()]
    
    try:
        c.execute("SELECT COUNT(*), AVG(score), SUM(total_cards), SUM(duration_seconds), SUM(duration_minutes) FROM study_stats")
        s_row = c.fetchone()
        avg_score = round(s_row[1] or 0)
        questions_answered = s_row[2] or 0
        total_seconds = (s_row[3] or 0) + ((s_row[4] or 0) * 60)
    except Exception:
        avg_score = 0
        questions_answered = 0
        total_seconds = 0
    
    hours = total_seconds // 3600
    mins = (total_seconds % 3600) // 60
    conn.close()
    
    return jsonify({
        "study_time_hours": hours,
        "study_time_mins": mins,
        "study_streak": 12,
        "questions_answered": questions_answered,
        "efficiency_score": avg_score,
        "documents": docs
    })

@app.route('/api/documents', methods=['GET'])
def list_documents():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, filename, file_type, page_count, uploaded_at FROM documents ORDER BY id DESC")
    docs = [{"id": r[0], "filename": r[1], "type": r[2], "pages": r[3], "uploaded_at": r[4]} for r in c.fetchall()]
    conn.close()
    return jsonify({"documents": docs})

@app.route('/api/documents/<int:doc_id>', methods=['DELETE'])
def delete_document(doc_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT filepath FROM documents WHERE id = ?", (doc_id,))
        row = c.fetchone()
        if row and os.path.exists(row[0]):
            try:
                os.remove(row[0])
            except Exception:
                pass
        c.execute("DELETE FROM flashcards WHERE doc_id = ?", (doc_id,))
        c.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Belge silindi."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# AKILLI ROTASYONLU FLASHCARD GETİRME
@app.route('/api/flashcards', methods=['GET'])
def get_flashcards():
    doc_id = request.args.get('doc_id')
    exclude_ids_raw = request.args.get('exclude_ids', '')
    exclude_ids = [int(x) for x in exclude_ids_raw.split(',') if x.isdigit()]
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    if doc_id and doc_id != 'all':
        c.execute("SELECT id, topic, question, answer FROM flashcards WHERE doc_id = ?", (doc_id,))
        rows = c.fetchall()
        if len(rows) < 10:
            c.execute("SELECT id, filename, content FROM documents WHERE id = ?", (doc_id,))
            d = c.fetchone()
            if d:
                generate_curated_cards(d[0], d[1], d[2])
                c.execute("SELECT id, topic, question, answer FROM flashcards WHERE doc_id = ?", (doc_id,))
                rows = c.fetchall()
    else:
        c.execute("SELECT id, topic, question, answer FROM flashcards")
        rows = c.fetchall()
        if len(rows) < 10:
            c.execute("SELECT id, filename, content FROM documents")
            for d_id, fn, cnt in c.fetchall():
                generate_curated_cards(d_id, fn, cnt)
            c.execute("SELECT id, topic, question, answer FROM flashcards")
            rows = c.fetchall()
            
    conn.close()
    
    if not rows:
        return jsonify({"flashcards": [], "topic": "Belge Yüklenmedi"})
    
    all_cards = [{"id": r[0], "topic": r[1], "q": r[2], "a": r[3]} for r in rows]
    
    # Ekranda daha önce gösterilmemiş soruları önceliklendir
    unseen_cards = [card for card in all_cards if card["id"] not in exclude_ids]
    
    if len(unseen_cards) >= 5:
        random.shuffle(unseen_cards)
        selected_cards = unseen_cards[:5]
    else:
        # Eğer havuz bittiyse tüm havuzdan rastgele 5 yeni soru çek
        random.shuffle(all_cards)
        selected_cards = all_cards[:5]
    
    topic_name = "Tüm Dersler"
    if doc_id and doc_id != 'all' and len(selected_cards) > 0:
        topic_name = selected_cards[0]["topic"]
        
    return jsonify({"flashcards": selected_cards, "topic": topic_name})

# 5 YENİ SORU İLE TAZELEME ROTASI
@app.route('/api/regenerate-flashcards', methods=['POST'])
def regenerate_flashcards():
    data = request.json or {}
    doc_id = data.get('doc_id')
    exclude_ids = data.get('exclude_ids', [])
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    if doc_id and doc_id != 'all':
        c.execute("SELECT id, topic, question, answer FROM flashcards WHERE doc_id = ?", (doc_id,))
        rows = c.fetchall()
        if len(rows) < 10:
            c.execute("SELECT id, filename, content FROM documents WHERE id = ?", (doc_id,))
            d = c.fetchone()
            if d:
                generate_curated_cards(d[0], d[1], d[2])
            c.execute("SELECT id, topic, question, answer FROM flashcards WHERE doc_id = ?", (doc_id,))
            rows = c.fetchall()
    else:
        c.execute("SELECT id, topic, question, answer FROM flashcards")
        rows = c.fetchall()
        if len(rows) < 10:
            c.execute("DELETE FROM flashcards")
            c.execute("SELECT id, filename, content FROM documents")
            for d_id, fn, cnt in c.fetchall():
                generate_curated_cards(d_id, fn, cnt)
            c.execute("SELECT id, topic, question, answer FROM flashcards")
            rows = c.fetchall()
        
    conn.close()
    
    all_cards = [{"id": r[0], "topic": r[1], "q": r[2], "a": r[3]} for r in rows]
    unseen_cards = [card for card in all_cards if card["id"] not in exclude_ids]
    
    if len(unseen_cards) >= 5:
        random.shuffle(unseen_cards)
        selected_cards = unseen_cards[:5]
    else:
        random.shuffle(all_cards)
        selected_cards = all_cards[:5]
        
    return jsonify({"success": True, "flashcards": selected_cards})

@app.route('/api/upload', methods=['POST'])
def upload_file():
    try:
        if 'files' not in request.files:
            return jsonify({"success": False, "error": "Dosya seçilmedi"}), 400
        
        files = request.files.getlist('files')
        if not files or files[0].filename == '':
            return jsonify({"success": False, "error": "Dosya seçilmedi"}), 400

        uploaded = []
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        for file in files:
            if file and file.filename:
                filename = file.filename
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                
                _, ext = os.path.splitext(filename)
                content, pages = extract_text_and_pages(filepath)
                
                c.execute('''
                    INSERT INTO documents (filename, filepath, file_type, page_count, content)
                    VALUES (?, ?, ?, ?, ?)
                ''', (filename, filepath, ext.replace('.', '').upper(), pages, content))
                doc_id = c.lastrowid
                
                generate_curated_cards(doc_id, filename, content)
                uploaded.append({"id": doc_id, "filename": filename, "pages": pages, "type": ext})
                
        conn.commit()
        conn.close()
        return jsonify({"success": True, "uploaded": uploaded})
    except Exception as e:
        print("Upload Hatası:", e)
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/ask', methods=['POST'])
def ask_question():
    data = request.json
    raw_question = data.get('question', '').strip()
    question = raw_question.lower()
    
    if not question:
        return jsonify({"answer": "Lütfen bir soru yazınız.", "sources": []})
        
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT filename, content FROM documents ORDER BY id DESC")
    docs = c.fetchall()
    conn.close()
    
    if not docs:
        return jsonify({
            "answer": "Henüz herhangi bir ders belgesi yüklemediniz. Lütfen PDF veya TXT yükleyin.",
            "sources": []
        })
    
    specific_answer = synthesize_ai_answer(raw_question, docs[0][0], "1", docs[0][1])
    
    matched_doc = docs[0][0]
    for d_name, d_content in docs:
        if any(w in d_content.lower() for w in re.findall(r'\w+', question) if len(w) > 3):
            matched_doc = d_name
            break
            
    return jsonify({"answer": specific_answer, "sources": [matched_doc]})

@app.route('/api/save-session', methods=['POST'])
def save_session():
    data = request.json
    topic = data.get('topic', 'Genel')
    score = data.get('score', 0)
    known = data.get('known_count', 0)
    total = data.get('total_cards', 0)
    duration_sec = data.get('duration_seconds', 0)
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO study_stats (topic, score, known_count, total_cards, duration_seconds)
        VALUES (?, ?, ?, ?, ?)
    ''', (topic, score, known, total, duration_sec))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

if __name__ == '__main__':
    print("StudyMate AI Assistant hazır: http://127.0.0.1:5000")
    app.run(debug=True, port=5000)