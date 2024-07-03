from flask import Flask, render_template, jsonify, request
import json 

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')  # Removed leading slash for index.html

@app.route('/kriteria')
def kriteria():
    return render_template('kriteria.html')  # Removed leading slash for index.html

@app.route('/process')
def process():
    return render_template('process.html')  # Removed leading slash for index.html



@app.route('/input_fuzzy', methods=['POST'])
def process_fuzzy():
    data = request.get_json()
    kriteria_bobot = {
        'permukaan_perkerasan': 0.247876,
        'retak_retak': 0.000000,
        'kerusakan_lain': 0.214617,
        'insfrastruktur_lain': 0.055374,
        # 'Anggaran': 0.265473,
        # 'VolumeKendaraan': 0.216660
    }
    subkriteria_bobot = {
        'permukaan_perkerasan': {
            'susunan': 0.106655,
            'kondisi_keadaan': 0.403255,
            'penurunan': 0.490090,
            'tambalan': 0.000000
        },
        'retak_retak': {
            'jenis': 0.44437,
            'lebar': 0.10914,
            'persen_luas': 0.44649
        },
        'kerusakan_lain': {
            'jumlah_lubang': 0.683145,
            'ukuran_lubang': 0.316855,
            'bekas_roda': 0.000000,
            'kerusakan_tepi': 0.000000
        },
        'insfrastruktur_lain': {
            'kondisi_bahu': 0.548948,
            'permukaan_bahu': 0.451052,
            'kondisi_saluran_samping': 0.000000,
            'kerusakan_lereng': 0.000000,
            'trotoar': 0.000000
        }
    }


    skor_fuzzy = []


    # * Find the length of the sample *
    length_sample = 0
    for kriteria in data:
        if len(data[kriteria]) > 0:
            length_sample = len(data[kriteria])
            break

    # Hitung skor fuzzy berdasarkan input pengguna
    for idx in range(0, length_sample):
        temp_fuzzy = 0
        for kriteria, bobot in kriteria_bobot.items():
            if kriteria in subkriteria_bobot:
                for subkriteria, subbobot in subkriteria_bobot[kriteria].items():
                    property_client_name = subkriteria.lower() + "_" + str(idx)
                    if(len(data[kriteria]) != 0) :
                        if(property_client_name in data[kriteria][idx]) :
                            temp_fuzzy += bobot * subbobot * float(data[kriteria][idx][property_client_name])
        skor_fuzzy.append(temp_fuzzy)
    # Add logic to process the fuzzy data here

    # Return a JSON response
    return jsonify(skor_fuzzy)

if __name__ == '__main__':
    app.run(debug=True)