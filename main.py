from fastapi import FastAPI
from pydantic import BaseModel
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import nltk
import uvicorn
import nltk
from fastapi.responses import FileResponse
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

# Ensure punkt and averaged_perceptron_tagger are downloaded
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')


class Item(BaseModel):
    sentence: str

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

# Define a root endpoint
@app.get("/")
def root():
    return {"message": "Sign Language API"}

@app.post("/a2sl")
def a2sl(Item: Item):
    text = Item.sentence
    text = text.lower()

    # Tokenize the input text into words
    words = word_tokenize(text)

    # Perform part-of-speech tagging on the words
    tagged = nltk.pos_tag(words)

    # Create a dictionary to store tense information
    tense = {}

    # Count the number of verbs in each tense
    tense["future"] = len([word for word in tagged if word[1] == "MD"])
    tense["present"] = len([word for word in tagged if word[1] in ["VBP", "VBZ", "VBG"]])
    tense["past"] = len([word for word in tagged if word[1] in ["VBD", "VBN"]])
    tense["present_continuous"] = len([word for word in tagged if word[1] in ["VBG"]])

    stop_words = set(["mightn't", 're', 'wasn', 'wouldn', 'be', 'has', 'that', 'does', 'shouldn',
                    'do', "you've",'off', 'for', "didn't", 'm', 'ain', 'haven', "weren't",
                    'are', "she's", "wasn't", 'its', "haven't", "wouldn't", 'don', 'weren', 's',
                    "you'd", "don't", 'doesn', "hadn't", 'is', 'was', "that'll", "should've", 'a',
                    'then', 'the', 'mustn', 'i', 'nor', 'as', "it's", "needn't", 'd', 'am', 'have',
                    'hasn', 'o', "aren't", "you'll", "couldn't", "you're", "mustn't", 'didn',
                    "doesn't", 'll', 'an', 'hadn', 'whom', 'y', "hasn't", 'itself', 'couldn',
                    'needn', "shan't", 'isn', 'been', 'such', 'shan', "shouldn't", 'aren', 'being',
                    'were', 'did', 'ma', 't', 'having', 'mightn', 've', "isn't", "won't"])

    lr = WordNetLemmatizer()
    filtered_text = []
    for w,p in zip(words,tagged):
        if w not in stop_words:
            if p[1]=='VBG' or p[1]=='VBD' or p[1]=='VBZ' or p[1]=='VBN' or p[1]=='NN':
                filtered_text.append(lr.lemmatize(w,pos='v'))
            elif p[1]=='JJ' or p[1]=='JJR' or p[1]=='JJS'or p[1]=='RBR' or p[1]=='RBS':
                filtered_text.append(lr.lemmatize(w,pos='a'))

            else:
                filtered_text.append(lr.lemmatize(w))

    words = filtered_text

    # Initialize a list to store modified words
    temp = []

    # Loop through the words and replace "I" with "Me"
    for w in words:
        if w == 'I':
            temp.append('Me')
        else:
            temp.append(w)

    # Update the 'words' variable with the modified words
    words = temp

    # Determine the probable tense based on the counts
    probable_tense = max(tense, key=tense.get)

    # Check the probable tense and make adjustments
    if probable_tense == "past" and tense["past"] >= 1:
        temp = ["Before"]
        temp = temp + words
        words = temp
    elif probable_tense == "future" and tense["future"] >= 1:
        if "Will" not in words:
            temp = ["Will"]
            temp = temp + words
            words = temp
        else:
            pass
    elif probable_tense == "present":
        if tense["present_continuous"] >= 1:
            temp = ["Now"]
            temp = temp + words
            words = temp

    # Convert all words to lowercase
    for i in range(len(words)):
        words[i] = words[i].lower()

    # List of animation videos for sign language
    videos=["0","1","2","3","4","5","6","7","8","9","a",
            "after","again","against","age","all","alone","also","and","ask","at",
            "b","be","beautiful","before","best","better","busy","but","bye",
            "c","can","cannot","change","college","come","computer",
            "d","day","distance","do not","does not",
            "e","eat","engineer","f","fight","finish","from","g","glitter","go",
            "god","gold","good","great","h","hand","hands","happy","hello","help",
            "her","here","his","home","homapage","how","i","invent","it","j","k","keep",
            "l","language","laugh","learn","m","me","more","my","n","name","next",
            "not","now","o","of","on","our","out","p","pretty","q","r","right","s","sad",
            "safe","see","self","sign","so","sound","stay","study","t","talk","television",
            "thank you","thank","that","they","this","those","time","to","type","u","us","v",
            "w","walk","wash","way","we","welcome","what","when","where","which","who","whole",
            "whose","why","will","with","without","words","work","world","wrong","x","y","you",
            "your","yourself","z"]

    # Initialize a list to store filtered and title-cased words
    filtered_text = []

    # Loop through words in the sentence
    for w in words:
        # If the word doesn't have an animation, split it into characters
        if w not in videos:
            for c in w:
                filtered_text.append(c)
        else:
            filtered_text.append(w)

    # Title-case all the words in the list
    for i in range(len(filtered_text)):
        filtered_text[i] = filtered_text[i].title()

    # Update the 'words' variable with the filtered and title-cased words
    words = filtered_text

    # Return the modified words
    return words

@app.get("/ui", response_class=HTMLResponse)
async def get_ui():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <title>Sign Language Translator</title>
    </head>
    <body>
      <h1>Sign Language Translator</h1>
      
      <input id="sentence" type="text" placeholder="Type a sentence...">
      <button id="translateBtn">Translate</button>
      
      <div id="output"></div>
      
      <script>
        document.getElementById("translateBtn").addEventListener("click", async function() {
          const sentence = document.getElementById("sentence").value;
          let response = await fetch("/a2sl", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ sentence })
          });
          let words = await response.json();

          let output = document.getElementById("output");
          output.innerHTML = "";

          let idx = 0;
          function playNext() {
            if (idx < words.length) {
              let w = words[idx].toLowerCase();
              let video = document.createElement("video");
              video.src = `/static/videos/${w}.mp4`;
              video.autoplay = true;
              video.controls = false;
              video.onended = () => {
                idx++;
                output.innerHTML = "";
                playNext();
              };
              output.appendChild(video);
            }
          }
          playNext();
        });
      </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    uvicorn.run(app)