from objects import City

# miestai
cities = {
    'airija': City('airija', 130.5, 348),
    'anglija': City('anglija', 217.5, 391.5),
    'armenija': City('armenija', 869.5, 617.5),
    'austrija': City('austrija', 413, 522),
    'azerbaidzanas': City('azerbaidzanas', 934, 591),

    'balkanu-centras': City('balkanu-centras', 478.5, 595.5),
    'balkanu-pietus': City('balkanu-pietus', 500, 674),
    'balkanu-siaure': City('balkanu-siaure', 435, 556.5),
    'baltarusija': City('baltarusija', 600, 400),
    'beneliuksas': City('beneliuksas', 283.5, 433.5),

    'bulgarija': City('bulgarija', 550, 633.5),
    'cekija': City('cekija', 416.5, 483.5),
    'danija': City('danija', 350, 350),
    'estija': City('estija', 550, 300),
    'islandija': City('islandija', 138, 87),

    'ispanijos-siaure': City('ispanijos-siaure', 97, 570),
    'ispanijos-pietus': City('ispanijos-pietus', 60, 662),
    'italija': City('italija', 366.5, 633.5),
    'karaliaucius': City('karaliaucius', 483.5, 370),
    'latvija': City('latvija', 550, 333.5),
    'lenkija': City('lenkija', 483.5, 416.5),

    'lietuva': City('lietuva', 533.5, 366.5),
    'moldova': City('moldova', 616.5, 550),
    'norvegijos-siaure': City('norvegijos-siaure', 507, 71),
    'norvegijos-pietus': City('norvegijos-pietus', 350, 233.5),
    'portugalija': City('portugalija', 40, 600),
    'prancuzijos-siaure': City('prancuzijos-siaure', 242, 482),
    'prancuzijos-pietus': City('prancuzijos-pietus', 209, 571),

    'rumunija': City('rumunija', 566.5, 566.5),
    'rusijos-siaure': City('rusijos-siaure', 766.5, 266.5),
    'rusijos-centras': City('rusijos-centras', 792, 398),
    'rusijos-pietus': City('rusijos-pietus', 798, 531),
    'rusijos-rytai': City('rusijos-rytai', 912, 325),
    'rusijos-vakarai': City('rusijos-vakarai', 646, 222),
    'sakartvelas': City('sakartvelas', 833.5, 583.5),
    'skotija': City('skotija', 216.5, 300),
    'slovakija': City('slovakija', 466.5, 500),

    'suomija': City('suomija', 533.5, 250),
    'svedijos-siaure': City('svedijos-siaure', 476, 150),
    'svedijos-pietus': City('svedijos-pietus', 433.5, 300),
    'sveicarija': City('sveicarija', 300, 533.5),
    'ukrainos-rytai': City('ukrainos-rytai', 666.5, 500),
    'ukrainos-vakarai': City('ukrainos-vakarai', 589, 472),
    'vokietija': City('vokietija', 366.5, 433.5)
}


bridges = [
    'suomija,estija',
    'svedijos-pietus,karaliaucius',
    'norvegijos-siaure,islandija',
    'norvegijos-pietus,islandija',
    'norvegijos-pietus,skotija',
    'islandija,airija',
    'airija,anglija',
    'airija,skotija',
    'skotija,islandija',
    'anglija,prancuzijos-siaure',
    'anglija,prancuzijos-pietus',
    'anglija,beneliuksas',
    'svedijos-pietus,danija'
]


# pagalbiniai miestai, skirti tiksliau nurodyti troops'u kelia link tikrojo target_city
aux_cities = [
    City('italija,balkanu-siaure', 352, 555),
    City('italija,austrija', 352, 555),
    City('italija,prancuzijos-pietus', 336, 580),
    City('austrija,vokietija', 359, 508),
    City('rumunija,balkanu-siaure', 500, 532),
    City('lietuva,lenkija', 527, 397),
    City('lenkija,baltarusija', 535, 419),
    City('slovakija,balkanu-siaure', 470, 537),
    City('airija,skotija', 171, 298),
    City('portugalija,ispanijos-siaure', 52, 563),
    City('ispanijos-siaure,prancuzijos-pietus', 175, 593),
    City('prancuzijos-pietus,anglija', 170, 486),
    City('prancuzijos-siaure,vokietija', 307, 502),
    City('prancuzijos-siaure,italija', 286, 575),
    City('norvegijos-siaure,svedijos-pietus', 402, 161),
    City('norvegijos-siaure,svedijos-siaure', 468, 109),
    City('norvegijos-siaure,suomija', 546, 166),
    City('svedijos-siaure,suomija', 540, 138),
    City('norvegijos-siaure,rusijos-vakarai', 556, 80),
    City('rusijos-siaure,rusijos-centras', 765, 337),
    City('rusijos-vakarai,rusijos-centras', 691, 335),
    City('ukrainos-rytai,rusijos-pietus', 756, 490),
    City('rusijos-pietus,azerbaidzanas', 885, 546),
    City('rusijos-vakarai,estija', 604, 287),
    City('rusijos-vakarai,latvija', 614, 310),
    City('rusijos-vakarai,baltarusija', 582, 327),
    City('ukrainos-vakarai,lenkija', 528, 467),
    City('ukrainos-vakarai,slovakija', 530, 503),
    City('ukrainos-vakarai,rumunija', 551, 500),
    City('ukrainos-rytai,baltarusija', 642, 445),
]


# su kuo miestai turi sienas
borders = {
    'airija': 'islandija,skotija,anglija',
    'anglija': 'skotija,airija,beneliuksas,prancuzijos-pietus,prancuzijos-siaure',
    'armenija': 'sakartvelas,azerbaidzanas',
    'austrija': 'vokietija,cekija,slovakija,balkanu-siaure,italija,sveicarija',
    'azerbaidzanas': 'armenija,sakartvelas,rusijos-pietus',
    
    'balkanu-centras': 'balkanu-siaure,rumunija,bulgarija,balkanu-pietus',
    'balkanu-pietus': 'balkanu-centras,bulgarija',
    'balkanu-siaure': 'italija,austrija,slovakija,rumunija,balkanu-centras,ukrainos-vakarai',
    'baltarusija': 'lietuva,latvija,lenkija,ukrainos-vakarai,ukrainos-rytai,rusijos-centras,rusijos-vakarai',
    'beneliuksas': 'anglija,vokietija,prancuzijos-siaure',

    'bulgarija': 'balkanu-centras,rumunija,balkanu-pietus',
    'cekija': 'vokietija,lenkija,slovakija,austrija',
    'danija': 'vokietija,svedijos-pietus',
    'estija': 'latvija,rusijos-vakarai,suomija',
    'islandija': 'airija,skotija,norvegijos-pietus,norvegijos-siaure',
    
    'ispanijos-siaure': 'portugalija,prancuzijos-pietus,ispanijos-pietus',
    'ispanijos-pietus': 'portugalija,ispanijos-siaure',
    'italija': 'sveicarija,austrija,balkanu-siaure,prancuzijos-pietus,prancuzijos-siaure',
    'karaliaucius': 'lietuva,lenkija,svedijos-pietus',
    'latvija': 'estija,baltarusija,lietuva,rusijos-vakarai',
    'lenkija': 'karaliaucius,lietuva,baltarusija,slovakija,cekija,vokietija,ukrainos-vakarai',
    
    'lietuva': 'karaliaucius,latvija,baltarusija,lenkija',
    'moldova': 'rumunija,ukrainos-vakarai',
    'norvegijos-siaure': 'norvegijos-pietus,svedijos-pietus,svedijos-siaure,suomija,rusijos-vakarai,islandija',
    'norvegijos-pietus': 'skotija,svedijos-pietus,norvegijos-siaure,islandija',
    'portugalija': 'ispanijos-pietus,ispanijos-siaure',
    'prancuzijos-siaure': 'anglija,beneliuksas,vokietija,sveicarija,italija,prancuzijos-pietus',
    'prancuzijos-pietus': 'ispanijos-siaure,italija,prancuzijos-siaure,anglija',

    'rumunija': 'moldova,bulgarija,balkanu-centras,balkanu-siaure,ukrainos-vakarai',
    'rusijos-siaure': 'rusijos-vakarai,rusijos-rytai,rusijos-centras',
    'rusijos-centras': 'rusijos-siaure,rusijos-rytai,rusijos-pietus,rusijos-vakarai,ukrainos-rytai,baltarusija',
    'rusijos-pietus': 'rusijos-centras,azerbaidzanas,sakartvelas,ukrainos-rytai',
    'rusijos-rytai': 'rusijos-siaure,rusijos-centras',
    'rusijos-vakarai': 'rusijos-siaure,rusijos-centras,baltarusija,latvija,estija,suomija,norvegijos-siaure',
    'sakartvelas': 'azerbaidzanas,armenija,rusijos-pietus',
    'skotija': 'anglija,airija,islandija,norvegijos-pietus',
    'slovakija': 'cekija,lenkija,balkanu-siaure,austrija,ukrainos-vakarai',
    
    'suomija': 'svedijos-siaure,norvegijos-siaure,rusijos-vakarai,estija',
    'svedijos-siaure': 'norvegijos-siaure,suomija,svedijos-pietus',
    'svedijos-pietus': 'danija,norvegijos-pietus,norvegijos-siaure,svedijos-siaure,karaliaucius',
    'sveicarija': 'vokietija,austrija,italija,prancuzijos-siaure',
    'ukrainos-rytai': 'ukrainos-vakarai,baltarusija,rusijos-centras,rusijos-pietus',
    'ukrainos-vakarai': 'ukrainos-rytai,moldova,rumunija,balkanu-siaure,slovakija,lenkija,baltarusija',
    'vokietija': 'danija,lenkija,cekija,austrija,sveicarija,beneliuksas,prancuzijos-siaure',
}
