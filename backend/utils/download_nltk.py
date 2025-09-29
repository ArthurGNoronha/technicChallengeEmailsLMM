import nltk
import os

def download_nltk_data():
    """Download necessary NLTK data packages"""
    nltk_data_dir = os.path.join(os.getcwd(), 'nltk_data')
    os.makedirs(nltk_data_dir, exist_ok=True)
    nltk.data.path.append(nltk_data_dir)
    
    try:
        nltk.download('punkt', download_dir=nltk_data_dir)
        nltk.download('stopwords', download_dir=nltk_data_dir)
        
        nltk.download('tokenizers/punkt', download_dir=nltk_data_dir)
        
        nltk.download('wordnet', download_dir=nltk_data_dir)
        nltk.download('averaged_perceptron_tagger', download_dir=nltk_data_dir)
        
        print("NLTK data downloaded successfully")
    except Exception as e:
        print(f"Error downloading NLTK data: {e}")

if __name__ == "__main__":
    print("Downloading NLTK packages...")
    download_nltk_data()
    print("Download completed.")