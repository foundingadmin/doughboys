# Key, genre from the mastered WAVs (Nov 8 2026). pip install essentia-tensorflow. Models from essentia.upf.edu into $TFB_AUDIO_WORK/models:
#   feature-extractors/discogs-effnet/discogs-effnet-bs64-1.pb, classification-heads/genre_discogs400/genre_discogs400-discogs-effnet-1.pb and .json
# Downloads each link shared master from Drive, analyzes, deletes. Writes analysis.json in $TFB_AUDIO_WORK.
import sys, json, os, subprocess, numpy as np
import essentia.standard as es
S = os.environ.get("TFB_AUDIO_WORK", "work/audio"); M = S + "/models"; os.makedirs(S + "/audio", exist_ok=True)
meta = json.load(open(M + "/genre_discogs400-discogs-effnet-1.json")); labels = meta["classes"]
emb = es.TensorflowPredictEffnetDiscogs(graphFilename=M + "/discogs-effnet-bs64-1.pb", output="PartitionedCall:1")
head = es.TensorflowPredict2D(graphFilename=M + "/genre_discogs400-discogs-effnet-1.pb", input="serving_default_model_Placeholder", output="PartitionedCall:0")
tracks = [("01","1WkT84PJ4ppNFhwkPKv8bf_pFZk9TUDjo"),("02","1pjTekOJDlS85CpUUuiBg3pESevTn2mSD"),("03","1O8UvVUcaI2V1UaoDHmV6qM6USlUns1mY"),("04","1YM71t790CiiTkrOPGm40iL4velWNEUR4"),("05","1ha9t6kL5kFOMdgtFGrJSppwgNxrVwpmv"),("06","1e4QbFWFBpCm6_Zn8AJ7ptfmIAg3sqAHv"),("07","1EfeEEQ_v16a7K5A1dcWtuKAd5RSPUxIN"),("08","1aNfyRSEhDGWE3Mp17rJZ6IbT9-ug7s9m"),("09","1vEtKMb9WcB6TiGiVeaQOgj3mg0uDLU29")]
out = {}
for n, fid in tracks:
    p = f"{S}/audio/{n}.wav"
    subprocess.run(["curl","-sS","-L","-o",p,f"https://drive.usercontent.google.com/download?id={fid}&export=download&confirm=t"], check=True)
    a44 = es.MonoLoader(filename=p, sampleRate=44100)()
    keys = {}
    for prof in ["bgate","edma","temperley","krumhansl"]:
        k, sc, st = es.KeyExtractor(profileType=prof)(a44); keys[prof] = [k, sc, round(float(st),3)]
    a16 = es.MonoLoader(filename=p, sampleRate=16000, resampleQuality=4)()
    pr = head(emb(a16)).mean(axis=0)
    top = [(labels[i], round(float(pr[i]),3)) for i in np.argsort(pr)[::-1][:10]]
    out[n] = {"keys": keys, "genres": top}
    os.remove(p)
    print(n, json.dumps(out[n]), flush=True)
json.dump(out, open(S + "/analysis.json","w"), indent=1)
