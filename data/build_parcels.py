#!/usr/bin/env python3
import json, math, random
from pathlib import Path
random.seed(20260916)

CENTERS = [
    (29.45,-23.90,'Polokwane'),(30.16,-23.83,'Tzaneen'),(29.90,-23.05,'Makhado'),
    (28.98,-24.18,'Mokopane'),(28.41,-24.70,'Modimolle'),(28.28,-24.88,'Bela-Bela'),
    (31.14,-23.94,'Phalaborwa'),(30.96,-24.35,'Hoedspruit'),(30.48,-22.95,'Thohoyandou'),
    (29.39,-25.17,'Groblersdal'),(29.29,-24.97,'Marble Hall'),(30.72,-23.31,'Giyani'),
]
LAND_TYPES = [
    'Hu — Hutton: deep red apedal soils of the Bushveld',
    'Cv — Clovelly: yellow-brown apedal soils, moderate depth',
    'Sd — Shortlands: red structured soils on basic parent material',
    'Gs — Glenrosa: shallow soils on granite / gneiss',
    'Ia — alluvial soils of the Olifants / Letaba floodplains',
    'Ms — Mispah: very shallow lithosols on rock',
]
CLIMATE = [
    ('Summer-rainfall subtropical Lowveld',620),
    ('Summer-rainfall semi-arid Bushveld',480),
    ('Summer-rainfall, escarpment / mistbelt margin',980),
    ('Summer-rainfall, dry western Limpopo',380),
    ('Summer-rainfall, Soutpansberg foothills',720),
    ('Summer-rainfall, Springbok Flats',540),
]
RIVERS = [
    ('Olifants River','Olifants'),('Great Letaba River','Letaba'),('Levuvhu River','Luvuvhu'),
    ('Mogalakwena River','Mogalakwena'),('Sand River','Sand'),('Palala River','Palala'),
    ('Blyde River','Blyde'),('Nzhelele River','Nzhelele'),
]
RELIEF = ['Bushveld plain','Lowveld plain','escarpment foothill','Soutpansberg foothill','undulating granite veld','river valley floor']
SETTLEMENT = ['farm','farm','farm','farm','rural','farm']
FARM_STEMS = ['Welgevonden','Doornfontein','Nooitgedacht','Klipfontein','Rietvlei','Groenfontein','Zandrivier','Mooiplaats','Driefontein','Elandsfontein','Krokodilpoort','Langgewacht','Sterkfontein','Vlakfontein','Boschhoek','Cyferfontein','Tweefontein','Wildebeesfontein','Modderfontein','Hartbeestfontein','Olifantsdrift','Letabadrift','Soutpansberg','Waterpoort','Makhadohoek']

ENTERPRISE = {
    'Polokwane': {
        'crops': ['dryland sorghum / millet', 'maize only where rainfall and soil depth allow', 'irrigated vegetables and lucerne if water rights exist'],
        'livestock_game': ['beef cattle (Bonsmara / Nguni-type on bushveld)', 'impala', 'kudu', 'blue wildebeest'],
        'fit': 'Semi-arid Bushveld. Game and cattle usually fit better than orchards without irrigation.',
    },
    'Tzaneen': {
        'crops': ['avocado', 'mango', 'macadamia', 'litchi', 'banana', 'tea / timber on mistbelt slopes'],
        'livestock_game': ['limited cattle on leftover veld', 'not a first-choice extensive game area'],
        'fit': 'Escarpment / mistbelt. Subtropical tree crops dominate where frost risk is low.',
    },
    'Makhado': {
        'crops': ['avocado and macadamia on Soutpansberg slopes', 'irrigated citrus in pockets', 'forestry on higher rainfall faces'],
        'livestock_game': ['beef cattle', 'impala', 'kudu', 'nyala on thicker bush'],
        'fit': 'Split landscape: fruit on the mountain, cattle and game on the bushveld floor.',
    },
    'Mokopane': {
        'crops': ['sunflower / sorghum on dryland', 'citrus or vegetables only under irrigation'],
        'livestock_game': ['beef cattle', 'game ranching (impala, kudu, gemsbok on open bushveld)', 'goats on mixed veld'],
        'fit': 'Dry Bushveld. Hunting and cattle are the default; cropping needs water.',
    },
    'Modimolle': {
        'crops': ['potatoes and vegetables under irrigation', 'citrus in frost-sheltered pockets'],
        'livestock_game': ['beef cattle', 'game (impala, kudu, giraffe on larger portions)', 'wildlife tourism'],
        'fit': 'Waterberg fringe. Mix of irrigation pockets and extensive game/cattle.',
    },
    'Bela-Bela': {
        'crops': ['irrigated lucerne and fodder', 'limited dryland grain'],
        'livestock_game': ['game ranching', 'beef cattle', 'wildlife / hospitality'],
        'fit': 'Warm Bushveld. Game and tourism often out-earn dryland crops.',
    },
    'Phalaborwa': {
        'crops': ['mango', 'citrus where irrigation and frost allow'],
        'livestock_game': ['game (impala, kudu, buffalo on suitable fenced ranches)', 'beef cattle', 'wildlife tourism'],
        'fit': 'Lowveld. Heat-tolerant fruit plus game; frost-sensitive orchards only with water.',
    },
    'Hoedspruit': {
        'crops': ['mango', 'citrus', 'specialty subtropical fruit under irrigation'],
        'livestock_game': ['game ranching and photo-tourism', 'limited cattle'],
        'fit': 'Wildlife Lowveld. Game and irrigated mango/citrus are the regional pattern.',
    },
    'Thohoyandou': {
        'crops': ['mango', 'citrus', 'banana', 'groundnuts', 'maize on deeper soils'],
        'livestock_game': ['cattle', 'goats', 'limited game on larger bush portions'],
        'fit': 'Vhembe. Subtropical fruit and smallholder cattle/goats; confirm frost and water.',
    },
    'Groblersdal': {
        'crops': ['citrus', 'table grapes', 'cotton', 'wheat', 'maize', 'irrigated vegetables'],
        'livestock_game': ['cattle on non-irrigated veld', 'game only on larger uncultivated portions'],
        'fit': 'Loskop irrigation district. High-value irrigated crops beat extensive game here.',
    },
    'Marble Hall': {
        'crops': ['citrus', 'cotton', 'vegetables', 'wheat', 'maize under irrigation'],
        'livestock_game': ['cattle on residual veld'],
        'fit': 'Irrigation scheme. Planted enterprises first; game is secondary.',
    },
    'Giyani': {
        'crops': ['mango', 'citrus pockets', 'groundnuts', 'maize where soil depth allows'],
        'livestock_game': ['cattle', 'goats', 'impala on bushveld portions'],
        'fit': 'Mopani Lowveld. Mixed livestock with fruit where water exists.',
    },
}

def poly_area_ha(coords):
    lat0 = coords[0][1]; mlat=111320.0; mlon=111320.0*math.cos(math.radians(lat0))
    pts=[(x*mlon,y*mlat) for x,y in coords]; s=0.0
    for i in range(len(pts)-1):
        s += pts[i][0]*pts[i+1][1]-pts[i+1][0]*pts[i][1]
    return abs(s)/2.0/10000.0

def make_poly(cx,cy,half_w,half_h,rot,n=6):
    pts=[]
    for i in range(n):
        ang=2*math.pi*i/n+rot; jx,jy=random.uniform(0.72,1.18),random.uniform(0.72,1.18)
        pts.append([round(cx+half_w*jx*math.cos(ang),6), round(cy+half_h*jy*math.sin(ang),6)])
    pts.append(pts[0]); return pts

def centroid(coords):
    xs=[p[0] for p in coords[:-1]]; ys=[p[1] for p in coords[:-1]]
    return [round(sum(xs)/len(xs),6), round(sum(ys)/len(ys),6)]

features=[]; idx=0
for cluster_i,(bx,by,locality) in enumerate(CENTERS):
    for j in range(7):
        idx += 1
        cx,cy=bx+random.uniform(-0.14,0.14), by+random.uniform(-0.10,0.10)
        target_ha=random.choice([18,28,40,55,80,120,180,240,36,70])
        side_km=math.sqrt(target_ha/100.0)
        half_w=(side_km/2)/(111.32*math.cos(math.radians(cy)))*random.uniform(0.7,1.5)
        half_h=(side_km/2)/111.32*random.uniform(0.7,1.4)
        ring=make_poly(cx,cy,half_w,half_h,random.uniform(0,math.pi),n=random.choice([5,6,7,8]))
        c=centroid(ring); ha=round(poly_area_ha(ring),1)
        stem=FARM_STEMS[(idx-1)%len(FARM_STEMS)]
        name=f'Demo portion {random.choice([1,2,3,4,5,6,8,12])} of farm {stem} ({locality})'
        lt=LAND_TYPES[(idx+cluster_i)%len(LAND_TYPES)]
        cl_class,rain=CLIMATE[(idx*3+cluster_i)%len(CLIMATE)]
        river,catch=RIVERS[(idx+cluster_i*2)%len(RIVERS)]
        pid=f'fm-limpopo-{idx:04d}'
        ent=dict(ENTERPRISE[locality])
        if lt.startswith('Ms') or lt.startswith('Gs'):
            ent['fit'] = ent['fit'] + ' Shallow soils on this parcel favour veld, cattle and game over orchards.'
        if lt.startswith('Ia'):
            ent['fit'] = ent['fit'] + ' Alluvial strip: irrigation crops possible if water law and flood risk allow.'
        features.append({'type':'Feature','id':pid,'geometry':{'type':'Polygon','coordinates':[ring]},'properties':{
            'parcel_id':pid,'sg_code':None,'name':name,'extent_ha':ha,
            'layer_settlement':SETTLEMENT[(idx+j)%len(SETTLEMENT)],'centroid':c,'locality':locality,
            'intelligence':{
                'land_type':{'class':lt,'source':'Demo classification styled on ARC Land Type (not an official sample)','scale':'1:250000','as_of':'demo','confidence':'indicative'},
                'climate':{'class':cl_class,'mean_annual_rainfall_mm':rain,'source':'Demo band styled on Schulze / Limpopo summer-rainfall (not a station record)','scale':'regional','as_of':'demo','confidence':'indicative'},
                'hydro':{'nearest_river':river,'km':round(random.uniform(0.4,8.0),1),'in_catchment':catch},
                'relief':{'description':RELIEF[(idx+j)%len(RELIEF)],'source':'DEM (demo label from location, not a surveyed contour)'},
                'settlement':{'class':SETTLEMENT[(idx+j)%len(SETTLEMENT)],'source':'SANLC-style reclass (demo)','as_of':'2020'},
                'enterprise':{
                    'crops':ent['crops'],
                    'livestock_game':ent['livestock_game'],
                    'fit':ent['fit'],
                    'source':'Indicative regional match for Limpopo agro-ecology (not a farm plan, soil test, or stocking rate)',
                    'scale':'regional',
                    'as_of':'demo',
                    'confidence':'indicative',
                },
            }},
        })

open(str(Path(__file__).resolve().parent/'parcels.geojson'),'w').write(json.dumps({
    'type':'FeatureCollection','name':'farmland_limpopo_demo_parcels','features':features}))
