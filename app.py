from flask import Flask, jsonify, request
import pickle
import numpy as np
from sklearn.preprocessing import StandardScaler
import librosa
import logging
import tensorflow_hub as hub
import tensorflow as tf
import numpy as np

loc = "saved_models"
model = tf.keras.models.load_model(loc,
custom_objects={'KerasLayer':hub.KerasLayer})

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)


@app.route('/')
def root():
    return app.send_static_file('index.html')

@app.route('/getPredictions',methods = ['POST'])
def upload2():
    if(request.method == 'POST'):
        f = request.files['file']
        dur = int(request.form["dur"]) # Duration, to be sent 
        app.logger.info(f'dur : {request.form["dur"]}')
        audioFile =  f
        scaler = pickle.load(open("scaler.ok","rb"))
        ret_list = []
        for cust_dur in range(1,dur):
                audioFile.seek(0)
                x , sr = librosa.load(audioFile,mono=True,duration=cust_dur)
                y=x
                #Extract the features
                chroma_stft = librosa.feature.chroma_stft(y=y, sr=sr)
                spec_cent = librosa.feature.spectral_centroid(y=y, sr=sr)
                spec_bw = librosa.feature.spectral_bandwidth(y=y, sr=sr)
                rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
                zcr = librosa.feature.zero_crossing_rate(y)
                rmse = librosa.feature.rms(y=y)
                mfcc = librosa.feature.mfcc(y=y, sr=sr)
                tempogram = librosa.feature.tempogram(y=y, sr=sr)
                bpm = librosa.beat.tempo(y=y, sr=sr)
                feat_arrays =[chroma_stft, spec_cent, spec_bw, rolloff, zcr, rmse, tempogram,bpm ]
                #for stat in stats:
                to_append = ''
                k = ["_mean", "_median", "_sd", "_ptp", "_kurt", "_skew"]
                for i in feat_arrays:
                    to_append += f' {np.mean(i)} {np.median(i)} {np.std(i)} {np.ptp(i)}'  
                
                for i in mfcc:
                    to_append += f' {np.mean(i)} {np.median(i)} {np.std(i)} {np.ptp(i)}' 
                features = f'{np.mean(chroma_stft)} {np.mean(rmse)} {np.mean(spec_cent)} {np.mean(spec_bw)} {np.mean(rolloff)} {np.mean(zcr)}'    
                for e in mfcc:
                    features += f' {np.mean(e)}'
                input_data2 = np.array([float(i) for i in to_append.split(" ")]).reshape(1,-1)
                input_data2 = scaler.transform(input_data2)
                tf_model_predictions = model.predict(input_data2)
                genres = "Blues Classical Country Disco Hiphop Jazz Metal Pop Reggae Rock".split()
                high=0
                tf_model_predictions = tf_model_predictions[0]
                res = {}
                for i,e in enumerate(tf_model_predictions):
                        app.logger.info(f'E : {e}')
                        res[genres[i]] = str(e)
                        app.logger.info(f'{res}')
                ret_list.append(res)
        return jsonify(ret_list)
  


@app.route('/getFeatures',methods = ['POST'])
def upload():
    if(request.method == 'POST'):
        f = request.files['file']
        dur = int(request.form["dur"])
        app.logger.info(f'AUDIO FORMAT\n\n\n\n\n\n\n\n\n\n: {f}')
        audioFile =  f
        scaler = pickle.load(open("scaler.ok","rb"))
        x , sr = librosa.load(audioFile,mono=True,duration=dur)
        y=x
        #Extract the features
        chroma_stft = librosa.feature.chroma_stft(y=y, sr=sr)
        spec_cent = librosa.feature.spectral_centroid(y=y, sr=sr)
        spec_bw = librosa.feature.spectral_bandwidth(y=y, sr=sr)
        rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
        zcr = librosa.feature.zero_crossing_rate(y)
        rmse = librosa.feature.rms(y=y)
        mfcc = librosa.feature.mfcc(y=y, sr=sr)
        features = f'{np.mean(chroma_stft)} {np.mean(rmse)} {np.mean(spec_cent)} {np.mean(spec_bw)} {np.mean(rolloff)} {np.mean(zcr)}'    
        for e in mfcc:
            features += f' {np.mean(e)}'
        input_data2 = np.array([float(i) for i in features.split(" ")]).reshape(1,-1)
        input_data2 = scaler.transform(input_data2)
        return jsonify(input_data2.tolist())
  
# driver function 
if __name__ == '__main__':   
    app.run(debug = True, host='0.0.0.0') 
