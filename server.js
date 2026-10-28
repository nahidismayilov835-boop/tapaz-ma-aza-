const express = require('express');
const multer = require('multer');
const Datastore = require('nedb');
const path = require('path');

const app = express();
const PORT = 3000;

// Verilənlər bazaları (fayllar avtomatik yaradılacaq)
const dbElanlar = new Datastore({ filename: 'elanlar.db', autoload: true });
const dbAdminler = new Datastore({ filename: 'adminler.db', autoload: true });

// İlkin admin qeydiyyatı (Əgər yoxdursa)
dbAdminler.findOne({ istifadeciAdi: 'admin' }, (err, doc) => {
    if (!doc) {
        dbAdminler.insert({ istifadeciAdi: 'admin', parol: '1234' });
    }
});

app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static('public'));
app.use('/uploads', express.static('uploads'));

// Şəkil yükləmə ayarları (Multer)
const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        const uploadDir = path.join(__dirname, 'public/uploads');
        const fs = require('fs');
        if (!fs.existsSync(uploadDir)){
            fs.mkdirSync(uploadDir, { recursive: true });
        }
        cb(null, uploadDir);
    },
    filename: (req, file, cb) => {
        cb(null, Date.now() + '-' + file.originalname);
    }
});
const upload = multer({ storage: storage });

// 1. Elanları gətir
app.get('/api/elanlar', (req, res) => {
    dbElanlar.find({}).sort({ timestamp: -1 }).exec((err, docs) => {
        res.json(docs);
    });
});

// 2. Yeni elan əlavə et (şəkil ilə)
app.post('/api/elanlar', upload.single('sekil'), (req, res) => {
    const { kategoriya, basliq, qiymet, seher, melumat } = req.body;
    const sekilYolu = req.file ? `/uploads/${req.file.filename}` : '';

    const yeniElan = {
        kategoriya,
        basliq,
        qiymet,
        seher,
        melumat,
        sekil: sekilYolu,
        timestamp: Date.now()
    };

    dbElanlar.insert(yeniElan, (err, newDoc) => {
        if (err) return res.status(500).json({ success: false });
        res.json({ success: true, elan: newDoc });
    });
});

// 3. Elanı sil (Admin üçün)
app.delete('/api/elanlar/:id', (req, res) => {
    const id = req.params.id;
    dbElanlar.remove({ _id: id }, {}, (err, numRemoved) => {
        if (err) return res.status(500).json({ success: false });
        res.json({ success: true });
    });
});

// 4. Admin Giriş
app.post('/api/giris', (req, res) => {
    const { istifadeciAdi, parol } = req.body;
    dbAdminler.findOne({ istifadeciAdi: istifadeciAdi.trim(), parol: parol.trim() }, (err, user) => {
        if (user) {
            res.json({ success: true });
        } else {
            res.json({ success: false, message: 'İstifadəçi adı və ya parol səhvdir!' });
        }
    });
});

// 5. Admin Qeydiyyatı (Gizli açar yoxlanışı ilə: master123)
app.post('/api/qeydiyyat', (req, res) => {
    const { istifadeciAdi, parol, gizliAcar } = req.body;
    if (gizliAcar !== 'master123') {
        return res.json({ success: false, message: 'Gizli açar yanlışdır!' });
    }

    dbAdminler.findOne({ istifadeciAdi: istifadeciAdi.trim() }, (err, existing) => {
        if (existing) {
            return res.json({ success: false, message: 'Bu istifadəçi adı artıq mövcuddur!' });
        }
        dbAdminler.insert({ istifadeciAdi: istifadeciAdi.trim(), parol: parol.trim() }, (err, newAdmin) => {
            res.json({ success: true });
        });
    });
});

app.listen(PORT, () => {
    console.log(`Server işləyir: http://localhost:${PORT}`);
});