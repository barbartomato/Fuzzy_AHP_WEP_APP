from flask import Flask, render_template, jsonify, request
import json 
from flask_mysqldb import MySQL

app = Flask(__name__)

# Configure MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'hahaha123'
app.config['MYSQL_DB'] = 'fuzzy_ahp'

mysql = MySQL(app)

users = {
    "mayella": "123",
    "user2": "password2"
}

def find_property(array, search_string, index_pos):
    #! assuming that the array is the 2 dimension array [[],[]]
    for sub_array in array:
        if sub_array[1] == search_string:
            return sub_array[index_pos]

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/check_credential_user', methods=['POST'])
def check_credential_user():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    # Check if username exists and password is correct
    if username in users and users[username] == password:
        return jsonify({'success': 'horray! '})
    else:
        return jsonify({'failed': 'incorrect credentials'})
@app.route('/')
def index():
    return render_template('index.html')  # Removed leading slash for index.html

@app.route('/kriteria')
def kriteria():

    return render_template('kriteria.html', data=kriteria)  # Removed leading slash for index.html

@app.route('/process')
def process():
    return render_template('process.html')  # Removed leading slash for index.html

@app.route('/input_fuzzy/<preset>', methods=['POST'])
def process_fuzzy(preset):

    data = request.get_json()

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM kriteria WHERE preset = %s", (preset,))
    kriteria = cur.fetchall()
    cur.close()

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM subkriteria")
    subkriteria = cur.fetchall()
    cur.close()
    
    kriteria_bobot = {
        'permukaan_perkerasan': find_property(kriteria, 'permukaan_perkerasan',  index_pos=2),
        'retak_retak': find_property(kriteria, 'retak_retak',  index_pos=2),
        'kerusakan_lain': find_property(kriteria, 'kerusakan_lain',  index_pos=2),
        'infrastruktur_lain': find_property(kriteria, 'infrastruktur_lain',  index_pos=2),
        'anggaran': find_property(kriteria, 'anggaran',  index_pos=2),
        'volume_kendaraan': find_property(kriteria, 'volume_kendaraan', index_pos=2)
    }


    subkriteria_bobot = {
        'permukaan_perkerasan': {
            'susunan': find_property(subkriteria, 'susunan', index_pos=2),
            'kondisi_keadaan': find_property(subkriteria, 'kondisi_keadaan', index_pos=2),
            'penurunan': find_property(subkriteria, 'penurunan', index_pos=2),
            'tambalan': find_property(subkriteria, 'tambalan', index_pos=2)
        },
        'retak_retak': {
            'jenis': find_property(subkriteria, 'jenis', index_pos=2),
            'lebar': find_property(subkriteria, 'lebar', index_pos=2),
            'persen_luas': find_property(subkriteria, 'persen_luas', index_pos=2)
        },
        'kerusakan_lain': {
            'jumlah_lubang': find_property(subkriteria, 'jumlah_lubang', index_pos=2),
            'ukuran_lubang': find_property(subkriteria, 'ukuran_lubang', index_pos=2),
            'bekas_roda': find_property(subkriteria, 'bekas_roda',  index_pos=2),
            'kerusakan_tepi': find_property(subkriteria, 'kerusakan_tepi', index_pos=2)
        },
        'infrastruktur_lain': {
            'kondisi_bahu': find_property(subkriteria, 'kondisi_bahu', index_pos=2),
            'permukaan_bahu': find_property(subkriteria, 'permukaan_bahu', index_pos=2),
            'kondisi_saluran_samping': find_property(subkriteria, 'kondisi_saluran_samping', index_pos=2),
            'kerusakan_lereng': find_property(subkriteria, 'kerusakan_lereng', index_pos=2),
            'trotoar':  find_property(subkriteria, 'trotoar', index_pos=2)
        },
        'anggaran': {
            "anggaran": 1
        },
        'volume_kendaraan': {
            "volume_kendaraan": 1
        }
    }

    skor_fuzzy = []

    # * Find the length of the sample *
    length_sample = 0
    for kriteria in data:
        if len(data[kriteria]) > 0:
            length_sample = len(data[kriteria])
            break

    # * LOGIC FOR Calculating the norm of sub kriteria*
    normalize_sub_kriteria_list = {}
    # * calculate the sum of kriteria weight directly while calculating the subkriteria first *
    sum_of_weight_kriteria =  0
    for kriteria, list_of_sub in data.items():
        # *collect the sub kriteria property from data*
        if len(list_of_sub) > 0 :
            if kriteria == 'anggaran' or kriteria == 'volume_kendaraan':
                sum_of_weight_kriteria += kriteria_bobot[kriteria]
        if len(list_of_sub) > 0 and kriteria != 'anggaran' and kriteria != 'volume_kendaraan' :
            sum_of_weight_kriteria += kriteria_bobot[kriteria]
            unique_sub_kriteria_junk = list(list_of_sub[0].keys())
            unique_sub_kriteria_fix_prefix = [unique_sub_kriteria_junk.rsplit('_', 1)[0] for unique_sub_kriteria_junk in unique_sub_kriteria_junk]
            # ** calculating the total of weight from subkriteria ** 
            sum_of_weight_subkriteria = 0
            for sub_kriteria_name in unique_sub_kriteria_fix_prefix:
                sum_of_weight_subkriteria += subkriteria_bobot[kriteria][sub_kriteria_name]
            # * calculaate single norm of subkritria *
            for sub_kriteria_name in unique_sub_kriteria_fix_prefix:
                if kriteria not in normalize_sub_kriteria_list:
                    normalize_sub_kriteria_list[kriteria] = {}
                    normalize_sub_kriteria_list[kriteria][sub_kriteria_name] = (subkriteria_bobot[kriteria][sub_kriteria_name] / sum_of_weight_subkriteria) 
                else:
                    normalize_sub_kriteria_list[kriteria][sub_kriteria_name] = (subkriteria_bobot[kriteria][sub_kriteria_name] / sum_of_weight_subkriteria)

    # * CALCULATING THE NORMALIZE OF KRITERIA *
    normalize_kriteria_list = {}
    for kriteria, list_of_sub in data.items():
        if len(list_of_sub) > 0 :
            normalize_kriteria_list[kriteria] = (kriteria_bobot[kriteria] / sum_of_weight_kriteria)
        else:
            normalize_kriteria_list[kriteria] = 0

    # special case. anggaran and volume kendaraan dont have subkriteria ** 
    if 'anggaran' in data:
        normalize_sub_kriteria_list["anggaran"] = {"anggaran" : normalize_kriteria_list["anggaran"]}
    
    if 'volume_kendaraan' in data:
        normalize_sub_kriteria_list["volume_kendaraan"] = {"volume_kendaraan" : normalize_kriteria_list["volume_kendaraan"]}

    # Hitung skor fuzzy berdasarkan input pengguna
    for idx in range(0, length_sample):
        temp_fuzzy = 0
        for kriteria, bobot in normalize_kriteria_list.items():
            if kriteria in normalize_sub_kriteria_list:
                for subkriteria, subbobot in normalize_sub_kriteria_list[kriteria].items():
                    property_client_name = subkriteria.lower() + "_" + str(idx)
                    if(len(data[kriteria]) != 0) :
                        if(property_client_name in data[kriteria][idx]) :
                            temp_fuzzy += bobot * subbobot * float(data[kriteria][idx][property_client_name])
        skor_fuzzy.append(temp_fuzzy)

    # Return a JSON response
    return jsonify(skor_fuzzy)


@app.route('/insert_result', methods=['POST'])
def insert_result_fuzzy():

    post_data = request.get_json()
    
    data = json.dumps(post_data['data'])
    result = json.dumps(post_data['result'])
    street_name = json.dumps(post_data['street_list'])

    insert_data_query = '''
    INSERT INTO fuzzy_result (data, result, nama_jalan) VALUES (%s, %s, %s);
    '''
    
    cur = mysql.connection.cursor()
    cur.execute(insert_data_query, (data, result, street_name))
    mysql.connection.commit()
    cur.close()
    
    return jsonify({'message': 'Data inserted successfully'})

@app.route('/result_history', methods=['GET'])
def result_history():

    cur = mysql.connection.cursor()

    cur.execute("SELECT * FROM fuzzy_result")
    fuzzy = cur.fetchall()
    cur.close()

    temp_data = []
    for item in fuzzy:
        id = item[0]
        data = item[1]
        date = item[2]
        result_list = item[3]
        street_list = item[4]

        data_json = json.loads(data)
        result_json = json.loads(result_list)
        street_json = street_list

        final_object = {
            'id': id,
            'date': date,
            'data': data_json,
            'result': result_json,
            'street_list': street_json.replace('[', '').replace(']', '').replace('"', '')
        }

        temp_data.append(final_object)

    return render_template('riwayat.html', data=temp_data) 


@app.route('/result_history/<int:item_id>', methods=['GET'])
def result_history_detail(item_id):

    cur = mysql.connection.cursor()

    cur.execute("SELECT * FROM fuzzy_result WHERE id = %s", (item_id,))
    fuzzy = cur.fetchall()
    cur.close()

    temp_data = []

    item = fuzzy[0]
    id = item[0]
    data = item[1]
    date = item[2]
    result_list = item[3]
    street_list = item[4]

    data_json = json.loads(data)
    result_json = json.loads(result_list)
    street_json = street_list

    final_object = {
        'id': id,
        'date': date,
        'data': data_json,
        'result': result_json,
        'street_list': street_json.replace('[', '').replace(']', '').replace('"', '')
    }

    temp_data.append(final_object)

    return jsonify(temp_data)


if __name__ == '__main__':
    app.run(debug=True)