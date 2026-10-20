import csv, re, os, collections

BASE_DIR = r'd:\.Candra\\Project\\stki-uts-A11.2023.15419-Candra-Wijayanto'
DOCS_DIR = os.path.join(BASE_DIR, 'Documents')
OUTPUT_EDA = os.path.join(DOCS_DIR, 'eda_dataset.csv')

POSITIF = {'bagus','indah','nyaman','bersih','murah','rekomendasi','rekomended','wajib','keren','mantap','suka','asyik','enak','sejuk','asri','luas','lengkap','ramah','memuaskan','puas','cocok','menyenangkan','terjangkau','segar','recommended','baik','ok','oke','top','good','great','perfect'}
NEGATIF  = {'kotor','mahal','sempit','jelek','buruk','kecewa','bising','rusak','panas','gelap','jauh','susah','sulit','ribet','macet','berbahaya','bau','jorok','kumuh','kurang','tidak','belum','banjir','licin','bahaya','ekstrim'}

FFLAGS = {
    'has_toilet':    ['toilet','kamar mandi'],
    'has_mushola':   ['mushola','musola','ibadah'],
    'has_listrik':   ['listrik','stop kontak','colokan'],
    'has_parkir':    ['parkir','parking'],
    'has_air_bersih':['air bersih'],
    'has_wifi':      ['wi-fi','wifi'],
    'has_warung':    ['warung','cafe','kantin','foodcourt'],
    'has_gazebo':    ['gazebo','pendopo','limasan'],
    'has_kolam':     ['kolam renang','berenang','umbul'],
    'has_pemandu':   ['pemandu','guide'],
}

def prov(lok):
    l=lok.lower()
    if 'diy' in l or 'yogyakarta' in l: return 'DIY'
    if 'jawa tengah' in l: return 'Jawa Tengah'
    return 'Lainnya'

def kab(lok): return lok.split(',')[0].strip()

def load(p):
    with open(p,encoding='utf-8',errors='replace') as f: return list(csv.DictReader(f))

corpus=load(os.path.join(DOCS_DIR,'corpus_master.csv'))
harga_r=load(os.path.join(DOCS_DIR,'input_harga.csv'))
fas_r=load(os.path.join(DOCS_DIR,'input_fasilitas.csv'))
info_r=load(os.path.join(DOCS_DIR,'input_info_statis.csv'))

harga_d=collections.defaultdict(list)
for r in harga_r:
    try: harga_d[r['Nama_Tempat'].strip()].append({'item':r['item'].strip(),'harga':int(r['harga']),'kat':r['kategori'].strip()})
    except: pass

def h_stats(n):
    its=harga_d.get(n,[])
    if not its: return dict(harga_tiket_masuk=None,harga_min=None,harga_max=None,harga_rata2=None,jumlah_item_harga=0)
    prices=[i['harga'] for i in its]
    tikwajib=[i['harga'] for i in its if i['kat']=='biaya wajib' and any(k in i['item'].lower() for k in ['tiket masuk','biaya camping','ground only','reguler pack'])]
    return dict(harga_tiket_masuk=min(tikwajib) if tikwajib else None,harga_min=min(prices),harga_max=max(prices),harga_rata2=round(sum(prices)/len(prices),2),jumlah_item_harga=len(its))

def kh(t):
    if t is None: return 'Tidak Diketahui'
    if t<=10000: return 'Murah'
    if t<=25000: return 'Sedang'
    return 'Mahal'

fas_d=collections.defaultdict(list)
for r in fas_r: fas_d[r['Nama_Tempat'].strip()].append(r['Fasilitas'].strip())

def f_feats(n):
    fl=fas_d.get(n,[])
    fg=' '.join(fl).lower()
    flags={fn:('Ya' if any(kw in fg for kw in kws) else 'Tidak') for fn,kws in FFLAGS.items()}
    return dict(jumlah_fasilitas=len(fl),**flags)

info_d={r['Nama_Tempat'].strip():r for r in info_r}

def waktu(n):
    w=info_d.get(n,{}).get('Waktu_Buka','')
    nums=re.findall(r'[0-9][0-9]:[0-9][0-9]',w)
    return nums[0] if nums else '12:00'

valid=[r for r in corpus if r['Nama_Tempat'].strip()]
rat_d=collections.defaultdict(list)
for r in valid:
    try: rat_d[r['Nama_Tempat'].strip()].append(int(r['Rating']))
    except: pass

def r_stats(n):
    vs=rat_d.get(n,[])
    if not vs: return dict(rating_rata2=None,jumlah_ulasan=0,rating_min=None,rating_max=None)
    return dict(rating_rata2=round(sum(vs)/len(vs),2),jumlah_ulasan=len(vs),rating_min=min(vs),rating_max=max(vs))

def sentimen(t):
    if not t.strip(): return 'Netral'
    ws=re.findall(r'[a-zA-Z]+',t.lower())
    p=sum(1 for w in ws if w in POSITIF)
    n=sum(1 for w in ws if w in NEGATIF)
    return 'Positif' if p>n else ('Negatif' if n>p else 'Netral')

def krat(s):
    try:
        v=int(s)
        if v<=2: return 'Buruk'
        if v==3: return 'Cukup'
        if v==4: return 'Baik'
        return 'Sangat Baik'
    except: return 'Tidak Ada'

places=sorted(set(r['Nama_Tempat'].strip() for r in valid))
cache={n:{**h_stats(n),**f_feats(n),**r_stats(n),'waktu_checkin':waktu(n)} for n in places}

eda=[]
for r in valid:
    n=r['Nama_Tempat'].strip()
    lok=r['Lokasi'].strip()
    rt=r['Rating'].strip()
    tx=r['Teks_Mentah'].strip()
    c=cache[n]
    row={
        'Doc_ID':r['Doc_ID'],'Nama_Tempat':n,
        'Lokasi':lok,'Provinsi':prov(lok),'Kabupaten':kab(lok),
        'Kategori_Harga':kh(c['harga_tiket_masuk']),'Waktu_CheckIn':c['waktu_checkin'],
        'Has_Toilet':c['has_toilet'],'Has_Mushola':c['has_mushola'],'Has_Listrik':c['has_listrik'],
        'Has_Parkir':c['has_parkir'],'Has_Air_Bersih':c['has_air_bersih'],'Has_WiFi':c['has_wifi'],
        'Has_Warung':c['has_warung'],'Has_Gazebo':c['has_gazebo'],'Has_Kolam':c['has_kolam'],'Has_Pemandu':c['has_pemandu'],
        'Rating':rt if rt else None,'Kategori_Rating':krat(rt),'Sentimen_Ulasan':sentimen(tx),
        'Harga_Tiket_Masuk':c['harga_tiket_masuk'],'Harga_Min':c['harga_min'],'Harga_Max':c['harga_max'],
        'Harga_Rata2':c['harga_rata2'],'Jumlah_Item_Harga':c['jumlah_item_harga'],
        'Jumlah_Fasilitas':c['jumlah_fasilitas'],
        'Rating_Rata2_Tempat':c['rating_rata2'],'Jumlah_Ulasan_Tempat':c['jumlah_ulasan'],
        'Rating_Min_Tempat':c['rating_min'],'Rating_Max_Tempat':c['rating_max'],
        'Panjang_Teks':len(tx.split()) if tx else 0,'Teks_Mentah':tx,
    }
    eda.append(row)

with open(OUTPUT_EDA,'w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(eda[0].keys()))
    w.writeheader()
    w.writerows(eda)

print('DONE',len(eda),'rows',len(eda[0]),'cols')
print('SENTIMEN:',dict(collections.Counter(r['Sentimen_Ulasan'] for r in eda)))
print('RATING:',dict(collections.Counter(r['Kategori_Rating'] for r in eda)))
print('PROVINSI:',dict(collections.Counter(r['Provinsi'] for r in eda)))
print('HARGA_CAT:',dict(collections.Counter(r['Kategori_Harga'] for r in eda)))
