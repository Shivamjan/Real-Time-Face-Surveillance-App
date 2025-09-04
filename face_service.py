import cv2
import numpy as np
from mtcnn import MTCNN
from deepface import DeepFace
import faiss

class FaceService:
    """
    Encapsulates all face detection, embedding, and recognition logic.
    """
    def __init__(self, db_service):
        self.db_service = db_service
        self.detector = MTCNN()
        self.embedding_dimension = 512  # ArcFace model dimension
        self.faiss_index = faiss.IndexFlatIP(self.embedding_dimension)
        self.known_embeddings = []
        self.known_labels = []
        self.recognition_threshold = 0.65 

        self.load_embeddings_from_db()

    def load_embeddings_from_db(self):
        """Loads all criminal embeddings from the database and populates the FAISS index."""
        self.known_embeddings.clear()
        self.known_labels.clear()
        self.faiss_index.reset()
        
        try:
            connection = self.db_service.get_connection()
            with connection.cursor() as cursor:
                cursor.execute("SELECT name, embedding FROM criminals WHERE embedding IS NOT NULL")
                results = cursor.fetchall()
                for row in results:
                    if row['embedding']:
                        embedding = np.frombuffer(row['embedding'], dtype=np.float32)
                        norm = np.linalg.norm(embedding)
                        if norm > 0:
                            normalized_embedding = embedding / norm
                            self.known_embeddings.append(normalized_embedding)
                            self.known_labels.append(row['name'])
            connection.close()
            
            if self.known_embeddings:
                embeddings_np = np.array(self.known_embeddings, dtype=np.float32)
                self.faiss_index.add(embeddings_np)
                print(f"Loaded {self.faiss_index.ntotal} embeddings into FAISS.")
        except Exception as e:
            print(f"Error loading embeddings: {e}")

    def extract_face(self, image_np, confidence_threshold=0.90):
        faces = self.detector.detect_faces(image_np)
        if not faces:
            return None, "No face detected."

        # filter faces by confidence and find the one with the largest bounding box
        confident_faces = [f for f in faces if f['confidence'] >= confidence_threshold]
        if not confident_faces:
            return None, "Face detection confidence too low."
            
        main_face = max(confident_faces, key=lambda f: f['box'][2] * f['box'][3])
        x, y, w, h = main_face['box']
        
        x, y = max(0, x), max(0, y)
        face_img = image_np[y:y+h, x:x+w]
        
        return face_img, None

    def get_embedding(self, face_image_np):
        """
        Generates a face embedding from a cropped face image.
        Handles the specific return format from DeepFace.
        """
        try:
            # DeepFace.represent returns a list of dictionaries
            embedding_result = DeepFace.represent(
                face_image_np,
                model_name="ArcFace",
                enforce_detection=False
            )
            
            if isinstance(embedding_result, list) and len(embedding_result) > 0:
                embedding_vector = embedding_result[0].get("embedding")
                if embedding_vector:
                    embedding_np = np.array(embedding_vector, dtype=np.float32)
                    # Normalize the embedding before searching
                    norm = np.linalg.norm(embedding_np)
                    if norm > 0:
                        return embedding_np / norm, None
            
            return None, "Could not extract embedding from face."
        except Exception as e:
            return None, f"Embedding extraction failed: {str(e)}"

    def search_face(self, embedding):
        """
        Searches for a similar face in the FAISS index using Cosine Similarity.
        Returns the name of the matched criminal and the similarity score.
        """
        if self.faiss_index.ntotal == 0:
            return "Unknown", 0.0
        
        embedding_np = np.array([embedding], dtype=np.float32)
        
        similarities, indices = self.faiss_index.search(embedding_np, k=1)
        
        similarity_score = similarities[0][0]
        matched_label = self.known_labels[indices[0][0]]
        
        #print(f"DEBUG: Closest match is '{matched_label}' with similarity {similarity_score:.4f}")

        if similarity_score >= self.recognition_threshold:
            return matched_label, similarity_score
            
        return "Unknown", similarity_score

