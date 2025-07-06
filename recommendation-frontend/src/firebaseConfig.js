// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";
import { getFirestore } from "firebase/firestore";
import { getStorage } from "firebase/storage";

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyDpweV6QJfTzdvx6w1CvGk_sxH6e5_jn3Y",
  authDomain: "ai-movie-recommendation-engine.firebaseapp.com",
  projectId: "ai-movie-recommendation-engine",
  storageBucket: "ai-movie-recommendation-engine.firebasestorage.app",
  messagingSenderId: "417192158866",
  appId: "1:417192158866:web:b84a63f27072b8d1b5a84b"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Firebase services
export const auth = getAuth(app);
export const db = getFirestore(app);
export const storage = getStorage(app);
export default app;
