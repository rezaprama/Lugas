# Lugas

**Tulisan jernih, makna tetap.** Skill gratis dan lokal untuk memparafrasekan, menyunting, mengoreksi, dan menerjemahkan naskah ilmiah serta teknis **berbahasa Indonesia dan Inggris** tanpa mengubah angka, sitasi, negasi, atau kekuatan klaim.

*Sampai v0.2, Lugas bernama **RhetoriLex**. Tautan lama, perintah `rhetorilex`, `import rhetorilex`, dan ID stabil `RLX-*` tetap berfungsi; lihat [Migrasi](#migrasi-dari-rhetorilex).*

[![CI](https://github.com/rezaprama/Lugas/actions/workflows/ci.yml/badge.svg)](https://github.com/rezaprama/Lugas/actions/workflows/ci.yml)
[![Pages](https://github.com/rezaprama/Lugas/actions/workflows/pages.yml/badge.svg)](https://github.com/rezaprama/Lugas/actions/workflows/pages.yml)
[![Lisensi: Apache-2.0](https://img.shields.io/badge/kode-Apache--2.0-0f766e.svg)](LICENSE)
[![Data: CC BY 4.0](https://img.shields.io/badge/data-CC%20BY%204.0-0f766e.svg)](LICENSES/CC-BY-4.0.txt)

[Alat parafrasa](https://rezaprama.github.io/Lugas/id/alat-parafrasa/) · [English](README.md) · [Agent Skill](skills/lugas/SKILL.md) · [Benchmark](docs/benchmarks.md) · [Provenans](PROVENANCE.md)

*Lugas* berarti jelas, langsung, dan tidak bertele-tele. Begitu pula cara kerjanya: pahami tujuan, periksa bukti, baru pilih kata.

## Yang dikerjakan

| Pekerjaan | Contoh permintaan | Yang dijaga tetap |
| --- | --- | --- |
| Koreksi | "Koreksi ejaan saja" | susunan kalimat, pilihan kata yang sudah benar |
| Sunting | "Rapikan bahasanya" | klaim, urutan argumen, istilah teknis |
| Parafrase | "Parafrasekan untuk tinjauan pustaka" | fakta, angka, sitasi, kekuatan klaim |
| Terjemah ID↔EN | "Terjemahkan ke bahasa Inggris akademik" | semuanya, kecuali koma↔titik desimal |
| Ringkas | "Ringkas untuk abstrak" | fakta yang dipertahankan, kontras, dan batasan |

Lugas tidak mengarang data atau rujukan, tidak mengubah hubungan menjadi sebab-akibat atau "tidak signifikan" menjadi "tidak berpengaruh", dan tidak menjanjikan lolos uji kemiripan atau detektor AI. Penulis tetap bertanggung jawab atas teks akhir.

## Tiga cara memakai

**1. Agent Skill (produk utama).** Salin `skills/lugas` ke `.agents/skills/lugas` (satu proyek) atau `~/.codex/skills/lugas` (semua proyek), atau pasang dengan:

```text
$skill-installer https://github.com/rezaprama/Lugas/tree/main/skills/lugas
```

Skill memuat sekitar 5,9 KB instruksi, ditambah rujukan bahasa Indonesia (5,6 KB) hanya untuk naskah Indonesia. Skill memilih jenis pekerjaan, mengunci elemen yang dilindungi, lalu menutup dengan pemeriksaan lokal.

**2. Pemeriksa makna luring (tanpa model, tanpa internet).** Bisa dipakai untuk keluaran model apa pun, termasuk model lokal:

```bash
python skills/lugas/scripts/guard.py check sumber.txt hasil.txt      # --translation / --summary
python skills/lugas/scripts/guard.py lint naskah.txt                 # petunjuk EYD V/KBBI dan kalke Inggris
```

Pemeriksa membandingkan angka (paham koma desimal), statistik, sitasi, kutipan, negasi (*tidak, bukan, belum, tanpa*), hedging, hubungan vs sebab-akibat, arah, cakupan, dan ketidaksignifikanan. Kode keluar 1 berarti ada temuan `high`. Ini penyaring leksikal, bukan bukti makna terjaga.

**3. Alat web (PWA).** [Alat parafrasa](https://rezaprama.github.io/Lugas/id/alat-parafrasa/). Pilih pekerjaan dan bahasa keluaran, buat prompt ringkas untuk model mana pun, tempel jawabannya, lalu jalankan pemeriksaan makna yang sama di browser. Opsional: panggil endpoint OpenAI-compatible atau Gemini milik Anda (batas 90 detik, tombol batal, peringatan jawaban terpotong). Tidak ada teks yang dikirim kecuali Anda mengisi endpoint; situs ini tanpa backend, akun, atau analytics.

## CLI dan API Python

```bash
git clone https://github.com/rezaprama/Lugas.git && cd Lugas
python -m pip install -e .
lugas check sumber.txt hasil.txt
lugas lint naskah.txt
lugas search "cautious interpretation" --stage discussion --limit 3
lugas explain RLX-QUA-001
```

```python
from lugas import Catalog, check_rewrite

for temuan in check_rewrite("Responden belum pernah dilatih.", "Responden sudah pernah dilatih."):
    print(temuan.severity, temuan.code)          # high negation-lost
```

Katalog pencarian berisi 96 pola bahasa Inggris orisinal untuk 24 fungsi retoris dan 144 writing skill (64 akademik, 66 ilmiah, 14 parafrasa) dengan deskripsi berbahasa Indonesia. Pola adalah kandidat, bukan otoritas.

## Bukti (diukur 22 Oktober 2026)

Metode, fixture, dan batasan lengkap: [docs/benchmarks.md](docs/benchmarks.md).

- **Pemeriksa makna vs pemeriksaan v0.2** pada set uji yang ditulis terpisah (24 kasus, 47 hasil keliru): pemeriksaan substring v0.2 menangkap 49% dengan 25% alarm palsu; pemeriksa baru menangkap 81% dengan 29% alarm palsu sebelum penyesuaian, dan 85% dengan 0% setelah perbaikan yang dipandu set itu (angka kedua cenderung optimistis).
- **Uji model** (satu model Claude frontier, 16 tugas ID/EN, juri LLM buta): kesalahan makna 3 dengan prompt biasa, 0 dengan skill v0.2, 0 dengan Lugas v0.3. Kealamian setara (4,6–4,8 dari 5). Lugas **belum** menghemat token dibanding v0.2 pada model ini (sekitar 11 KB instruksi masing-masing); Lugas menambah kaidah Indonesia dengan biaya yang sama.
- **Prompt alat web** turun dari 788 ke 576 karakter per permintaan (−27%) sambil menambah kendali bahasa keluaran dan perlindungan injeksi.

Belum diukur: model kecil/lokal, latensi dan biaya per provider, penilaian pakar manusia, data lapangan Lighthouse.

## Model katalog

Setiap entri kanonis memuat:

| Field | Fungsi |
| --- | --- |
| `function` | Tujuan komunikasi stabil seperti `identify_gap` atau `state_limitation` |
| `template` | Kalimat original dengan slot bernama yang eksplisit |
| `stage` | Tahap manuskrip yang kompatibel |
| `claim_strength` | `tentative`, `bounded`, `assertive`, atau `causal` |
| `evidence_requirement` | `none`, `contextual`, `observational`, `direct`, atau `convergent` |
| `causal_design_required` | Mencegah pola kausal dipakai sebagai prosa umum |
| `risk` | Tingkat review editorial: `low`, `medium`, atau `high` |
| `provenance` | Catatan wajib `original_editorial` dan `source_reuse: false` |

Lihat [data/taxonomy/taxonomy.v1.json](data/taxonomy/taxonomy.v1.json),
[data/contracts/evidence-claim.v1.json](data/contracts/evidence-claim.v1.json), dan
[docs/data-model.md](docs/data-model.md).

## Riset dan discovery

Model ini berorientasi pada riset tentang genre dan gerakan retoris
([10.1017/CBO9781139524827](https://doi.org/10.1017/CBO9781139524827)), stance dan
interaksi pembaca ([10.1177/1461445605050365](https://doi.org/10.1177/1461445605050365)),
serta fraseologi korpus dan variasi disiplin
([10.1016/j.jeap.2019.01.003](https://doi.org/10.1016/j.jeap.2019.01.003)). Sumber ini
mengarahkan desain original; prosa, contoh, dan inventarisnya tidak diambil. Provenance
riset lengkap tersedia di [PROVENANCE.md](PROVENANCE.md).

Positioning publik juga diukur, bukan ditebak. [Studi discovery](docs/discovery-research.md)
dan [landscape GitHub](docs/github-landscape.md) merekam query, metrik, timestamp, batas
interpretasi, dan bukti terstruktur dalam [data/discovery](data/discovery/). Jumlah repo
GitHub adalah sinyal suplai/indeks—bukan volume pencarian web, permintaan pengguna,
adopsi, atau kualitas. Pengukuran langsung Google Trends tidak tersedia, sehingga
nilainya dicatat sebagai `null`; tidak ada volume proxy yang dikarang.

## Build dan verifikasi

```bash
python scripts/validate_data.py
python scripts/build_data.py
python -m unittest discover -s tests -v
python scripts/package_plugin.py --output dist/lugas-plugin.zip
```

Test suite memeriksa schema, provenance, kesamaan slot, kebutuhan bukti, guard kausal,
build deterministik, perilaku retrieval, routing benchmark beku, perilaku CLI, dan
keamanan kontrak. Continuous integration mengulang build dan membandingkan checksum.

## Arsitektur

```text
data/canonical/catalog.v1.jsonl
          |
          +--> data/dist/*                    artefak data portabel
          +--> src/lugas/resources/*          paket Python
          +--> skills/lugas/assets/*     Agent Skill offline
          +--> docs/data/phrases.json          artefak Pages hasil assembly

taxonomy + JSON Schema + kontrak bukti
          |
          +--> validator --> tests --> gate rilis deterministik
```

Explorer browser dan workbench parafrasa berupa HTML, CSS, dan JavaScript statis. Tidak ada akun, backend, dependensi CDN, telemetry, atau database naskah Lugas. Panggilan endpoint berjalan langsung dari browser pengguna ke endpoint yang dimasukkan. Layanan hosted dengan shared key di masa depan membutuhkan backend dengan secret di server, penyimpanan kuota, perlindungan abuse, dan logging naskah mati secara default.

## Batas sumber dan hak penggunaan

Workbook privat yang diberikan untuk proyek ini memiliki ketentuan penggunaan akademik
dan larangan distribusi. File hanya diaudit lokal untuk struktur agregat non-ekspresif
dan sinyal kualitas. File diabaikan Git; isi sel dan labelnya tidak masuk repo; semua
kandidat migrasi tetap unresolved; dan **nol item turunan sumber dipromosikan**.

Manchester Academic Phrasebank hanya menjadi konteks konseptual dan sitasi; inventaris
frasanya tidak diimpor atau ditulis ulang. BAWE dikecualikan. Elsevier OA CC-BY Corpus
v3 hanya terdaftar sebagai kemungkinan sumber validasi agregat di masa depan dan belum
diingest. Baca [PROVENANCE.md](PROVENANCE.md),
[source registry](data/sources/source-registry.yaml), dan
[laporan audit](reports/xlsx-audit.md).

## Kontribusi

Kontribusi diterima jika kalimat ditulis mandiri dan aman terhadap bukti. Mulai dari
[CONTRIBUTING.md](CONTRIBUTING.md). Pola baru membutuhkan provenance, slot bernama,
kompatibilitas taxonomy, metadata bukti, review orisinalitas, dan tes. Jangan unggah
workbook terbatas, inventaris sumber, manuskrip, atau kutipan korpus ke issue atau pull
request.

Masalah keamanan, draft rahasia, provenance, dan hak penggunaan dilaporkan lewat proses
privat di [SECURITY.md](SECURITY.md). Keputusan proyek dicatat di
[GOVERNANCE.md](GOVERNANCE.md) dan [IMPLEMENTATION_LOG.md](IMPLEMENTATION_LOG.md).

## Migrasi dari RhetoriLex

| Lama | Baru | Status |
| --- | --- | --- |
| `github.com/rezaprama/RhetoriLex` | `github.com/rezaprama/Lugas` | Nama lama kini menjadi repo publik khusus pengalih Pages; ubah remote Git ke `Lugas` untuk source dan rilis |
| `rezaprama.github.io/RhetoriLex/...` | `rezaprama.github.io/Lugas/...` | halaman pengalih per rute; service worker lama dicabut |
| perintah `rhetorilex`, `python -m rhetorilex` | `lugas` | alias dipertahankan di seri 0.x |
| `import rhetorilex` | `import lugas` | alias dengan `DeprecationWarning` |
| `skills/rhetorilex`, `$rhetorilex` | `skills/lugas`, `$lugas` | skill menjawab kedua nama |
| ID `RLX-*`, berkas data `rhetorilex-v0.2.*`, ID format | tidak berubah | pengenal stabil |

Rollback tidak lagi cukup dengan mengganti nama repo: nama lama dipakai repo publik pengalih Pages. Pindahkan atau atur ulang repo pengalih sebelum mempertimbangkan rollback; periksa ulang Pages dan remote Git.

## Proyek dan pembuat

Lugas dibuat dan dikelola oleh
[Reza Prama Arviandi](https://rezaprama.com). Riwayat rilis tersedia di
[CHANGELOG.md](CHANGELOG.md); rencana publik tersedia di [ROADMAP.md](ROADMAP.md).

## Lisensi dan sitasi

Kode, konfigurasi, tes, dan Agent Skill memakai Apache-2.0. Data original, laporan,
benchmark, aset, dan dokumentasi memakai CC BY 4.0. Pemetaan path machine-readable
tersedia di [REUSE.toml](REUSE.toml); status pihak ketiga tersedia di
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

Metadata sitasi versi 0.3.0 tersedia di [CITATION.cff](CITATION.cff). Dokumen lisensi
menyatakan kebijakan proyek, bukan nasihat hukum.
