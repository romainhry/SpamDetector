from Carbon.Windows import false
from django.template import loader
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.template import RequestContext
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from .forms import DocumentForm
from normalize import Normalizer
from kmeans import KMeanClusterer
import os

global norm, kMeanClusterer, nomChamp, champs, name_champ

# Create your views here.
def index(request):
    # Handle file upload
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['docfile'], request.FILES['docfile'].name)
            # Redirect to the document list after POST
            norm = Normalizer()
            data_save = []
            workpath = os.path.dirname(os.path.abspath(__file__)) #Returns the Path your .py file is in
            data = norm.load_csv(os.path.join(workpath, 'dataset/'+request.FILES['docfile'].name))

            for line in data:
                try:
                    data_save.append(line)
                except IndexError:
                    pass

            '''
            data_normalized = norm.normalization(data_save, 0.0, 1.0, 58)
            stats = norm.statistics(data_normalized, 58)
            '''
            normalizedData = norm.normalization()
            normSplitedData = norm.split(normalizedData)
            normNospams = normSplitedData[1]
            normSpams = normSplitedData[0]
            stats = norm.stats(normSpams, normNospams)

            spam = []
            for i in range(0, 58):
                line = []
                line.append(i)
                for j in range(0, 4):
                    line.append(stats[0][j][i])
                spam.append(line)

            no_spam = []
            for i in range(0, 58):
                line = []
                line.append(i)
                for j in range(0, 4):
                    line.append(stats[1][j][i])
                no_spam.append(line)

            new_stats = []
            for i in range(0, 58):
                line = []
                line.append(i)
                for j in range(0, 4):
                    line.append(stats[0][j][i])
                for j in range(0, 4):
                    line.append(stats[1][j][i])
                new_stats.append(line)

            global nomChamp
            nomChamp = ['word_freq_make', 'word_freq_address', 'word_freq_all',
                        'word_freq_3d', 'word_freq_our', 'word_freq_over', 'word_freq_remove',
                        'word_freq_internet', 'word_freq_order', 'word_freq_mail',
                        'word_freq_receive', 'word_freq_will', 'word_freq_people',
                        'word_freq_report', 'word_freq_addresses', 'word_freq_free',
                        'word_freq_business', 'word_freq_email', 'word_freq_you',
                        'word_freq_credit', 'word_freq_your', 'word_freq_font',
                        'word_freq_000', 'word_freq_money', 'word_freq_hp', 'word_freq_hpl',
                        'word_freq_george', 'word_freq_650', 'word_freq_lab',
                        'word_freq_labs', 'word_freq_telnet', 'word_freq_857',
                        'word_freq_data', 'word_freq_415', 'word_freq_85',
                        'word_freq_technology', 'word_freq_1999', 'word_freq_parts',
                        'word_freq_pm', 'word_freq_direct', 'word_freq_cs',
                        'word_freq_meeting', 'word_freq_original', 'word_freq_project',
                        'word_freq_re', 'word_freq_edu', 'word_freq_table',
                        'word_freq_conference', 'char_freq_semi', 'char_freq_lparen',
                        'char_freq_lbrack', 'char_freq_bang', 'char_freq_dollar',
                        'char_freq_hash', 'capital_run_length_average',
                        'capital_run_length_longest', 'capital_run_length_total',
                        'spam']

            stats_names = []
            stats_names = zip(nomChamp, new_stats)
            return render(request, 'stats.html', {'data': stats_names})
    else:
        form = DocumentForm() # A empty, unbound form
        return render(request, 'index.html', {'form': form})


def kmeans(request):
    k = 2
    global norm, champs, name_champ
    norm = Normalizer()
    workpath = os.path.dirname(os.path.abspath(__file__)) #Returns the Path your .py file is in
    datafile = os.path.join(workpath, 'dataset/spambase.data.txt')
    norm.load_csv(os.path.join(workpath, 'dataset/spambase.data.txt'))
    champs = []
    name_champ = []
    if request.method == 'GET':
        if(request.GET['nb'] == '3'):
            champs.append(int(request.GET['champs1']))
            champs.append(int(request.GET['champs2']))
            champs.append(int(request.GET['champs3']))
            name_champ.append(nomChamp[champs[0]])
            name_champ.append(nomChamp[champs[1]])
            name_champ.append(nomChamp[champs[2]])
        elif (request.GET['nb'] == '2'):
            champs.append(int(request.GET['champs1']))
            champs.append(int(request.GET['champs2']))
            name_champ.append(nomChamp[champs[0]])
            name_champ.append(nomChamp[champs[1]])

        global kMeanClusterer
        kMeanClusterer = KMeanClusterer(k, datafile, champs)
        kMeanClusterer.assignement()
        centroids = []
        clusters = []
        for i in range(k):
            centroids.append(kMeanClusterer.getCluster(i).getCentroid())
            #centroids.append(kMeanClusterer.getCluster(i).normalizeCentroid(0.0, 1.0, len(champs)))
        for i in range(k):
            clusters.append(kMeanClusterer.getCluster(i).getPoints())
            #clusters.append(norm.normalization(kMeanClusterer.getCluster(i).getPoints(), 0.0, 1.0, len(champs)))


        splitedData = norm.get_splitedData(champs)
        spams = splitedData[0]
        nospams = splitedData[1]

        html = render_to_string('kmeans.html', {'k': len(champs), 'centroids': centroids, 'clusters': clusters,
                                                'spams': spams, 'no_spams': nospams, 'nomChamps': name_champ})
        return HttpResponse(html)
    else:
        form = DocumentForm() # A empty, unbound form
        return redirect('index.html', {'form': form})

def extraction(request):
    k = 2
    workpath = os.path.dirname(os.path.abspath(__file__)) #Returns the Path your .py file is in
    datafile = os.path.join(workpath, 'dataset/spambase.data.txt')
    norm.load_csv(os.path.join(workpath, 'dataset/spambase.data.txt'))
    N = 0
    if request.method == 'GET':
        if (int(request.GET['N']) >= 0 or int(request.GET['N'] <=100)):
            N = int(request.GET['N'])
        kMeanClusterer.extraction_n(N)
        centroids = []
        clusters = []
        for i in range(k):
            centroids.append(kMeanClusterer.getCluster(i).getCentroid())
            #centroids.append(kMeanClusterer.getCluster(i).normalizeCentroid(0.0, 1.0, len(champs)))
        for i in range(k):
            clusters.append(kMeanClusterer.getCluster(i).getPoints())
            #clusters.append(norm.normalization(kMeanClusterer.getCluster(i).getPoints(), 0.0, 1.0, len(champs)))


        splitedData = norm.get_splitedData(champs)
        spams = splitedData[0]
        nospams = splitedData[1]
        spams_extracted = []
        nospams_extracted = []
        for s in spams:
            if s in clusters[0] or s in clusters[1]:
                spams_extracted.append(s)

        for n in nospams:
            if n in clusters[0] or n in clusters[1]:
                nospams_extracted.append(n)


        html = render_to_string('kmeans.html', {'k': len(champs), 'centroids': centroids, 'clusters': clusters,
                                                'spams': spams_extracted, 'no_spams': nospams_extracted, 'nomChamps': name_champ})
        return HttpResponse(html)
    else:
        form = DocumentForm() # A empty, unbound form
        return redirect('index.html', {'form': form})

def reinit(request):
    k = 2
    workpath = os.path.dirname(os.path.abspath(__file__)) #Returns the Path your .py file is in
    datafile = os.path.join(workpath, 'dataset/spambase.data.txt')
    norm.load_csv(os.path.join(workpath, 'dataset/spambase.data.txt'))
    N = 0
    if request.method == 'GET':
        kMeanClusterer = KMeanClusterer(k, datafile, champs)
        kMeanClusterer.assignement()
        centroids = []
        clusters = []
        for i in range(k):
            centroids.append(kMeanClusterer.getCluster(i).getCentroid())
            #centroids.append(kMeanClusterer.getCluster(i).normalizeCentroid(0.0, 1.0, len(champs)))
        for i in range(k):
            clusters.append(kMeanClusterer.getCluster(i).getPoints())
            #clusters.append(norm.normalization(kMeanClusterer.getCluster(i).getPoints(), 0.0, 1.0, len(champs)))


        splitedData = norm.get_splitedData(champs)
        spams = splitedData[0]
        nospams = splitedData[1]


        html = render_to_string('kmeans.html', {'k': len(champs), 'centroids': centroids, 'clusters': clusters,
                                                'spams': spams, 'no_spams': nospams, 'nomChamps': name_champ})
        return HttpResponse(html)
    else:
        form = DocumentForm() # A empty, unbound form
        return redirect('index.html', {'form': form})


def handle_uploaded_file(f, file_name):
    workpath = os.path.dirname(os.path.abspath(__file__)) #Returns the Path your .py file is in
    destination = open(os.path.join(workpath, 'dataset/'+file_name), 'wb+')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()